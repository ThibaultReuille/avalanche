import random
import json

class Plugin(object):
	def __init__(self, info):
		pass

	def run(self, node):
		while True:
			#node.output.send_json({ 'number' : random.uniform(-1, 1) })
			node.output.send_json({ 'number' : random.randint(0, 100) })
	
if __name__ == "__main__":
	print("Please import this file!")