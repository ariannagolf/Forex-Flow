
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
mode = "overwrite"
url = "jdbc:postgresql://***/fx_db"
properties = {
    "user": "***",
    "password": "***",
    "driver": "org.postgresql.Driver"}

# Defining scheme
data_schema = [StructField('timestamp', StringType(), True),
    StructField('bid', FloatType(), True),
    StructField('ask', FloatType(), True)]
final_struc = StructType(fields=data_schema)

def write_to_postgres(df,url,mode,properties):
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
    mode = "overwrite"
    url = "jdbc:postgresql://***:5431/fx_db"
    properties = {
        "user": "***",
        "password": "***",
        "driver": "org.postgresql.Driver"}
    write_to_postgres(df1,url,mode,properties)

def read_csv(path,pair):
    df = spark.read.csv(path,schema=final_struc)
    df = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").orderBy('date')
    #df.show()
    daily_values(df,pair)

#pairs = ['GBPUSD',"NZDUSD","AUDUSD","USDCAD","USDCHF","USDJPY"]
pairs = ['GBPUSD']
years = ['2020']
#months = ['01','02','03','04','05','06','07','08']
months = ['01']

for pair in pairs:
    for year in years:
        for month in months:
            path = f"s3a://historical-forex-data/DAT_ASCII_{pair}_T_{year}{month}.csv"
            #path = "s3a:///historical-forex-data/"
            read_csv(path,pair)
spark.stop()
print("--- %s seconds ---" % (time.time() - start_time))



