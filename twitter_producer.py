from threading import Thread
import paho.mqtt.client as paho
import redis

redis_client = redis.Redis(host='localhost')
mqtt_client = paho.Client()
mqtt_client.connect('localhost')


class Publisher(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global redis_client
        global mqtt_client

        while True:
            topic, text = redis_client.blpop('trump-executive-order')
            print text
            mqtt_client.publish(topic, text.decode('utf-8', 'replace'))

if __name__ == '__main__':
    Publisher().start()

