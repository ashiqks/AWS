#!/usr/bin/env python
# coding: utf-8

# In[121]:


'''
An example to connect with AWS DyanmoDB database locally and interact it with table creation, insertion, updation,
reading, deletion operations
'''


# Import necessary packages
import boto3


# Create a boto3 session and retreive the current region 
session = boto3.session.Session()
region_name = session.region_name

# Create a client for dynamodb in the local environment given the downloadable dynamodb is running locally
dynamo_client = boto3.client('dynamodb', region_name=region_name, endpoint_url='http://localhost:8000')

# Create a dynamodb resource in the local environment given the downloadable dynamodb is running locally
dynamo_resource = boto3.resource('dynamodb', region_name=region_name, endpoint_url='http://localhost:8000')

football_column = 'Football_Club'
player_column = 'Player'

# Create a list of attributes to be given to create a table
attr_def = [
            {
                'AttributeName': football_column, # Column name
                'AttributeType': 'S'              # Column type, here it is string
                                },
            {
                'AttributeName': player_column,   # Column name
                'AttributeType': 'S'              # Column type
                                }
]

# Create a list of key schema for the table, here we are creating two primary keys, partition key and sort key
key_schema = [
                {
                    'AttributeName': football_column, # Column name
                    'KeyType': 'HASH'                 # Key type - here it is the partition key, meaning more than one item in the table can have same partition key
                },
                {
                    'AttributeName': player_column,   # Column name
                    'KeyType': 'RANGE'                # Key type - here it is the sort key, meaning this key's value should be unique throughout the table
                }
]

# Create a data for reading and writing capacities per second until it throws throttle exception error
provisioned_throughput = {
                            'ReadCapacityUnits': 25, # Read 25 items per second
                            'WriteCapacityUnits': 25 # Write 25 items per second
}

table_name = 'aws_dynamodb'

# Create the table 
table_response = dynamo_client.create_table(AttributeDefinitions=attr_def, # The attribute definition
                                            KeySchema=key_schema,          # The key schema
                                            ProvisionedThroughput=provisioned_throughput, # The provisioned throughput
                                            TableName=table_name) # Table name


print(table_response)

# Create a table instance from the dyanmodb resource using the table name
table = dynamo_resource.Table(table_name)

# Create a function to put an item to the table
def put(item):
    return table.put_item(Item=item)

# Create an item to be inserted to the table
item_1 = {
            football_column: 'Barcelona', # Partition key column
            player_column: 'Messi'        # Sort key column
}


# Insert the item
put_response = put(item_1)

print(put_response)

item_2 = {
            football_column: 'PSG',
            player_column: 'Neymar'
}

# Insert another item
item_2_response = put(item_2)

# Update an existing item in the table, with update funtion one can create new columns in the existing item
update_respnse = table.update_item(Key={    # The key of the item to be updated
                                            football_column: 'Barcelona',                                        
                                            player_column: 'Messi'
                                       }, # Define the update expression, here it means set the value of no_of_ballondors to a placeholder 'b'
                                   UpdateExpression='set no_of_ballondors = :b', 
                                   ExpressionAttributeValues={':b': 5} # Transfer the value to the placeholder
                                  )

print(update_respnse)

# Get a particular item using the key
get_response = table.get_item(Key={
                                        'Football_Club': 'Barcelona',                                        
                                        'Player': 'Messi'
                                       })

# Delete an item  using its key
delete_item = table.delete_item(Key={
                                        'Football_Club': 'Barcelona',                                        
                                        'Player': 'Messi'
                                       })

# Delete the table using the delete method of the table instance
table_delete = table.delete()

