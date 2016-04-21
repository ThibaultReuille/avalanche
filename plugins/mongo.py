import plugins.base

import pymongo

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.host = info['attributes']["host"]
		self.port = info['attributes']["port"]
		self.database = info['attributes']["database"]
		self.collection = info['attributes']["collection"]
		self.index = info['attributes']['index']

		self.client = pymongo.MongoClient(self.host, self.port)
		self.target = self.client[self.database][self.collection]
		self.target.create_index([ (self.index, pymongo.ASCENDING) ])

		self.message_id = dict()

	def process_message(self, message):

		try:
			self.message_id[self.index] = message[self.index]
		except Exception as e:
			print("Exception: {0}".format(e))

		self.target.update_one(self.message_id, { "$set" : message }, upsert=True)
		return message
