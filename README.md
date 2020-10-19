# Currency-Flow

Monitering Money Movement.

[Slidedeck](https://docs.google.com/presentation/d/1CGO0-aTaNrPxvtQt1upfs92xHOfhBJdkzWmq1ynoBG4/edit?usp=sharing), 
[Dashboard Demo](https://youtu.be/21LVI_MPG7M), and [Dashboard](https://currencyflow.datatesting.me/)

## Table of Contents
1. [Introduction](README.md#introduction)
2. [Architecture](README.md#architecture)
3. [Dataset](README.md#dataset)
4. [Engineering Challenges](README.md#engineering-challenges)
5. [Processing](README.md#processing)
6. [Setup](README.md#setup)

## Introduction
The foreign exchange market (also known as the forex market) is the largest financial market in the world. Over 6 trillion in US dollars are traded every day. 

The currency market is crucial to multinational corporations who want to protect themselves from the risk associated with foreign currency transactions. When creating long term business and investment strategies, it is important for these corporations to keep track of not just currency prices, but also changes in interest rates since there is a strong relationship between the two. However, most forex trading platforms do not provide easy access to interest rate data. 

Currency Flow is a data platform that synthesizes data that helps corporate researchers and analysts determine how forex price action responds to a global event. To do so, it aggregates historical forex data and interest rates for a chosen timeframe to get a snapshot of the underlying movement of capital between economies. Currency Flow leverages Airflow to regularly update currency and interest rate data to provide timely data for recalculating percent changes in currency prices. 

Note: Currency Flow processes ~200GB of raw Forex data for the period January 2010 to October 2020. 

## Architecture
![Test Image 8](https://raw.githubusercontent.com/ariannagolf/Forex-Flow/master/architecture.png)

## Dataset
Historical currency data starting from 2000 is available through [histdata.com](https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/). Some currency pairs have more data then others. The data is available in a variety of formats but the data used for this project are ascii tick data. Interest rate data since 1956 is available from [OECD](https://data.oecd.org/interest/short-term-interest-rates.htm).

## Engineering Challenges
I tested and tuned various methods and configurations to optimize the Spark aspect of the pipeline. The first effective method I found was pre-defining a static schema and utilizing Spark functions as opposed to UDF wrappers. Repartitioning and caching dataframes before running Spark SQL queries brought run-time down to 8 minutes. Also tuning partition parameters led to further decreased job time. And this resulted in a total 34% reduction compared to baseline. 

Another challenge I tackled was improving database query speeds for my UI. I improved query speeds by creating an index for lookups and list partitioning tables by currency pair which reduced look up time from 3.23 to 1.2 seconds.

## Processing
In the Data Processing folder you will find the currency_pairs.csv file which lists the currency pair options. The read_in.py script reads currency trade csv files to Spark dataframes for each month of the specified date range and does the following:

Filters dataframes based on specified conditions and returns certain fields
Writes the DataFrame to a Postgres table (table creation is not included in this script) with the following schemas:

Forex Data Schema
```
|-- pair      (string),
|-- date      (date),
|-- min_bid   (float),
|-- max_bid   (float),
|-- avg_bid   (double),
|-- min_ask   (float),
|-- max_ask   (float),
|-- avg_ask   (double)
```
Interest Rate Data Schema
```
|-- location  (string),
|-- time      (date),
|-- value     (float)
```

## Setup
This project was built using an Apache Spark 2.4.7 / Hadoop 2.7 binary downloaded from spark.apache.org. It reads from AWS S3 and writes to PostgreSQL, so a driver from jdbc.postgresql.org should added in spark/jars/ and configurations should be added to spark-defaults.conf. The frontend runs in Python 3 with Dash.
#### Data Ingestion
For data ingestion, run the data_upload.py script. Specify the date range you are interested in and the destination. The script performs the following tasks:
- Downloads compressed trade files for each month in the specified date range.
- Unzips the files (.zip -> .csv)
- Stores monthly csv files to specified S3 bucket
#### Processing
I set up 1 master node and 2 workers which are m5.large EC2 instances (18.04 Ubuntu,2 vCPUs, 8GB). Setup Spark 2.4.7 using these [instructions](https://blog.insightdatascience.com/simply-install-spark-cluster-mode-341843a52b88). Use run.sh to read in and process data for this application.
#### Airflow
