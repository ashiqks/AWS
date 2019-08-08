#!/usr/bin/env python
# coding: utf-8

# In[5]:


"""

An example to demonstrate how to receive data from
AWS Kinesis streams sent by a stream producer and processing
of the data

"""


# Import necessary packages
import boto3
import json
from datetime import datetime
import time

# Create a boto3 session and get the region name
session = boto3.session.Session()
region_name = session.region_name

# Create a kinesis client
kinesis_client = boto3.client('kinesis', region_name=region_name)

stream_name = 'new_stream'

# Get the details of streams defined in the aws account
response = kinesis_client.describe_stream(StreamName=stream_name)

# Get the shard id of the shard from which we receive the data 
my_shard_id = response['StreamDescription']['Shards'][0]['ShardId']

# Get the shard iterator response 
shard_iterator = kinesis_client.get_shard_iterator(StreamName=stream_name, # Stream name
                                                      ShardId=my_shard_id, # Shard id
                                                      ShardIteratorType='LATEST') # Iterator type, here it is the latest records

# Get the shard iterator to point to the records
my_shard_iterator = shard_iterator['ShardIterator']

# Get the records response from the stream
record_response = kinesis_client.get_records(ShardIterator=my_shard_iterator,
                                              Limit=2)

# Loop over untill 'NextShardIterator' is available
while 'NextShardIterator' in record_response:
    # Get the records continuously from the stream
    record_response = kinesis_client.get_records(ShardIterator=record_response['NextShardIterator'],
                                                  Limit=2)
    print(record_response)


# In[ ]:




