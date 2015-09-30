import json
import time
from datetime import datetime
import random
import string
import os

class Plugin(object):
	def __init__(self, info):
		self.message_limit = None
		self.time_limit = None
		self.cache = None
		if 'message-limit' in info['attributes']:
			self.message_limit = info['attributes']['message-limit']
		if 'time-limit' in info['attributes']:
			self.time_limit = info['attributes']['time-limit']
		if 'cache' in info['attributes']:
			self.cache = info['attributes']['cache']
			self.create_cache_dir(self.cache)

	def create_cache_dir(self, path):
		try: 
			os.makedirs(path)
		except OSError:
			if not os.path.isdir(path):
				raise

	def create_random_word(self, length):
	   return ''.join(random.choice(string.lowercase) for i in range(length))

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

				# NOTE : This doesn't work if we don't receive messages
				if self.cache is not None:
					filename = "{0}/{1}.{2}.json".format(self.cache, datetime.utcnow().strftime("%Y-%m-%d_%H:%M:%S"), self.create_random_word(4))
					with open(filename, 'w') as outfile:
						json.dump(messages, outfile)

				messages = list()
				last_time = time.time()

	
if __name__ == "__main__":
	print("Please import this file!")