spark-submit --packages com.amazonaws:aws-java-sdk:1.7.4,org.apache.hadoop:hadoop-aws:2.7.7 --conf spark.hadoop.fs.s3a.endpoint=s3.us-west-1.amazonaws.com --conf spark.executor.extraJavaOptions=-Dcom.amazonaws.services.s3.enableV4=true --conf spark.driver.extraJavaOptions=-Dcom.amazonaws.services.s3.enableV4=true  --master spark://ec2-3-101-124-56.us-west-1.compute.amazonaws.com:7077 --jars /usr/local/spark/jars/postgresql-42.2.16.jar --driver-class-path /usr/local/spark/jars/postgresql-42.2.16.jar ~/data-processing/read_in.py