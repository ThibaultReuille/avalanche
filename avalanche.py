#!/usr/bin/env python

import sys
import json
import pprint as pp
import zmq
import time
import threading
import md5
import os.path
import imp
import traceback

from abc import ABCMeta, abstractmethod

import plugins.base

context = dict()

# ----- Nodes -----

class Node(object):
	def __init__(self, info):
		global context

		self.info = info
		self.url = None
		self.connectors = [ 'sub', 'pub' ] # Default connectors are subscribers/publishers

		self.predecessors = list()

		self.thread = None
		if 'type' in self.info and self.info['type'] == 'rack':
			self.plugin = plugins.base.PluginRack()
			for p in self.info['plugins']:
				rack_plugin_type = p['type']
				print("\t+ {0}".format(rack_plugin_type))
				rack_plugin = context['plugins'][rack_plugin_type](p)
				self.plugin.plugins.append(rack_plugin)
		elif 'type' in self.info and self.info['type'] != 'virtual':
			self.plugin = context['plugins'][self.info['type']](info)
		else:
			self.plugin = None

class ZMQ_Node(Node):
	def __init__(self, info):
		global context
		super(ZMQ_Node, self).__init__(info)

		if 'url' in self.info:
			self.port = None
			self.url = self.info['url']
		else:
			if 'port' in self.info:
				self.port = self.info['port']
			else:
				self.port = context['ports']['next']
				if self.port > context['ports']['stop']:
					print("[WARNING]\tDefined port range is too small for pipeline! Collision may happen.")
				context['ports']['next'] += 1
				print("\tAutomatic port: {0}".format(self.port))			
			self.url = "tcp://localhost:{0}".format(self.port)

		if 'connectors' in self.info:
			self.connectors = self.info['connectors']

	def initialize(self):
		ctx = zmq.Context.instance()

		# Input Connector
		if self.connectors[0] is None:
			self.input = None
		elif self.connectors[0] == "sub":
			self.input = ctx.socket(zmq.SUB)
			#self.input.set_hwm(10)
		elif self.connectors[0] == "pull":
			self.input = ctx.socket(zmq.PULL)
			self.input.setsockopt(zmq.CONFLATE, 1)
		else:
			print("[ERROR] '{0}': Unknown connector type!".format(self.connectors[0]))

		# Output Connector
		if self.connectors[1] is None:
			self.output = None
		elif self.connectors[1] == "pub":
			self.output = ctx.socket(zmq.PUB)
			#self.output.set_hwm(10)
		elif self.connectors[1] == "push":
			self.output = ctx.socket(zmq.PUSH)
		else:
			print("[ERROR] '{0}': Unknown connector type!".format(self.connectors[1]))

		''' DEBUG INFO
		if self.input is not None:
			print(self.input.get_hwm())
		if self.output is not None:
			print(self.output.get_hwm())
		'''
		
		if self.port is not None:
			self.url = "tcp://localhost:{0}".format(self.port)

			if self.output is not None:
				self.output.bind("tcp://*:{0}".format(self.port))
				print("\tBinding {0} ...".format(self.url))

		for pred in self.predecessors:
			src_url = pred['url']
			print("\tConnecting to {0} ...".format(src_url))
			
			self.input.connect(src_url)

			if self.connectors[0] == "sub":
				self.input.setsockopt(zmq.SUBSCRIBE, '')
		
	def run(self):
		self.initialize()
		if self.plugin is not None:
			self.plugin.run(self)
	
# ----- Edges -----

class Edge(object):
	def __init__(self, info):
		pass
	def run(self):
		pass

class ZMQ_Edge(Edge):
	def __init__(self, info):
		super(ZMQ_Edge, self).__init__(info)

		global context
		self.info = info
		self.src = context['graph'].nodes[info['src']]
		self.dst = context['graph'].nodes[info['dst']]
		
		print("\t. Connecting {0} and {1} ...".format(self.src.info['id'], self.dst.info['id']))
		self.dst.predecessors.append({ "url" : self.src.url })

	def run(self):
		pass

class Graph(object):

	def __init__(self):
		self.nodes = dict()
		self.edges = dict()
		self.threads = list()

	def create_node(self, info):
		if 'id' not in info or 'type' not in info:
			return None
		uid = info['id']
		self.nodes[uid] = ZMQ_Node(info)

	def create_edge(self, info):
		if 'id' not in info:
			return None
		uid = info['id']
		self.edges[uid] = ZMQ_Edge(info)

	def start(self):
		for k in self.nodes.keys():
			if self.nodes[k].plugin is None:
				continue
			repr(self.nodes[k])
			self.nodes[k].thread = threading.Thread(target=self.nodes[k].run)
			self.nodes[k].thread.start()
			self.threads.append(self.nodes[k].thread)

	def wait(self):
		for thread in self.threads:
			thread.join()

# ----- Main -----

def load_module(code_path):
    try:
        try:
            code_dir = os.path.dirname(code_path)
            code_file = os.path.basename(code_path)
            fin = open(code_path, 'rb')
            return  imp.load_source(md5.new(code_path).hexdigest(), code_path, fin)
        finally:
            try: fin.close()
            except: pass
    except ImportError, x:
        traceback.print_exc(file = sys.stderr)
        raise
    except:
        traceback.print_exc(file = sys.stderr)
        raise

def main(conf):

	global context

	# ----- Load plugins -----

	context['plugins'] = dict()

	if "attributes" in conf:
		if "plugins" in conf['attributes']:
			for plugin in conf['attributes']['plugins']:
				name = plugin['name']
				filename = plugin['filename']

				plugin_module = load_module(filename)
				plugin_class = getattr(plugin_module, 'Plugin')
				context['plugins'][name] = plugin_class

				print("[PLUGIN] {0}: {1}".format(name, filename))

	# ----- Load graph -----

	context['graph'] = Graph()

	for item in conf['nodes']:
		print("[NODE] {0}: {1}".format(item['id'], item['type']))
		context['graph'].create_node(item)

	edges = dict()
	for item in conf['edges']:
		print("[EDGE] {0}: {1} -> {2}".format(item['id'], item['src'], item['dst']))
		context['graph'].create_edge(item)

	print("[INFO] Launching node threads ...")
	context['graph'].start()
	print("[INFO] Running.")
	context['graph'].wait()

	while True:
		print("Main idle.")
		time.sleep(1)

if __name__ == "__main__":

	if len(sys.argv) != 3:
		print("Usage: {0} <conf.json> <port-range>".format(sys.argv[0]))
		sys.exit(0)

	ports = [ int(p) for p in sys.argv[2].split('-') ]
	if len(ports) == 1:
		ports.append(65535)

	context['ports'] = {
		'start' : ports[0],
		'stop' : ports[1],
		'next' : ports[0]
	}

	with open(sys.argv[1], "rU") as conf:
		jconf = json.load(conf)
		main(jconf)