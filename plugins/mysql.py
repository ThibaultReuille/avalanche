import json
import time
import MySQLdb

class Plugin(object):

	def __init__(self, info):
		self.host = info['attributes']['host']
		self.user = info['attributes']['user']
		self.passwd = info['attributes']['passwd']
		self.database = info['attributes']['database']
		self.query = info['attributes']['query']
		self.period = info['attributes']['period']

	def run(self, node):

		while True:

			db = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.database)

			cursor = db.cursor() 
			cursor.execute(self.query)

			for row in cursor.fetchall() :
			    print row
			    node.output.send_json(row)

			time.sleep(self.period)

if __name__ == "__main__":
	print("Please import this file!")


