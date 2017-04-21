from threading import Thread
import paho.mqtt.client as paho
import redis

broker = redis.Redis(host='hpc.erikasiregar.tk')
client = paho.Client()
client.connect('hpc.erikasiregar.tk')


class Publisher(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global broker
        global client

        while True:
            topic, text = broker.blpop('trump-executive-order')
            print text
            client.publish(topic, text.decode('utf-8', 'replace'))

if __name__ == '__main__':
    Publisher().start()

