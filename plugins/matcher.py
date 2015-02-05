import json
import fnmatch

class Plugin(object):
	def __init__(self, info):
		self.string = info['attributes']['matcher-string']
		self.field = info['attributes']['matcher-field']

		self.invert = False
		if "matcher-invert" in info['attributes']:
			self.invert = info['attributes']['matcher-invert']

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			if self.field not in message:
				continue

			if fnmatch.fnmatch(message[self.field], self.string) == self.invert:
				continue

			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")