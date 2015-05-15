import json

from kafka.client import KafkaClient
from kafka.consumer import SimpleConsumer

class Plugin(object):
    def __init__(self, info):
        self.host = info['attributes']['host']
        self.group = info['attributes']['group']
        self.topic = info['attributes']['topic']

        self.client = KafkaClient(self.host)
        self.consumer = SimpleConsumer(client, self.group, self.topic)

    def run(self, node):

        while True:

            for message in self.consumer:
                node.output.send_json(message)
    
if __name__ == "__main__":
    print("Please import this file!")