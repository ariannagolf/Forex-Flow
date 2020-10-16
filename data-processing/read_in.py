
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql.types import StructField, StringType, IntegerType, FloatType, StructType, DateType, TimestampType
import pyspark.sql.functions as f
from pyspark.sql.window import Window
from datetime import datetime
import time
import config

start_time = time.time()
#----------------------Defining Schemas----------------------#

# Defining static Schema for Forex data
fx_data_schema = [StructField('timestamp', StringType(), True),
    StructField('bid', FloatType(), True),
    StructField('ask', FloatType(), True)]
fx_final_struc = StructType(fields=fx_data_schema)

# Defining static Schema for Interest Rate data
ir_data_schema = [StructField('location', StringType(), True),
    StructField('indicator', StringType(), True),
    StructField('subject', StringType(), True),
    StructField('measure', StringType(), True),
    StructField('frequency', StringType(), True),
    StructField('time', StringType(), True),
    StructField('value', FloatType(), True),
    StructField('flag_codes', StringType(), True)]
ir_final_struc = StructType(fields=ir_data_schema)

#-------------------------------------------------------------------#

def write_to_postgres(df,table,url,mode,properties):
    """ Write dataframe to Postgres """
    try:
        df.write.jdbc(url=url,table = table, mode=mode, properties=properties)
    except:
        pass
    

def daily_values(df,pair):
    """ Aggregate and calculate daily values """
    df = df.groupBy("date").agg(
        f.min("bid").alias("min_bid"),
        f.max("bid").alias("max_bid"),
        f.avg("bid").alias("avg_bid"),
        f.min("ask").alias("min_ask"),
        f.max("ask").alias("max_ask"),
        f.avg("ask").alias("avg_ask"))
    df1 = df.withColumn("pair",f.lit(pair)).select("pair","date","min_bid","max_bid","avg_bid","min_ask","max_ask","avg_ask")
    #df1 = df1.cache()
    #df1 = df1.orderBy("pair","date")
    mode = "append"
    write_to_postgres(df1,config.db_table,url,mode,properties)

def read_fx_csv(path,pair,csv_schema):
    """ Read historical currency data and insert into dataframe"""
    df = spark.read \
        .format("csv") \
        .schema(csv_schema) \
        .load(path) 
        #.repartition(5)
        #.cache()
        #.withColumn("pid", f.spark_partition_id())
    df = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").orderBy('date').cache()
    #df.withColumn("partition_id", f.spark_partition_id()).groupBy("partition_id").count().show()
    daily_values(df,pair)

def read_ir_csv(path,csv_schema):
    """ Read interest data and insert into dataframe"""
    df = spark.read.format("csv") \
        .option("header", True) \
        .schema(csv_schema) \
        .load(path)
    df = df.withColumn('date', f.to_date('time', 'yyyy-MM')).drop("indicator","subject","measure","frequency","flag_codes","time")
    mode = "overwrite"
    #write_to_postgres(df,"ir_data",url,mode,properties)
    #df.show()


if __name__ == '__main__':
    start_time = time.time()
    conf = SparkConf() \
        .set('spark.sql.inMemoryColumnarStorage.compressed', True) \
        .set('spark.sql.files.maxPartitionBytes',268435456) \
        .set('spark.sql.inMemoryColumnarStorage.batchSize', 20000) \
        .set('spark.sql.shuffle.partitions', 12)
    #.set('spark.serializer', 'org.apache.spark.serializer.KryoSerializer')
    #.set("spark.sql.shuffle.partitions",250)
    #.set('spark.sql.shuffle.partitions', 64) \
    #.set('spark.executor.memory', '2400m') \
    #.set('spark.executor.cores', 2)
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")
    
    # start Spark session
    spark = SparkSession \
        .builder \
        .appName("forexflow") \
        .getOrCreate()

    # Postgresql credentials
    mode = "overwrite"
    url = config.db_url
    properties = {
        "user": config.db_user,
        "password": config.db_pass,
        "driver": "org.postgresql.Driver"}

    # Pairs you want to process
    #pairs = ['EURUSD']
    #years = ['2020']
    #months = ['09','10']
    pairs = ['USDPLN']
    years = ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2011','2010']
    months = ['01','02','03','04','05','06','07','08','09','10','11','12']
    #months = ['01']
    # Read in Forex Data
    for pair in pairs:
        for year in years:
            for month in months:
                path = f"s3a://historical-forex-data/DAT_ASCII_{pair}_T_{year}{month}.csv"
                try:
                    read_fx_csv(path,pair,fx_final_struc)
                except:
                    pass

    # Read in Interest Rate Data
    path_ir = f"s3a://historical-forex-data/interest-rate/Interest_Rate.csv"
    read_ir_csv(path_ir,ir_final_struc)

    spark.stop()
    print("--- Runtime took %s seconds ---" % (time.time() - start_time))





