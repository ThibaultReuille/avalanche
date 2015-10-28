import random
import json

class Plugin(object):
	def __init__(self, info):
		self.probability = info['attributes']['probability']

	def process_message(self, message):
		return message if random.uniform(0, 1) <= self.probability else None
	
if __name__ == "__main__":
	print("Please import this file!")