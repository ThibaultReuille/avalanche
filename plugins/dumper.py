import plugins.base
import json
import time
import datetime
import os

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		self.folder = info['attributes']['folder']
		
		if "filename" in info['attributes']:
			self.filename = info['attributes']['filename']
		else:
			self.filename = "%Y-%m-%d_%H:%M:%S.json"

		self.create_cache_dir(self.folder)

	def create_cache_dir(self, path):
	    try: 
	        os.makedirs(path)
	    except OSError:
	        if not os.path.isdir(path):
	            raise

	def process_message(self, message):

		now = time.time()

		timestamp = datetime.datetime.fromtimestamp(now).strftime(self.filename)
		with open("{0}/{1}".format(self.folder, timestamp), "w") as result_file:
			json.dump(message, result_file, indent=4)

		return message

if __name__ == "__main__":
	print("Please import this file!")