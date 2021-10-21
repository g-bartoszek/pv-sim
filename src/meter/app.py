import argparse
import dataclasses
from datetime import datetime, timedelta
import logging
from meter import generate_measurements
import json
from rabbitmq import connection

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger('Meter')


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def parse_delta(s):
    delta = datetime.strptime(s, "%H:%M:%S")
    return timedelta(hours=delta.hour, minutes=delta.minute, seconds=delta.second)


parser = argparse.ArgumentParser(description='Mock measurements generator')

parser.add_argument('-s', '--start', dest='start', type=parse_date,
                    default='2021-01-01 00:00:00', help='Start date and time in format: "YYYY-MM-DD HH:mm:ss"')
parser.add_argument('-e', '--end', dest='end', type=parse_date,
                    default='2021-01-02 00:00:00', help='End date and time in format: "YYYY-MM-DD HH:mm:ss"')
parser.add_argument('-i', '--interval', dest='interval', type=parse_delta,
                    default='00:01:00', help='Interval between measurements in format: "HH:mm:ss"')
parser.add_argument('-r', '--realtime', dest='realtime', action='store_true',
                    help='If set measurements are generated in real time, if not, as fast as possible')
parser.add_argument('--host', default='localhost',
                    help='RabbitMQ server')


args = parser.parse_args()

start, end, interval, realtime, host = args.start, args.end, args.interval, args.realtime, args.host

LOGGER.info(f"""
Generating measurements:
Start: {start}
End: {end}
Interval: {interval}
RabbitMQ host: {host}
""")

channel, connection = connection(host)

for m in generate_measurements(start, end, interval, realtime):
    as_json = json.dumps(dataclasses.asdict(m))
    LOGGER.debug(f"Sending: {as_json}")

    try:
        channel.basic_publish(
            exchange='', routing_key='measurements', body=as_json)
    except Exception as e:
        LOGGER.error(e)

connection.close()
