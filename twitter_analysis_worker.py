#!/usr/bin/env python


from py4j.protocol import Py4JJavaError
from pyspark.storagelevel import StorageLevel
from pyspark.serializers import UTF8Deserializer
from pyspark.streaming import DStream


class MQTTUtils(object):
    @staticmethod
    def createStream(ssc, brokerUrl, topic, storageLevel=StorageLevel.MEMORY_AND_DISK_SER_2):
        """
        Create an input stream that pulls messages from a Mqtt Broker.

        :param ssc:  StreamingContext object
        :param brokerUrl:  Url of remote mqtt publisher
        :param topic:  topic name to subscribe to
        :param storageLevel:  RDD storage level.
        :return: A DStream object
        """
        jlevel = ssc._sc._getJavaStorageLevel(storageLevel)

        try:
            helperClass = ssc._jvm.java.lang.Thread.currentThread().getContextClassLoader() \
                .loadClass("org.apache.spark.streaming.mqtt.MQTTUtilsPythonHelper")
            helper = helperClass.newInstance()
            jstream = helper.createStream(ssc._jssc, brokerUrl, topic, jlevel)
        except Py4JJavaError as e:
            if 'ClassNotFoundException' in str(e.java_exception):
                MQTTUtils._printErrorMsg(ssc.sparkContext)
            raise e

        return DStream(jstream, ssc, UTF8Deserializer())

    @staticmethod
    def _printErrorMsg(sc):
        print("""
________________________________________________________________________________________________

  Spark Streaming's MQTT libraries not found in class path. Try one of the following.

  1. Include the MQTT library and its dependencies with in the
     spark-submit command as

     $ bin/spark-submit --packages org.apache.spark:spark-streaming-mqtt:%s ...

  2. Download the JAR of the artifact from Maven Central http://search.maven.org/,
     Group Id = org.apache.spark, Artifact Id = spark-streaming-mqtt-assembly, Version = %s.
     Then, include the jar in the spark-submit command as

     $ bin/spark-submit --jars <spark-streaming-mqtt-assembly.jar> ...
________________________________________________________________________________________________
""" % (sc.version, sc.version))


# Export PATH and PYTHONPATH
# export SPARK_HOME=../spark
# export PATH=$SPARK_HOME/bin:$PATH
# export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.8.2.1-src.zip:$SPARK_HOME/python/build:$PYTHONPATH


## Imports
import time
import json
import re
from datetime import datetime
from pyspark import SparkConf, SparkContext
from pyspark.sql import SparkSession, Row
from pyspark.sql.context import SQLContext
from pyspark.streaming import StreamingContext

# ===========================================================
# SETTINGS
# ===========================================================
broker_url = "tcp://localhost:1883"
topic = "trump-executive-order"
mysql_host = 'localhost'
mysql_user = 'root'
mysql_password = ''
mysql_db = 'hpc_project'

sentiment_table = 'trump_executive_order'
execute_summary_table = 'trump_executive_order_summary'
hashtag_table = 'trump_executive_order_hashtag'
term_table = 'trump_executive_order_term'
# ===========================================================

conf = SparkConf().setAppName('Twitter')
conf = conf.setMaster('local[*]')
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 5)
ssc.checkpoint("checkpoint")

sql_context = SQLContext(sc)

stopwords = [u'all', u'just', u'being', u'over', u'both', u'through', u'yourselves', u'its', u'before',
             u'o', u'hadn', u'herself', u'll', u'had', u'should', u'to', u'only', u'won', u'under',
             u'ours', u'has', u'do', u'them', u'his', u'very', u'they', u'not', u'during', u'now', u'him',
             u'nor', u'd', u'did', u'didn', u'this', u'she', u'each', u'further', u'where', u'few',
             u'because', u'doing', u'some', u'hasn', u'are', u'our', u'ourselves', u'out', u'what', u'for',
             u'while', u're', u'does', u'above', u'between', u'mustn', u't', u'be', u'we', u'who', u'were',
             u'here', u'shouldn', u'hers', u'by', u'on', u'about', u'couldn', u'of', u'against', u's',
             u'isn', u'or', u'own', u'into', u'yourself', u'down', u'mightn', u'wasn', u'your', u'from',
             u'her', u'their', u'aren', u'there', u'been', u'whom', u'too', u'wouldn', u'themselves',
             u'weren', u'was', u'until', u'more', u'himself', u'that', u'but', u'don', u'with', u'than',
             u'those', u'he', u'me', u'myself', u'ma', u'these', u'up', u'will', u'below', u'ain', u'can',
             u'theirs', u'my', u'and', u've', u'then', u'is', u'am', u'it', u'doesn', u'an', u'as',
             u'itself', u'at', u'have', u'in', u'any', u'if', u'again', u'no', u'when', u'same', u'how',
             u'other', u'which', u'you', u'shan', u'needn', u'haven', u'after', u'most', u'such', u'why',
             u'a', u'off', u'i', u'm', u'yours', u'so', u'y', u'the', u'having', u'once']


def get_spark_session_instance(spark_conf):
    if ('sparkSessionSingletonInstance' not in globals()):
        globals()['sparkSessionSingletonInstance'] = SparkSession \
            .builder \
            .config(conf=spark_conf) \
            .getOrCreate()
    return globals()['sparkSessionSingletonInstance']


