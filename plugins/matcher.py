import json
import fnmatch

class Plugin(object):
	def __init__(self, info):
		self.string = info['attributes']['matcher-string']
		self.field = info['attributes']['matcher-field']

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			if self.field not in message:
				continue

			if not fnmatch.fnmatch(message[self.field], self.string):
				continue

			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")