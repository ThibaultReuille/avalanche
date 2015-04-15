import time
import json
import mmap
import glob

class Plugin(object):
	def __init__(self, info):
		self.path = info['attributes']['path']
		self.schema = info['attributes']['schema']
		self.delimiter = info['attributes']['delimiter']
		self.delay = 1.0

		self.log_files = glob.glob(self.path)
		if len(self.log_files) == 0:
			print("[ERROR] No file found in path for replay!")
 
	def run(self, node):
		while True:
			for filename in self.log_files:
				with open(filename, "rU") as logfile:

					for line in logfile:
						split = line.strip().split(self.delimiter)
						if len(split) != len(self.schema):
							continue
						
						message = dict()
						for i in range(len(split)):
							message[self.schema[i]] = split[i]
						
						node.output.send_json(message)

			time.sleep(self.delay)
			#break

if __name__ == "__main__":
	print("Please import this file!")
