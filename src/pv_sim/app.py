import argparse
import dataclasses
import json
import logging
from rabbitmq import connection
from pv import handle_message
import signal

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger('PV')

parser = argparse.ArgumentParser(description='PV simulator')
parser.add_argument('--host', default='localhost',
                    help='RabbitMQ server')
parser.add_argument('-o', '--output', default='/tmp/output',
                    help='Output file')


args = parser.parse_args()

(host, output) = (args.host, args.output)


def write(file, result):
    """ Writes given result to file """
    result = json.dumps(dataclasses.asdict(result))
    file.write(f"{result}\n")


LOGGER.info(f"""
PV Simulator:
RabbitMQ host: {host}
Output file: {output}
""")

(channel, connection) = connection(host)

with open(output, "w") as output:
    channel.basic_consume(queue='measurements',
                          auto_ack=True,
                          on_message_callback=lambda ch, method, properties, body: handle_message(body, lambda s: write(output, s)))

    signal.signal(signal.SIGINT, lambda *args: channel.stop_consuming())
    signal.signal(signal.SIGTERM, lambda *args: channel.stop_consuming())

    channel.start_consuming()
    
connection.close()

