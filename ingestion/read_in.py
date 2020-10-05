
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StringType, IntegerType, FloatType, StructType, DateType, TimestampType
import pyspark.sql.functions as f
from pyspark.sql.window import Window
from datetime import datetime
import time
start_time = time.time()

spark = SparkSession \
    .builder \
    .appName("forex") \
    .getOrCreate()

# Postgresql credentials
mode = "append"
url = "jdbc:postgresql://***/fx_db"
properties = {
    "user": "**",
    "password": "**",
    "driver": "org.postgresql.Driver"}

#-------------------------Defining Schemas-------------------------#

# Defining Schema for Forex data
fx_data_schema = [StructField('timestamp', StringType(), True),
    StructField('bid', FloatType(), True),
    StructField('ask', FloatType(), True)]
fx_final_struc = StructType(fields=fx_data_schema)

# Defining Schema for Interest Rate data
ir_data_schema = [StructField('location', StringType(), True),
    StructField('time', StringType(), True),
    StructField('value', FloatType(), True)]
ir_final_struc = StructType(fields=ir_data_schema)

# Defining Schema for GDP data
gdp_data_schema = [StructField('location', StringType(), True),
    StructField('time', StringType(), True),
    StructField('value', FloatType(), True)]
gdp_final_struc = StructType(fields=ir_data_schema)

#-------------------------------------------------------------------#

def write_fx_to_postgres(df,url,mode,properties):
    df.write.jdbc(url=url,table = "fx_data", mode=mode, properties=properties)

def daily_values(df,pair):
    df = df.groupBy("date").agg(
        f.min("bid").alias("min_bid"),
        f.max("bid").alias("max_bid"),
        f.avg("bid").alias("avg_bid"),
        f.min("ask").alias("min_ask"),
        f.max("ask").alias("max_ask"),
        f.avg("ask").alias("avg_ask"))
    df1 = df.withColumn("pair",f.lit(pair)).select("pair","date","min_bid","max_bid","avg_bid","min_ask","max_ask","avg_ask")
    #df1.show()
    # Postgresql credentials
    mode = "append"
    url = "jdbc:postgresql://***/fx_db"
    properties = {
        "user": "***",
        "password": "***",
        "driver": "org.postgresql.Driver"}
    write_fx_to_postgres(df1,url,mode,properties)

def read_fx_csv(path,pair,csv_schema):
    df = spark.read.csv(path,schema=csv_schema)
    df = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").orderBy('date')
    #df.show()
    daily_values(df,pair)

def read_fx_csv(path,pair,csv_schema):
    df = spark.read.csv(path,schema=csv_schema)
    df = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").orderBy('date')
    #df.show()
    daily_values(df,pair)

#pairs = ['GBPUSD',"NZDUSD","AUDUSD","USDCAD","USDCHF","USDJPY"]
pairs = ['USDJPY']
years = ['2020']
#months = ['01','02','03','04','05','06','07']
months = ['05','06']

for pair in pairs:
    for year in years:
        for month in months:
            path = f"s3a://historical-forex-data/DAT_ASCII_{pair}_T_{year}{month}.csv"
            #path = "s3a:///historical-forex-data/"
            read_fx_csv(path,pair,fx_final_struc)
path_gdp = f"s3a://historical-forex-data/GDP/GDP.csv"
read_fx_csv(path_ir,fx_final_struc)
path_ir = f"s3a://historical-forex-data/interest-rate/Interest_Rate.csv"
read_fx_csv(path_ir,fx_final_struc)

spark.stop()
print("--- %s seconds ---" % (time.time() - start_time))



