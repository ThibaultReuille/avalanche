import json
import fnmatch

class Filter(object):
	def __init__(self, attributes):
		self.field = attributes['field']
		self.condition = attributes['condition']
		self.result = attributes['result']

		if 'values' in attributes:
			self.values = attributes['values']
		elif 'file' in attributes:
			with open(attributes['file'], "rU") as infile:
				self.values = [ line.strip() for line in infile.readlines() ]
		else:
			raise Exception("No 'values' or 'file' field defined!")

	def test(self, message):
		raise Exception("Not implemented!")

class InFilter(Filter):
	def __init__(self, attributes):
		super(InFilter, self).__init__(attributes)
		self.elements = set(self.values)

	def test(self, message):
		return message[self.field] in self.elements

class MatchFilter(Filter):
	def __init__(self, attributes):
		super(MatchFilter, self).__init__(attributes)

	def test(self, message):
		for element in self.values:
			if not fnmatch.fnmatch(message[self.field], element):
				return False
		return True

class Plugin(object):
	def __init__(self, info):

		processor_info = info['attributes']['processor']

		self.processor = list()
		for i in range(len(processor_info)):
			try:
				p = None
				if processor_info[i]['condition'] == "in":
					p = InFilter(processor_info[i])
				elif processor_info[i]['condition'] == "match":
					p = MatchFilter(processor_info[i])
				else:
					raise Exception("Unknown condition: '{0}'!".format(processor_info['condition']))
				self.processor.append(p)
			except Exception, e:
				print("[ERROR] Couldn't parse matcher processor: {0}".format(str(e)))

				
	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			result = True
			for item in self.processor:
				result = result and (item.test(message) == item.result)
				if not result:
					break

			if result:
				node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")