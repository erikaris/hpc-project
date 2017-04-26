HPC PROJECT

# Twitter Sentiment Analysis of President Trump’s Executive Order using Apache Spark and MQTT

Presentation's slide: https://docs.google.com/presentation/d/1uu_o3Xn6Km2GtLikEi9pnLsZFHoev6PRy2TCq77tjNc/edit?usp=sharing

The Twitter Sentiment Analysis Project is a tool that download twitter streaming data related to President Trump's Executive Order towards certain issues.
The tweets that are downloaded are the tweets containing hashtags: \#ExecutiveOrder, \#Trump, \#WinningForAmerica, \#MuslimBan, \#Muslim, \#TerrorBan, \#TravelBan, \#NoBanNoWallNoRaids, \#immigration, \#refugee, \#MakeAmericaGreatAgain, \#travel, and \#Latino.

This is a final project for the course CS824 - High Parallel Computing and Big Data that I took at Old Dominion University (ODU) in Spring 2017.

This project comprises 4 main components:
1. Twitter crawler    --> Crawl the streaming Twitter data.
2. Twitter producer   --> Fetch data from Redis and publish it to Spark Streaming.
3. Twitter analyzer   --> Conduct sentiment analysis on the streaming data.
4. Twitter dashboard  --> Visualize the sentiment analysis result.

## Usage
There are 2 (two) ways that are provided to use this tool:
1. Using Docker (Recommended)
2. Without Docker

### Method 1: Using Docker
Using Docker is really recommended because user does not have to worry about software dependencies and can avoid the hassle of downloading and installing the required softwares.
The user should download and install Docker from https://docs.docker.com/engine/installation/ or from https://docs.docker.com/docker-for-windows/install/ (for Windows OS), then simply follows the steps below:

1. Open terminal and pull the Docker Image, using command:
```
docker pull erikaris/hpc_project:latest
```

2. Run the Docker Image as a container, using command: 

Notes: User must first go to https://apps.twitter.com to create Twitter App Key. 
```
docker run -i -t -d --memory=2g -p 5555:80  -e PORT=80 -e CONSUMER_KEY=<USER_CONSUMER_KEY> -e CONSUMER_SECRET=<USER_CONSUMER_SECRET> -e ACCESS_TOKEN_KEY=<USER_TOKEN_KEY> -e ACCESS_TOKEN_SECRET=<USER_TOKEN_SECRET> --name=hpc-project erikaris/hpc-project:latest /app/entrypoint.sh
```

3. The second the container is running, the crawling, producing, and analyzing process will be automatically started. The next thing that a user should do is opening the dashboard to see the visualization of the sentiment analysis result.
Type the command below on terminal to get the URI:
```
ip address
```
![ip_address](https://cloud.githubusercontent.com/assets/16355740/25354181/0c57ba34-2900-11e7-9478-119be7ba2fe7.png)

4. Copy the ip address resulted from the command in point no. 3 and paste it onto a web browser.

5. The user can see the visualization of the sentiment analysis as illustrated in the screenshot below.
![visualization_dashboard](https://cloud.githubusercontent.com/assets/16355740/25354542/4b8ecac0-2901-11e7-998d-9424cbbc9567.png)


### Method 2: Without Docker
Without using Docker, the user has to install all the required software before starting the sentiment analysis tool.

1. Install required software
```
apt-get install -y python python-pip redis-server openjdk-8-jre mysql-server mosquitto mosquitto-clients python-mysqldb
```

```
pip install tweepy redis paho-mqtt flask nltk
```

2. Create MySQL database and required tables
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

3. Download and extract Spark
```
wget -O spark.tgz http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
tar -xvzf spark.tgz
```

4. Run the crawler process
```
1_twitter_crawler.sh
```

5. Run the analysis process
```
2_twitter_analysis.sh
```

6. Run the Twitter producer
```
3_twitter_producer.sh
```

7. Run the Twitter dashboard
```
4_twitter_dashboard.sh
```
8. View the visualization dashboard on a web browser by accessing the URI: *localhost*
