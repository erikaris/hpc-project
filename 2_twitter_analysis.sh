#!/usr/bin/env bash

# Export PATH and PYTHONPATH
export SPARK_HOME=../spark
export PATH=$SPARK_HOME/bin:$PATH
export PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.4-src.zip:$SPARK_HOME/python/build:$PYTHONPATH

spark-submit --jars mysql-connector-java-5.1.38.jar,spark-streaming-mqtt-assembly_2.11-1.6.3.jar twitter_analysis_worker.py
