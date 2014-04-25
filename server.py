import json
import os

from twisted.internet import defer, reactor

from stompest.config import StompConfig

from stompest.async import Stomp
from stompest.async.listener import ReceiptListener

import optparse

def parse_args():
    usage = """usage: %prog poetry-file

This is a poetry server, which serves up poetry over ActiveMQ.

Run it like this:

  python server.py <path-to-poetry-file>

"""

    parser = optparse.OptionParser(usage)

    options, args = parser.parse_args()

    if len(args) != 1:
        parser.error('Provide exactly one poetry file.')

    poetry_file = args[0]

    if not os.path.exists(args[0]):
        parser.error('No such file: %s' % poetry_file)

    return options, poetry_file

class Producer(object):
    def __init__(self, name, text, config=None):
        if config is None:
            address = os.getenv('ACTIVEMQ_PORT_61613_TCP', 'tcp://localhost:61613')
            print "sending poetry to: %s" % address
            config = StompConfig(address)
        self.config = config
        self.queue = '/queue/poetry'
        self.name = name
        self.text = text.split('\n')

    @defer.inlineCallbacks
    def run(self):
        client = yield Stomp(self.config).connect()
        client.add(ReceiptListener(1.0))

        i = 0

        # Send the header
        yield client.send(self.queue, json.dumps({'type': 'meta', 'name': self.name, 'lines': len(self.text)}), receipt='message-%d' % i)
        i += 1

        for line in self.text:
            yield client.send(self.queue, json.dumps({'type': 'line', 'name': self.name, 'line': i, 'content': line}), receipt='message-%d' % i)
            i += 1

        client.disconnect(receipt='bye')
        yield client.disconnected # graceful disconnect: waits until all receipts have arrived
        reactor.stop()

def main():
    options, poetry_file = parse_args()

    poem = open(poetry_file).read()

    producer = Producer(poetry_file, poem)

    producer.run()
    reactor.run()

if __name__ == '__main__':
    main()