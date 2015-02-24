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

metrics = dict()
metrics['volume'] = 0
metrics['start_time'] = time.time()

time_delay = 10

while True:
    line = s.recv()
    jdata = json.loads(line)

    metrics['current_time'] = time.time()
    metrics['volume'] += 1

    if metrics['current_time'] - metrics['start_time'] > time_delay:

    	metrics['msg/sec'] = metrics['volume'] / (metrics['current_time'] - metrics['start_time'])
    	print(json.dumps(metrics))
    	
    	metrics['start_time'] = metrics['current_time']
    	metrics['volume'] = 0

    print("{0}: {1}".format(time.time(), json.dumps(jdata)))

