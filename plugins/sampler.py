import random
import json

class Plugin(object):
	def __init__(self, info):
		self.probability = info['attributes']['sampler-probability']

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			if random.uniform(0, 1) > self.probability:
				continue

			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")