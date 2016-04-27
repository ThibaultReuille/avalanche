import plugins.base

import pylru

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.size = info['attributes']['size']
		self.key = info['attributes']['key']

		self.cache = pylru.lrucache(self.size)

	def process_message(self, message):
		key = message[self.key]

		if key not in self.cache:
			self.cache[key] = True
			return message
		else:
			# NOTE: Forcing lookup to update cache even though we don't need the value
			value = self.cache[key] 
			return None

if __name__ == "__main__":
	print("Please import this file!")