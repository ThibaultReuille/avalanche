import plugins.base

import random

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.count = 0

	def process_message(self, message):
		self.count += 1
		message['counter'] = self.count
		return message
	
if __name__ == "__main__":
	print("Please import this file!")