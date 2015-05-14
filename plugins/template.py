import json

class Plugin(object):
	def __init__(self, info):
		# NOTE: The info argument contains the full node definition
		# written in the pipeline configuration file.
		pass

	def run(self, node):
		# NOTE: Each node runs on its own thread/process,
		# Here we enter our infinite loop.
		while True:

			# NOTE: Read incoming data sent to our node
			data = node.input.recv()

			# NOTE: Parse it as a JSON message
			message = json.loads(data)
			
			# NOTE: This template plugin doesn't do anything except being a passthru filter.
			# This is where the processing would actually happen in a real processor.
			# You can send whatever data you like in the output stream. That can be a modified
			# version of the incoming messages or any other message of your creation.

			# NOTE: Send it back through the pipeline 
			node.output.send_json(message)
	
if __name__ == "__main__":
	print("Please import this file!")
