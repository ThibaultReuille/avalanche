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
import string
import random

from abc import ABCMeta, abstractmethod

import plugins.base

context = dict()

# ----- Nodes -----

class Node(object):
	def __init__(self, info):
		global context

		self.info = info

		# NOTE: Default connectors are sub/pub
		if "connectors" not in self.info:
			self.info['connectors'] = [ "sub", "pub" ]

		self.connectors = list()
		for connector in self. info['connectors']:
			if isinstance(connector, dict):
				self.connectors.append(connector)
			else:
				self.connectors.append({ 'type' : connector })

		self.predecessors = list()
		self.successors = list()

		self.thread = None
		if 'type' in self.info and self.info['type'] == 'rack':
			self.plugin = plugins.base.PluginRack()
			print("    . plugins")
			for p in self.info['plugins']:
				rack_plugin_type = p['type']
				print("        + {0}".format(rack_plugin_type))
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

		binders = [ 'pull', 'pub', 'router' ]

		for connector in self.connectors:
			if connector['type'] is None:
				continue
			if connector['type'] in binders:
				if 'url' in connector:
					print("    . {0}: {1}".format(connector['type'], connector['url']))
				elif 'port' not in connector:
					if context['ports']['next'] > context['ports']['stop']:
						print("[WARNING] Defined port range is too small for pipeline! Collision may happen.")
					connector['port'] = context['ports']['next']
					context['ports']['next'] += 1
					print("    . {0}: {1}".format(connector['type'], connector['port']))
			else:
				print("    . {0}".format(connector['type']))

		#print("    Connectors: {0}".format(self.connectors))

	def initialize(self):

		if self.info['type'] == "virtual":
			return

		context = zmq.Context.instance()

		# ------ Input -----

		input_connector = self.connectors[0]

		if input_connector['type'] is None:
			self.input = None

		elif input_connector['type'] == "sub":
			self.input = context.socket(zmq.SUB)
			for predecessor in self.predecessors:
				if 'url' in predecessor.connectors[1]:
					src_url = predecessor.connectors[1]['url']
				else:
					src_url = "tcp://localhost:{0}".format(predecessor.connectors[1]['port'])

				print("    Connecting sub to {0} ...".format(src_url))
				self.input.connect(src_url)
				self.input.setsockopt(zmq.SUBSCRIBE, '')

		elif input_connector['type'] == "pull":
			self.input = context.socket(zmq.PULL)
			url = "tcp://*:{0}".format(input_connector['port'])
			print("    Binding pull on {0} ...".format(url))
			self.input.bind(url)

		elif input_connector['type'] == "dealer":
			self.input = context.socket(zmq.DEALER)
			self.identity = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
			self.input.setsockopt(zmq.IDENTITY, self.identity)
			for predecessor in self.predecessors:
				if 'url' in predecessor.connectors[1]:
					src_url = predecessor.connectors[1]['url']
				else:
					src_url = "tcp://localhost:{0}".format(predecessor.connectors[1]['port'])

				print("    Connecting dealer to {0} ...".format(src_url))
				self.input.connect(src_url)

		else:
			print("[ERROR] '{0}': Unsupported input connector type!".format(self.connectors[0]))

		# ----- Output -----

		output_connector = self.connectors[1]

		if output_connector['type'] is None:
			self.output = None

		elif output_connector['type'] == "pub":
			self.output = context.socket(zmq.PUB)
			url = "tcp://*:{0}".format(output_connector['port'])
			print("    Binding pub on {0} ...".format(url))
			self.output.bind(url)

		elif output_connector['type'] == "push":
			self.output = context.socket(zmq.PUSH)
			for successor in self.successors:
				if 'url' in successor.connectors[0]:
					dst_url = successor.connectors[0]['url']
				else:
					dst_url = "tcp://localhost:{0}".format(successor.connectors[0]['port'])

				print("    Connecting push to {0} ...".format(dst_url))
				self.output.connect(dst_url)

		elif output_connector['type'] == "router":
			self.output = context.socket(zmq.ROUTER)
			url = "tcp://*:{0}".format(output_connector['port'])
			print("    Binding router on {0} ...".format(url))
			self.output.bind(url)

		else:
			print("[ERROR] '{0}': Unsupported output connector type!".format(self.connectors[1]))

 	def run(self):
		self.initialize()
		# TODO : We should have plugins wait here for all to be ready
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
		self.dst.predecessors.append(self.src)
		self.src.successors.append(self.dst)

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