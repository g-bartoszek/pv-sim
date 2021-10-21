from datetime import datetime
import json
import subprocess
import os
import pika
import tempfile
import time


def timestamp(json_input):
    return json.loads(json_input)['timestamp']


def test_meter():
    dir = os.path.dirname(os.path.realpath(__file__))

    subprocess.call(
        ['python', dir + '/../src/meter/app.py', '-s', '2020-01-01 00:00:00', '-e', '2020-01-01 03:00:00', '-i', '01:00:00'])

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='measurements')
    consume = channel.consume('measurements', auto_ack=True)

    assert timestamp(next(consume)[2]) == datetime(2020, 1, 1, 0).timestamp()
    assert timestamp(next(consume)[2]) == datetime(2020, 1, 1, 1).timestamp()
    assert timestamp(next(consume)[2]) == datetime(2020, 1, 1, 2).timestamp()
    assert timestamp(next(consume)[2]) == datetime(2020, 1, 1, 3).timestamp()

    connection.close()


def test_pv_sim():
    dir = os.path.dirname(os.path.realpath(__file__))

    output = tempfile.NamedTemporaryFile()

    app = subprocess.Popen(
        ['python', dir + '/../src/pv_sim/app.py', '-o', output.name])

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='measurements')

    channel.basic_publish(exchange='', routing_key='measurements',
                          body='{"timestamp": 1577833200.0, "value": 7690.193618512156}')
    channel.basic_publish(exchange='', routing_key='measurements',
                          body='{"timestamp": 1577836800.0, "value": 2086.3717389895514}')

    time.sleep(1)

    app.terminate()
    app.wait()
    connection.close()

    result = open(output.name, 'r').readlines()

    assert timestamp(result[0]) == 1577833200.0
    assert timestamp(result[1]) == 1577836800.0


def test_meter_and_pv_sim():
    dir = os.path.dirname(os.path.realpath(__file__))

    output = tempfile.NamedTemporaryFile()

    app = subprocess.Popen(
        ['python', dir + '/../src/pv_sim/app.py', '-o', output.name])

    subprocess.call(
        ['python', dir + '/../src/meter/app.py', '-s', '2020-01-01 00:00:00', '-e', '2020-01-01 03:00:00', '-i', '01:00:00'])

    time.sleep(1)

    app.terminate()
    app.wait()

    result = open(output.name, 'r').readlines()

    assert len(result) == 4
    assert timestamp(result[0]) == datetime(2020, 1, 1, 0).timestamp()
    assert timestamp(result[1]) == datetime(2020, 1, 1, 1).timestamp()
    assert timestamp(result[2]) == datetime(2020, 1, 1, 2).timestamp()
    assert timestamp(result[3]) == datetime(2020, 1, 1, 3).timestamp()
