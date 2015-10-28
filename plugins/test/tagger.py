import plugins.base

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.field = info['attributes']['field']
		self.value = info['attributes']['value']

	def process_message(self, message):
		message[self.field] = self.value
		return message
	
if __name__ == "__main__":
	print("Please import this file!")