FROM ubuntu:xenial
MAINTAINER Erika Siregar <erikaris1515@gmail.com>

# Change ubuntu mirror
RUN sed -i 's|http://archive.ubuntu.com/ubuntu/|mirror://mirrors.ubuntu.com/mirrors.txt|g' /etc/apt/sources.list
RUN apt-get update -y

# Install python pip redis java
RUN apt-get install -y python python-pip redis-server openjdk-8-jre

# Install mysql
RUN { \
		echo mysql-server-5.7 mysql-server/root_password password ''; \
		echo mysql-server-5.7 mysql-server/root_password_again password ''; \
		echo mysql-server mysql-server/root_password password ''; \
		echo mysql-server mysql-server/root_password_again password ''; \
	} | debconf-set-selections
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server

# Install mqtt broker
RUN apt-get install -y mosquitto mosquitto-clients

# Download spark
RUN apt-get install -y wget
RUN wget -O spark.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
RUN tar -xvzf spark.tgz
RUN mv spark-2.1.0-bin-hadoop2.7 spark
RUN rm spark.tgz

ENV SPARK_HOME="/spark"
ENV PATH="${SPARK_HOME}/bin:${SPARK_HOME}/sbin:${PATH}"
ENV PYTHONPATH="${SPARK_HOME}/python:${SPARK_HOME}/python/lib/py4j-0.10.4-src.zip:${SPARK_HOME}/python/build:${PYTHONPATH}"

# Install mysql python
RUN apt-get install -y python-mysqldb

RUN pip install --upgrade pip --no-cache-dir
RUN pip install tweepy redis paho-mqtt flask nltk --no-cache-dir

# Project dir
ENV CONSUMER_KEY='85FOoqjpMwDzU6JYfxlCkYFXR'
ENV CONSUMER_SECRET='7jCu216FRhU0nTnx1c8j9rXXNnItsoHiBV4WPalSUUaQkiE27O'
ENV ACCESS_TOKEN_KEY='2689318266-7KnyuRjv8MitXGiiLkjgBeVzFqIyjxAVbVaRY8v'
ENV ACCESS_TOKEN_SECRET='BqdwUYQXMkNtWHt2IClHjSOkJxhFdL8Cp2pObqVDF6lls'

RUN mkdir -p /app
COPY . /app
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/1_twitter_crawler.sh
RUN chmod +x /app/2_twitter_analysis.sh
RUN chmod +x /app/3_twitter_producer.sh
RUN chmod +x /app/4_twitter_dashboard.sh

ENV PORT 80
EXPOSE $PORT
ENTRYPOINT /app/entrypoint.sh
