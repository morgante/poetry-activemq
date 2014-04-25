import json
import logging
import os

from twisted.internet import reactor, defer

from stompest.async import Stomp
from stompest.async.listener import SubscriptionListener
from stompest.config import StompConfig
from stompest.protocol import StompSpec


class Consumer(object):
	def __init__(self, config=None):
		if config is None:
			address = os.getenv('ACTIVEMQ_PORT_61613_TCP', 'tcp://localhost:61613')
			config = StompConfig(address)
		self.config = config
		self.queue = '/queue/poetry'
		self.errors = '/queue/poetry/errors'

		self.poems = {}

	@defer.inlineCallbacks
	def run(self):
		client = yield Stomp(self.config).connect()
		headers = {
			# client-individual mode is necessary for concurrent processing
			# (requires ActiveMQ >= 5.2)
			StompSpec.ACK_HEADER: StompSpec.ACK_CLIENT_INDIVIDUAL,
			# the maximal number of messages the broker will let you work on at the same time
			'activemq.prefetchSize': '100',
		}
		client.subscribe(self.queue, headers, listener=SubscriptionListener(self.consume, errorDestination=self.errors))

	def consumeMeta(self, message):
		self.poems[message["name"]]["count"] = message["lines"]

	def consumeLine(self, message):
		name = message["name"]
		self.poems[name]["lines"].append(message)

	def statusCheck(self, name):
		poem = self.poems[name]

		if ("count" not in poem or poem["count"] > len(poem["lines"])):
			print "I have received %d lines from %s" % (len(poem["lines"]), name)
		else:
			self.printPoem(poem)

	def printPoem(self, poem):
		# LInes could arrive in any order
		lines = sorted(poem["lines"], key=lambda msg: msg['line'])

		print "Presenting %s" % poem["name"]

		for line in lines:
			print line["content"]

	def consume(self, client, frame):
		"""
		NOTE: you can return a Deferred here
		"""

		data = json.loads(frame.body)

		name = data["name"]

		if name not in self.poems:
			self.poems[name] = {
				"name": name,
				"lines": []
			}

		if (data["type"] == "meta"):
			self.consumeMeta(data)
		elif (data["type"] == "line"):
			self.consumeLine(data)

		self.statusCheck(name)

def main():
	Consumer().run()
	reactor.run()

if __name__ == '__main__':
	main()