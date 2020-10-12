# Currency-Flow

Monitering Money Movement.

[Currency Flow Slides](https://docs.google.com/presentation/d/1CGO0-aTaNrPxvtQt1upfs92xHOfhBJdkzWmq1ynoBG4/edit?usp=sharing) to your presentation.
[Recorded Demo]()

## Introduction
The foreign exchange market, also called the forex market is the largest financial market in the world. Over 6 trillion in US dollars are traded every day. 95% of currency trades are conducted by institutional investors like central banks, governments, and multinational corporations. 

The currency market is crucial to multinational corporations who want to protect themselves from the risk associated with foreign currency transactions. When creating long term business and investment strategies, it is important for these corporations to keep track of not just currency prices, but also changes in interest rates since there is a strong relationship between the two. However, most forex trading platforms do not provide easy access to interest rate data. 

The goal of this pipeline is to synthesize data that may help corporate researchers and analysts determine how forex price action responds to global event. To do so, it aggregates historical forex data and interest rates to get a snapshot of the underlying movement of capital between economies.

## Architecture
![Test Image 8](https://raw.githubusercontent.com/ariannagolf/Forex-Flow/master/architecture.png)

## Dataset
Historical currency data starting from 2000 is available through [histdata.com](https://www.histdata.com/download-free-forex-historical-data/?/ascii/tick-data-quotes/). Some currency pairs have more data then others. The data is available in a variety of formats but the data used for this project are ascii tick data. Interest rate data since 1956 is available from [OECD](https://data.oecd.org/interest/short-term-interest-rates.htm).

## Engineering challenges

## Trade-offs

<hr/>
## How to install and get it up and running
This project was built using an Apache Spark 2.4.7 / Hadoop 2.7 binary downloaded from spark.apache.org. It reads from AWS S3 and writes to PostgreSQL, so a driver from jdbc.postgresql.org should added in spark/jars/ and configurations should be added to spark-defaults.conf.

Use run.sh to read in and process data for this application. The frontend runs in Python 3 with Dash.
<hr/>
