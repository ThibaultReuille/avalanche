import json

from collections import deque

class Plugin(object):
	def __init__(self):
		pass

	def run(self, node):
		while True:
			data = node.input.recv()
			message = json.loads(data)

			output = self.process_message(message)
			
			if output is None:
				continue

			if isinstance(output, list):
				for msg in output:
					node.output.send_json(msg)
			else:
				node.output.send_json(output)

	def process_message(self, message):
		return message  

class PluginRack(Plugin):
	def __init__(self):
		self.plugins = list()

	def run(self, node):
		while True:

			data = node.input.recv()
			message = json.loads(data)

			input_messages = deque()
			input_messages.append(message)

			output_messages = deque()

			for plugin in self.plugins:

				while len(input_messages) > 0:
					msg = input_messages.popleft()
					output = plugin.process_message(msg)

					if output is None:
						continue
					elif isinstance(output, list):
						output_messages.extend(output)
					else:
						output_messages.append(output)

				input_messages, output_messages = output_messages, input_messages

			while len(input_messages) > 0:
				node.output.send_json(input_messages.popleft())