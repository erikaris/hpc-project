import json
import sys
from threading import Thread
import redis
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import StreamListener


# broker = redis.Redis(host='hpc.erikasiregar.tk')
broker = redis.Redis(host='localhost')
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
    def __init__(self, consumer_key, consumer_secret, token_key, token_secret):
        Thread.__init__(self)
        self.consumer_key, self.consumer_secret, self.token_key, self.token_secret = \
            consumer_key, consumer_secret, token_key, token_secret

    def run(self):
        auth = OAuthHandler(self.consumer_key, self.consumer_secret)
        auth.set_access_token(self.token_key, self.token_secret)
        stream = Stream(auth, TwitterListener())

        while True:
            try:
                # stream.sample()
                stream.filter(languages=["en"], track=['trump'])
            except:
                pass

if __name__ == '__main__':
    args = sys.argv
    if len(args) < 5:
        args[1], args[2], args[3], args[4] = '85FOoqjpMwDzU6JYfxlCkYFXR', \
                                             '7jCu216FRhU0nTnx1c8j9rXXNnItsoHiBV4WPalSUUaQkiE27O', \
                                             '2689318266-7KnyuRjv8MitXGiiLkjgBeVzFqIyjxAVbVaRY8v', \
                                             'BqdwUYQXMkNtWHt2IClHjSOkJxhFdL8Cp2pObqVDF6lls'

    TwitterCrawler(args[1], args[2], args[3], args[4]).start()

