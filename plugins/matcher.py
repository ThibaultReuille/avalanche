import json
import fnmatch

class Plugin(object):
	def __init__(self, info):
		self.matches = info['attributes']['matcher:matches']

		self.processor = list()
		for m in self.matches:
			f = m['field']
			v = m['value']

			if 'string' in m:
				self.processor.append({
					'field' : f,
					'value' : v,
					'lines' : [ m['string'] ]
				})
			elif 'file' in m:
				with open(m['file'], "rU") as infile:
					lines = [ line.strip() for line in infile.readlines() ]
					print("lines", lines)
					self.processor.append({
						'field' : f,
						'value' : v,
						'lines' : lines
					})
			else:
				print("[ERROR] Couldn't parse matcher element! Skipped.")

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			match = True
			for item in self.processor:
				f = item['field']
				v = item['value']

				local_match = False
				for line in item['lines']:
					local_match = fnmatch.fnmatch(message[f], line) or local_match
					if local_match:
						break

				match = match and (local_match == v)
				if not match:
					break

			if not match:
				continue

			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")