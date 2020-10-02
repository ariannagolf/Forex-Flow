
from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StringType, IntegerType, FloatType, StructType, DateType, TimestampType
import pyspark.sql.functions as f
from pyspark.sql.window import Window
from datetime import datetime

spark = SparkSession \
        .builder \
        .appName("forex") \
        .getOrCreate()

# Postgresql credentials
mode = "overwrite"
url = "jdbc:postgresql://****:5431/***"
properties = {"user": "***","password": "***","driver": "org.postgresql.Driver"}

# Defining scheme
data_schema = [StructField('timestamp', StringType(), True),
              StructField('bid', FloatType(), True),
              StructField('ask', FloatType(), True)]
final_struc = StructType(fields=data_schema)

def write_to_postgres(df,url,mode,properties):
        df.write.jdbc(url=url,table = "historical_data", mode=mode, properties=properties)

def daily_values(df):
        #Group dates and calculate mean
        #df_max = df.groupBy("date").max("bid")
        #df_min = df.groupBy("date").min("bid")
        #df_avg = df.groupBy("date").mean("bid")
        df = df.groupBy("date") \
    .agg(f.min("bid").alias("min_bid"), \
         f.max("bid").alias("max_bid"), \
         f.avg("bid").alias("avg_bid") \
     ) \
        # Partition by a window and calculate difference
        #price_window = Window.partitionBy("date").orderBy("date")
        #df = df.withColumn("prev_value", f.lag(col).over(price_window))
        #df = df.withColumn("diff", f.when(f.isnull(col - df.prev_value), 0).otherwise(col - df.prev_value))
        df.show()
        #df_min.show()
        #df_avg.show()

def read_csv(path):
        df = spark.read.csv(path,schema=final_struc)
        df1 = df.withColumn('date', f.to_date('timestamp', 'yyyyMMdd')).drop("timestamp").select("date","bid","ask")
        #df2 = df.withColumn("date", df.timestamp.substr(1,8)).drop("timestamp").select("date","bid","ask")
        daily_values(df1)


pairs = ['GBPUSD']
years = ['2020']
#months = ['01','02','03','04','05','06','07','08']
months = ['01']

for pair in pairs:
        for year in years:
                for month in months:
                        path = f"s3a://historical-forex-data/DAT_ASCII_{pair}_T_{year}{month}.csv"
                        read_csv(path)


