import plugins.base

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.history = info['attributes']['history']
		self.fields = info['attributes']['fields']

		self.cache = list()
		self.index = -1

	def process_message(self, message):
		
		vector = list()
		for k in self.fields:
			if k not in message:
				return message
			vector.append(message[k])

		found = False
		for e in self.cache:
			if e == vector:
				found = True
				break

		#print(self.cache, vector, found)

		if found:
			return None
		else:
			if len(self.cache) < self.history:
				self.cache.append(vector)
			else:
				self.cache[self.index] = vector
			self.index = (self.index + 1) % self.history

			return message
	
if __name__ == "__main__":
	print("Please import this file!")