def remove_hash_etc(text):
    words = re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", text).split()
    words = filter(lambda word: word != 're' and word != 'rt', words)
    return ' '.join(words)


def decide_sentiment(score):
    # {'neg': 0.158, 'neu': 0.842, 'pos': 0.0, 'compound': -0.128}
    compound = score['compound']

    keys = ['Negative', 'Neutral', 'Positive']
    values = {0: score['neg'], 1: score['neu'], 2: score['pos']}
    max_key = max(values, key=lambda k: values[k])

    return keys[max_key]


def detect_hashtags(text):
    return re.findall(r"#(\w+)", text)


def count_in_a_partition(iterator):
    yield sum(1 for _ in iterator)


def process_rdd(rdd):
    now = datetime.now()

    try:
        spark = get_spark_session_instance(rdd.context.getConf())
        sc = spark.sparkContext

        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        sid = SentimentIntensityAnalyzer(lexicon_file='vader_lexicon.txt')
        rdd = rdd.map(lambda (ts, text): (ts, text, remove_hash_etc(text))) \
            .map(lambda (ts, ori_text, text): (ts, ori_text, text, sid.polarity_scores(text))) \
            .map(lambda (ts, ori_text, text, score): (ts, ori_text, text, decide_sentiment(score)))

        # Save sentiment to mysql
        row_rdd = rdd.map(lambda (ts, ori_text, text, sentiment):
                          Row(process_time=now, status_time=datetime.fromtimestamp(int(ts) / 1000),
                              status=ori_text, sentiment=sentiment))
        sentiment_df = spark.createDataFrame(row_rdd)
        sentiment_df.write.format("jdbc").mode('append') \
            .option("url", "jdbc:mysql://{0}/{1}".format(mysql_host, mysql_db)) \
            .option("driver", "com.mysql.jdbc.Driver").option("dbtable", sentiment_table) \
            .option("user", mysql_user).option("password", mysql_password).save()

        # To select
        # sentiment_df = spark.read.format("jdbc") \
        #     .option("url", "jdbc:mysql://{0}/{1}".format(mysql_host, mysql_db)) \
        #     .option("driver", "com.mysql.jdbc.Driver").option("dbtable", sentiment_table) \
        #     .option("user", mysql_user).option("password", mysql_password).load()
        # sentiment_df.show()

        # Parse hashtag and save to mysql
        hashtag_rdd = rdd.map(lambda (ts, ori_text, text, sentiment): (ts, detect_hashtags(ori_text)))\
            .flatMapValues(lambda w: w)\
            .map(lambda (ts, hashtag): Row(process_time=now, status_time=datetime.fromtimestamp(int(ts) / 1000),
                                           hashtag=hashtag))
        hashtag_df = spark.createDataFrame(hashtag_rdd)
        hashtag_df.write.format("jdbc").mode('append') \
            .option("url", "jdbc:mysql://{0}/{1}".format(mysql_host, mysql_db)) \
            .option("driver", "com.mysql.jdbc.Driver").option("dbtable", hashtag_table) \
            .option("user", mysql_user).option("password", mysql_password).save()

        # Parse term and save to mysql
        term_rdd = rdd.map(lambda (ts, ori_text, text, sentiment): (ts, text.split()))\
            .flatMapValues(lambda w: w)\
            .filter(lambda (ts, term): term and term.lower() not in stopwords)\
            .map(lambda (ts, term): Row(process_time=now, status_time=datetime.fromtimestamp(int(ts) / 1000),
                                        term=term))
        term_df = spark.createDataFrame(term_rdd)
        term_df.write.format("jdbc").mode('append') \
            .option("url", "jdbc:mysql://{0}/{1}".format(mysql_host, mysql_db)) \
            .option("driver", "com.mysql.jdbc.Driver").option("dbtable", term_table) \
            .option("user", mysql_user).option("password", mysql_password).save()

        # Save execution summary to mysql
        num_status_processed = sum(rdd.mapPartitions(count_in_a_partition).collect())
        summ_row_rdd = sc.parallelize([[now, num_status_processed]], 1)\
            .map(lambda (ts, count): Row(process_time=ts, status_count=count))
        summ_row_df = spark.createDataFrame(summ_row_rdd)
        summ_row_df.write.format("jdbc").mode('append') \
            .option("url", "jdbc:mysql://{0}/{1}".format(mysql_host, mysql_db)) \
            .option("driver", "com.mysql.jdbc.Driver").option("dbtable", execute_summary_table) \
            .option("user", mysql_user).option("password", mysql_password).save()

    except Exception, e:
        print str(e)


if __name__ == '__main__':
    try:
        import pip
        pip.main(['install', 'nltk'])
        pip.main(['install', 'redis'])
    except Exception, e:
        pass

    stream = MQTTUtils.createStream(ssc, broker_url, topic)
    word_stream = stream.map(lambda line: json.loads(line.lower().encode('utf-8', errors='replace')))
    word_stream.foreachRDD(lambda rdd: process_rdd(rdd))

    ssc.start()
    ssc.awaitTermination()
