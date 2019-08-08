#!/usr/bin/env python
# coding: utf-8

# In[236]:


"""

An example to send data over AWS Kinesis stream
by creating a stream and defining the shards

"""

# Import necessary packages
import boto3
import json
from datetime import datetime
import calendar
import random
import time

# Create a boto3 session and get the current region
session = boto3.session.Session()
region_name = session.region_name

# Create a kinesis client
kinesis = boto3.client('kinesis', region_name=region_name)

stream_name = 'new_stream'
# Create a kinesis stream with the stream name and the number of required shards
stream_create = kinesis.create_stream(StreamName=stream_name, ShardCount=1)
print(stream_create)

# Create a function to put the records into the kinesis stream
def put_to_stream(thing_id, property_value, property_timestamp):
    # Define the data payload
    payload = {
                'prop': str(property_value),
                'timestamp': str(property_timestamp)
              }

    print(payload)
    # Put the record into the stream
    put_response = kinesis_client.put_record(
                        StreamName=stream_name,  # Stream name 
                        Data=json.dumps(payload),   # Serialized payload
                        PartitionKey=thing_id)      # Partition key to determine to be sent to which shard 


while True:
    # Create a random integer value
    property_value = random.randint(40, 120)
    # Get the calendar data
    property_timestamp = calendar.timegm(datetime.utcnow().timetuple())
    # Assign a partition key
    thing_id = 'abc'
    # Put the records into the stream
    put_to_stream(thing_id, property_value, property_timestamp)
    

