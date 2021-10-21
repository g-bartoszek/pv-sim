import pika


def connection(host: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
    channel = connection.channel()
    channel.queue_declare(queue='measurements')

    return (channel, connection)
