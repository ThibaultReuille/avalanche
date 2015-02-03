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


context = dict()

# ----- Plugins -----

class Plugin(object):
	def __init__(self):
		self.tracing = True

	def run(self, node):
		while True:
			data = node.input.recv()
			if self.tracing:
				message = json.loads(data)
				node.trace(message)
				node.output.send_json(message)
			else:
				node.output.send(data)

# ----- Nodes -----

class Node(object):
	def __init__(self, info):
		super(Node, self).__init__()
		
		global context

		self.info = info
		self.url = None
		self.thread = None

		if 'plugin' not in self.info['attributes']:
			self.plugin = Plugin()
		else:

			self.plugin = context['plugins'][self.info['attributes']['plugin']](info)
		
class ZMQ_Stream(Node):
	def __init__(self, info):
		super(ZMQ_Stream, self).__init__(info)
		
		if 'url' in self.info['attributes']:
			self.url = self.info['attributes']['url']
			print("\t. URL: {0}".format(self.url))
		else:
			print("\t. Error: Missing URL!")

	def run(self):
		pass

class ZMQ_Node(Node):
	def __init__(self, info):
		super(ZMQ_Node, self).__init__(info)
		global context

		ctx = zmq.Context.instance()

		self.input = ctx.socket(zmq.SUB)
		self.output = ctx.socket(zmq.PUB)

		port = self.info['attributes']['port']
		self.url = "tcp://localhost:{0}/".format(port)
		self.output.bind("tcp://*:{0}/".format(port))
		print("\t. Started on {0}.".format(self.url))

	def trace(self, message):
		if self.tracing:
			if '#' not in message:
				message['#']  = { 'path' : [ self.info['id'] ] }
			else:
				message['#']['path'].append(self.info['id'])
	
	def run(self):
		self.plugin.run(self)

		return message
	
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

		src_type = self.src.info['type']
		dst_type = self.dst.info['type']

		if src_type == '0mq-stream' and dst_type == '0mq-node':
			self.dst.input.connect(self.src.url)
			self.dst.input.setsockopt(zmq.SUBSCRIBE, '')

		elif src_type == '0mq-node' and dst_type == '0mq-node':
			self.dst.input.connect(self.src.url)
			self.dst.input.setsockopt(zmq.SUBSCRIBE, '')
		else:
			print("Error: Coulnd't connect nodes. Invalid types!")

	def run(self):
		pass

class Graph(object):

	def __init__(self):
		self.nodes = dict()
		self.edges = dict()

	def create_node(self, info):
		if 'id' not in info or 'type' not in info:
			return None

		uid = info['id']

		if info['type'] == '0mq-stream':
			self.nodes[uid] = ZMQ_Stream(info)
		elif info['type'] == '0mq-node':
			self.nodes[uid] = ZMQ_Node(info)
		else:
			print("\t. Unknown node type '{0}'!".format(info['type']))
			self.nodes[uid] = None

	def create_edge(self, info):
		if 'id' not in info or 'type' not in info:
			return None

		uid = info['id']
		if info['type'] == '0mq-edge':
			self.edges[uid] = ZMQ_Edge(info)
		else:
			print("\t. Unknown node type '{0}'!".format(info['type']))
			self.edges[uid] = None

	def start(self):
		for k in self.nodes.keys():
			self.nodes[k].thread = threading.Thread(target=self.nodes[k].run)
			self.nodes[k].thread.start()

	def wait(self):
		for k in self.nodes.keys():
			self.nodes[k].thread.join()

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
		print("[NODE] {0}: {1}, '{2}'.".format(item['id'], item['type'], item['label']))
		context['graph'].create_node(item)

	edges = dict()
	for item in reversed(conf['edges']): # NOTE : Naive topological sort
		print("[EDGE] {0} ({3}->{4}): {1}, '{2}'.".format(item['id'], item['type'], item['label'], item['src'], item['dst']))
		context['graph'].create_edge(item)

	print("[INFO] Launching node threads ...")
	context['graph'].start()
	print("[INFO] Running.")
	context['graph'].wait()

	while True:
		print("Main idle.")
		time.sleep(1)

if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("Usage: {0} <conf.json>".format(sys.argv[0]))
		sys.exit(0)
	
	with open(sys.argv[1], "rU") as conf:
		jconf = json.load(conf)
		main(jconf)