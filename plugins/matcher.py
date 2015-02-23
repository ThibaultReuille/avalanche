import json
import fnmatch

class Plugin(object):
	def __init__(self, info):
		self.matches = info['attributes']['matcher:matches']

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			match = True
			for item in self.matches:
				f = item['field']
				s = item['string']
				v = item['value']
				if fnmatch.fnmatch(message[f], s) != v:
					match = False
					break

			if not match:
				continue

			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")