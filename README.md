# Currency-Flow

Monitering Money Movement.

[Currency Flow Slides](https://docs.google.com/presentation/d/1CGO0-aTaNrPxvtQt1upfs92xHOfhBJdkzWmq1ynoBG4/edit?usp=sharing), 
[Recorded Demo](), and [Dashboard](http://ec2-54-193-31-247.us-west-1.compute.amazonaws.com:8050/)

## Introduction
The foreign exchange market, also called the forex market is the largest financial market in the world. Over 6 trillion in US dollars are traded every day. 95% of currency trades are conducted by institutional investors like central banks, governments, and multinational corporations. 

The currency market is crucial to multinational corporations who want to protect themselves from the risk associated with foreign currency transactions. When creating long term business and investment strategies, it is important for these corporations to keep track of not just currency prices, but also changes in interest rates since there is a strong relationship between the two. However, most forex trading platforms do not provide easy access to interest rate data. 

The goal of this pipeline is to synthesize data that may help corporate researchers and analysts determine how forex price action responds to global event. To do so, it aggregates historical forex data and interest rates to get a snapshot of the underlying movement of capital between economies.

## Architecture
![Test Image 8](https://raw.githubusercontent.com/ariannagolf/Forex-Flow/master/architecture.png)

## Dataset
Historical currency data starting from 2000 is available through [histdata.com](https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/). Some currency pairs have more data then others. The data is available in a variety of formats but the data used for this project are ascii tick data. Interest rate data since 1956 is available from [OECD](https://data.oecd.org/interest/short-term-interest-rates.htm).

## Engineering challenges
I tested and tuned various methods and configurations to optimize the Spark aspect of the pipeline. 

The first effective method I found was pre-defining a static schema and utilizing Spark functions as opposed to UDF wrappers. This reduced runtime by 8%. This makes sense since pre-defining a static schema reduces job time as schema inference requires Spark to physically inspect some of the data coming in which requires a job of its own. Likewise, UDF’s slow down runtime because they require data to be copied from the executor and back while spark functions optimize for this. 

Repartitioning and caching dataframes before running Spark SQL queries brought run-time down to 8 minutes. Also tuning partition parameters led further decreased job time. And this resulted in a total 34% reduction compared to baseline. 

Another challenge that I tackled was improving database query speeds for my UI. I improved query speeds by creating an index for lookups and list partitioning tables by currency pair which reduced look up time from 3.23 to 1.2 seconds.

## How to install and get it up and running
This project was built using an Apache Spark 2.4.7 / Hadoop 2.7 binary downloaded from spark.apache.org. It reads from AWS S3 and writes to PostgreSQL, so a driver from jdbc.postgresql.org should added in spark/jars/ and configurations should be added to spark-defaults.conf.

Use run.sh to read in and process data for this application. The frontend runs in Python 3 with Dash.
