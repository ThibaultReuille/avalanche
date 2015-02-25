import time
import json
import mmap
import glob

class Plugin(object):
	def __init__(self, info):
		self.path = info['attributes']['replayer:path']
		self.schema = info['attributes']['replayer:schema']
		self.delimiter = info['attributes']['replayer:delimiter']
		self.delay = 1.0

	def run(self, node):

		while True:

			for filename in glob.glob(self.path):

				with open(filename, "rU") as logfile:

					for line in logfile:

						split = line.strip().split(self.delimiter)
						if len(split) != len(self.schema):
							continue
						
						message = dict()
						for i in range(len(split)):
							message[self.schema[i]] = split[i]
						
						node.output.send_json(message)

			node.output.send_json({ "type" : "---------------------------------------------" })
			time.sleep(self.delay)
			break

if __name__ == "__main__":
	print("Please import this file!")
