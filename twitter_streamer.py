import json
from threading import Thread
import redis
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import StreamListener


broker = redis.Redis(host='hpc.erikasiregar.tk')
broker_channel = 'trump-executive-order'
text_to_track = ['executive order', 'winning for america', 'muslim ban', 'terror ban', 'travel ban', 'immigration',
                 'refugee', 'latino', 'executiveorder', 'winningforamerica', 'muslimban', 'muslim', 'terrorban',
                 'travelban', 'nobannowallnoraids', 'makeamericagreatagain']


class TwitterListener(StreamListener):
    def on_data(self, data):
        global broker

        data = json.loads(data)

        text = data['text']
        timestamp_ms = data['timestamp_ms']
        for term in text_to_track:
            if 'trump' in data['text'].lower() and term in data['text'].lower():
                print broker.rpush(broker_channel, json.dumps([timestamp_ms, text]))

    def on_error(self, status):
        print 'Streaming error:', status


class TwitterCrawler(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        auth = OAuthHandler('ofYvOilGnckcvn5gARVJnIhsY', 'QC8p29bOTm66R2ZFnRvndHWFkfK8YFPVCfSqbwe8gjHavA6CYc')
        auth.set_access_token('	2689318266-7KnyuRjv8MitXGiiLkjgBeVzFqIyjxAVbVaRY8v',
                              'BqdwUYQXMkNtWHt2IClHjSOkJxhFdL8Cp2pObqVDF6lls')
        stream = Stream(auth, TwitterListener())

        while True:
            try:
                # stream.sample()
                stream.filter(languages=["en"], track=['trump'])
            except:
                pass

if __name__ == '__main__':
    TwitterCrawler().start()

