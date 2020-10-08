
from pyspark.sql import SparkSession
from pyspark import SparkConf
from pyspark import SparkContext
from pyspark.sql.types import StructField, StringType, IntegerType, FloatType, StructType, DateType, TimestampType
import pyspark.sql.functions as f
from pyspark.sql.window import Window
from datetime import datetime
import time
start_time = time.time()

conf = SparkConf() \
    .set('spark.serializer', 'org.apache.spark.serializer.KryoSerializer')
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
url = "jdbc:postgresql://***/fx_db"
properties = {
    "user": "***",
    "password": "***",
    "driver": "org.postgresql.Driver"}

#-------------------------Defining Schemas-------------------------#

# Defining Schema for Forex data
fx_data_schema = [StructField('timestamp', StringType(), True),
    StructField('bid', FloatType(), True),
    StructField('ask', FloatType(), True)]
fx_final_struc = StructType(fields=fx_data_schema)

# Defining Schema for Interest Rate data
ir_data_schema = [StructField('location', StringType(), True),
    StructField('indicator', StringType(), True),
    StructField('subject', StringType(), True),
    StructField('measure', StringType(), True),
    StructField('frequency', StringType(), True),
    StructField('time', StringType(), True),
    StructField('value', FloatType(), True),
    StructField('flag_codes', StringType(), True)]
ir_final_struc = StructType(fields=ir_data_schema)

# Defining Schema for GDP data
gdp_data_schema = [StructField('location', StringType(), True),
    StructField('indicator', StringType(), True),
    StructField('subject', StringType(), True),
    StructField('measure', StringType(), True),
    StructField('frequency', StringType(), True),
    StructField('time', StringType(), True),
    StructField('value', FloatType(), True),
    StructField('flag_codes', StringType(), True)]
gdp_final_struc = StructType(fields=ir_data_schema)

#-------------------------------------------------------------------#

def write_to_postgres(df,table,url,mode,properties):
    df.write.jdbc(url=url,table = table, mode=mode, properties=properties)

def daily_values(df,pair):
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
    #df1.show()
    # Postgresql credentials
    mode = "append"
    write_to_postgres(df1,"fx_data",url,mode,properties)

def read_fx_csv(path,pair,csv_schema):
    #df = spark.read.csv(path,schema=csv_schema)
    df = spark.read \
        .format("csv") \
        .schema(csv_schema) \
        .load(path) \
        .repartition(15) \
        #.withColumn("pid", f.spark_partition_id())
    df = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").orderBy('date')
    #df.withColumn("partition_id", f.spark_partition_id()).groupBy("partition_id").count().show()
    daily_values(df,pair)

def read_ir_csv(path,csv_schema):
    df = spark.read.format("csv") \
        .option("header", True) \
        .schema(csv_schema) \
        .load(path)
    df = df.withColumn('date', f.to_date('time', 'yyyy-MM')).drop("indicator","subject","measure","frequency","flag_codes","time")
    mode = "overwrite"
    #write_to_postgres(df,"ir_data",url,mode,properties)
    #df.show()


pairs = ['USDJPY']
#years = ['2019','2018','2017','2016','2015','2014','2013','2012','2011','2010']
years = ['2019','2018','2017','2016','2015','2014','2013','2012']
months = ['01','02','03','04','05','06','07','08','09','10','11','12']

# Read in Forex Data
for pair in pairs:
    for year in years:
        for month in months:
            path = f"s3a://historical-forex-data/DAT_ASCII_{pair}_T_{year}{month}.csv"
            read_fx_csv(path,pair,fx_final_struc)

# Read in Interest Rate Data
path_ir = f"s3a://historical-forex-data/interest-rate/Interest_Rate.csv"
read_ir_csv(path_ir,ir_final_struc)

# Read in GDP Data
#path_gdp = f"s3a://historical-forex-data/GDP/GDP.csv"
#read_gdp_csv(path_gdp,gdp_final_struc)


spark.stop()
print("--- %s seconds ---" % (time.time() - start_time))









