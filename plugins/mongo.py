import plugins.base

import json
import pymongo

class Plugin(plugins.base.Plugin):
    def __init__(self, info):
        self.host = info['attributes']["host"]
        self.port = int(info['attributes']["port"])
        self.database = info['attributes']["database"]
        self.collection = info['attributes']["collection"]
        self.indices = info['attributes']['indices']

        print("[Mongo] Connecting to {}:{}/{}/{}".format(self.host, self.port, self.database, self.collection))
        self.client = pymongo.MongoClient(self.host, self.port)
        self.target = self.client[self.database][self.collection]

        for index in self.indices:
            print("[Mongo] Creating index on key '{}' ...".format(index))
            self.target.create_index([ (index, pymongo.ASCENDING) ])

    def process_message(self, message):
        # NOTE: This ensures we have the right JSON format for BSON encoding (UTF-8)
        json_string = json.dumps(message)
        json_obj = json.loads(json_string)

        result = self.target.insert_one(json_obj)
        return message
