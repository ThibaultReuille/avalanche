import plugins.base

import pygeoip
import json
import os

class Plugin(plugins.base.Plugin):
	def __init__(self, info):
		current_dir = os.path.dirname(os.path.realpath(__file__))
		self.gi_asn = pygeoip.GeoIP(current_dir + "/GeoIPASNum.dat")
		self.actions = info['attributes']['actions']

	def process_message(self, message):
			geoip = dict()
			
			for action in self.actions:
				value = None
				try:
					get_key = action['get']
					if get_key not in message:
						continue
					set_key = action['set']
					action_key = action['action']
					if action_key == 'asn_by_addr':
						value = self.gi_asn.asn_by_addr(message[get_key])
					# TODO : Implement other GeoIP actions
				except:
					pass
				finally:
					geoip[set_key] = value

			message['geoip'] = geoip

			return message


if __name__ == "__main__":
	print("Please import this file!")