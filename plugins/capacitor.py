import json
import time

class Plugin(object):
	def __init__(self, info):
		self.message_limit = None
		self.time_limit = None
		if 'message-limit' in info['attributes']:
			self.message_limit = info['attributes']['message-limit']
		if 'time-limit' in info['attributes']:
			self.time_limit = info['attributes']['time-limit']

	def run(self, node):

		if self.message_limit is None and self.time_limit is None:
			print('[ERROR] No capacitor limit defined!')
			return

		last_time = time.time()
		last_count = 0

		messages = list()

		while True:
			data = node.input.recv()
			message = json.loads(data)

			messages.append(message)

			t = time.time()

			if (self.message_limit is not None and len(messages) > self.message_limit) or \
			   (self.time_limit is not None and t - last_time > self.time_limit):
				node.output.send_json(messages)
				messages = list()
				last_time = time.time()

	
if __name__ == "__main__":
	print("Please import this file!")