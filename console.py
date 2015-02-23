#!/usr/bin/env python

import sys
import zmq
import json
import time
import pprint as pp

if len(sys.argv) != 3:
	print("Usage: {0} <host> <port>".format(sys.argv[0]))
	sys.exit(0)

ctx = zmq.Context()
s = ctx.socket(zmq.SUB)

url = "tcp://{0}:{1}".format(sys.argv[1], sys.argv[2])
print("Connecting to " + url + " ...")
s.connect(url)
s.setsockopt(zmq.SUBSCRIBE, '')

while True:
    line = s.recv()
    jdata = json.loads(line)

    print("{0}: {1}\n".format(time.time(), jdata))
