#!/usr/bin/env bash

/etc/init.d/mysql start
mysql -u root -e "CREATE DATABASE hpc_project";
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
status VARCHAR(200), sentiment VARCHAR(50));";
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_summary \
(process_time TIMESTAMP, status_count INT);";
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_hashtag \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
hashtag VARCHAR(200));";
mysql -u root -D "hpc_project" -e "CREATE TABLE trump_executive_order_term \
(process_time TIMESTAMP, status_time TIMESTAMP DEFAULT '1970-01-01 00:00:01', \
term VARCHAR(200));";

nohup redis-server /etc/redis/redis.conf > redis.log &
nohup mosquitto -c /etc/mosquitto/mosquitto.conf > mosquitto.log &

nohup /app/1_twitter_crawler.sh > crawler.log &
nohup /app/2_twitter_analysis.sh > analysis.log &
nohup /app/3_twitter_producer.sh > producer.log &
nohup /app/4_twitter_dashboard.sh > dashboard.log &

bash