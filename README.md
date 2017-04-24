# HPC PROJECT
Twitter Sentiment Analysis of President Trump’s Executive Order using Apache Spark and MQTT

Project ini terdiri dari 4 komponen utama:

1. Twitter crawler
2. Twitter producer
3. Twitter analyzer
4. Twitter dashboard

## Usage
Cara menjalankan project ini dapat dilakukan dalam 2 cara:

### Docker
```
docker pull erikaris/hpc_project:latest
```

```
docker run -i -t -P erikaris/hpc_project:latest
```

### Per Subsystem
- Install required software
```
apt-get install -y python python-pip redis-server openjdk-8-jre mysql-server mosquitto mosquitto-clients python-mysqldb
```

```
pip install tweepy redis paho-mqtt flask nltk
```

- Create MySQL database and required tables
```
mysql -u root -e "CREATE DATABASE hpc_project";
```

```
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
status VARCHAR(200), sentiment VARCHAR(50));";
```

```
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_summary \
(process_time TIMESTAMP, status_count INT);";
```

```
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_hashtag \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
hashtag VARCHAR(200));";
```

```
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_term \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
term VARCHAR(200));";
```

- Download and extract Spark
```
wget -O spark.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
tar -xvzf spark.tgz
```

- Running crawler
```
1_twitter_crawler.sh
```

- Running analysis
```
2_twitter_analysis.sh
```

- Twitter producer
```
3_twitter_producer.sh
```

- Twitter dashboard
```
4_twitter_dashboard.sh
```
