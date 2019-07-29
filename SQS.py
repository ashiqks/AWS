#!/usr/bin/env python
# coding: utf-8

# In[89]:

'''

A tutorial to demonstrate AWS SQS.

Following are the actions done in the example

- Creating standard and fifo queues
- Attaching dead queue letters for both standard and fifo queues
- List all the queues available
- Update the queue attributes
- Add permissions to the SQS service
- Sending messages and also by batches
- Receiving and deleting the messages
- Deleting the queues

'''

# Import the necessary packages
import boto3
import json
from uuid import uuid4


# Create a sqs client object with the region name set
sqs = boto3.client('sqs', region_name='us-east-2')


QUEUE_NAME = 'First-Queue'
# Create a standard sqs queue
sqs_queue = sqs.create_queue(QueueName=QUEUE_NAME)

print(sqs_queue)


# Get the url for the standard queue
QUEUE_URL = sqs_queue['QueueUrl']

# Naming convention for the sqs fifo queue states that the name should end with '.fifo'
FIFO_QUEUE = 'First-FIFO-Queue.fifo'

# Create a sqs fifo queue with the attribute value 'FifoQueue' set to make it fifo
fifo_queue = sqs.create_queue(QueueName=FIFO_QUEUE, Attributes={
                                                                    'FifoQueue': 'true'
                                                                })

print(fifo_queue)

# Get the fifo queue url
fifo_url = fifo_queue['QueueUrl']

print(response)


# Define a function to get the attributes of the queue
def get_queue_attr(queue_name, *args):
    attr_list = []
    for arg in args:
        attr_list.append(arg)
    # Find the queue url using the queue name on the function 'get_queue_url'
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    # Get the attributes of the queue using the queue url and passing to the list of wanted queue attributes 
    queue_attr = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=attr_list)
    return queue_attr


# Get the queue arn attribute of the fifo queue using the custom function
fifo_queue_attr = get_queue_attr(FIFO_QUEUE, 'QueueArn')
print(fifo_queue_attr)


# Function to create a standard or fifo queue along with a dead letter queue associated with it
def queue_with_optional_dead_letter(queue_name, dead_letter=None, fifo=False):
    # Variable to determine whether a dead letter queue is needed
    dead_letter_required = False
    # If the dead letter queue is needed   
    if dead_letter:
        # Set the variable dead_letter_required to true
        dead_letter_required = True
        # Get the dead letter queue's arn 
        dead_letter_arn = get_queue_attr(dead_letter, 'QueueArn')['Attributes']['QueueArn']
        # Define the redrive policy attribute to passed to the 'create_queue' function
        redrive_policy = {
            'deadLetterTargetArn': dead_letter_arn, # Make this url as the dead letter queue for the queue to created
            'maxReceiveCount': 5                    # The no. of times a message is delivered to the source queue for moving to dead letter queue
        }
    # If both dead letter queue is and the queue has to be fifo
    if dead_letter_required and fifo:
        # Create the queue with the redrive policy attributes and and the attribute to make it fifo
        queue = sqs.create_queue(QueueName=queue_name, Attributes={'FifoQueue': 'true', 'RedrivePolicy': json.dumps(redrive_policy)})
    # If the dead letter queue is required but not a fifo queue
    elif dead_letter_required and not fifo:
        queue = sqs.create_queue(QueueName=queue_name, Attributes={'RedrivePolicy': json.dumps(redrive_policy)})
    # A dead letter queue is not required but it has to be fifo
    elif not dead_letter_required and fifo:
        queue = sqs.create_queue(QueueName=queue_name, Attributes={'FifoQueue': 'true'})
    # Neither dead letter queue required nor is fifo
    else:
        queue = sqs.create_queue(QueueName=queue_name)
    return queue


# Create a standard queue with a dead letter queue associated with it
queue_with_dead_letter = queue_with_optional_dead_letter('Queue_and_dead', dead_letter=QUEUE_NAME)

print(queue_with_dead_letter)

# Create  a fifo queue with a dead letter queue associate with it
fifo_queue_dead_letter = queue_with_optional_dead_letter('Fifo_and_dead_letter.fifo', dead_letter=FIFO_QUEUE, fifo=True)

print(fifo_queue_dead_letter)


# Create a function to list all the queues with an option to filter out the queue by  a prefix
def list_queue(prefix=None):
    # Checking if the prefix is the type of string
    if isinstance(prefix, str):
        # List all the queue with the same prefix
        queue = sqs.list_queues(QueueNamePrefix=prefix)
    else:
        # List all the queues 
        queue = sqs.list_queues()
    return queue


# List all the queues with the prefix
queue = list_queue('First')
print(queue)

# List all the queues
all_queues = list_queue()
print(all_queues)


# Define a function to update the attributes of the queue by passing in the attributes keys and values in separate lists
def update_queue_attr(queue_name, key_list, value_list):
    # Create a dictionary with the attribute keys and values
    attr_dict = dict(zip(key_list, value_list))
    # Get the url of the queue
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    # Update the attributes by passing in the attriubtes dictionary
    update_response = sqs.set_queue_attributes(QueueUrl=queue_url, Attributes=attr_dict)
    return update_response


# Update the values of the 'DelaySeconds' and 'MaximumMessageSize' to 10 and 30000 respectively
update_response = update_queue_attr(QUEUE_NAME, ['DelaySeconds', 'MaximumMessageSize'], ['10', '30000'])
print(update_response)


# Function to retreive the url of the queue using the queue name
def queue_name_to_url(queue_name):
    queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
    return queue_url

# Adding permission for sqs to send and receive messages
add_permission_response = sqs.add_permission(QueueUrl=queue_name_to_url(QUEUE_NAME), # Queue Url
                                             Label='AddPermissionForAll,   # Unique string Id
                                             AWSAccounIds=['*'],           # All the users 
                                             Actions=['*'])                # All the actions
  
  
# Function to send message to the sqs queue
def send_msg(queue_name, msg, message_group_id=None, fifo=False): 
    # Get the url of the queue
    queue_url = queue_name_to_url(queue_name)
    # If message has to be sent to a standard queue
    if not fifo:
        # Send the message using the queue url and pass in the message to the 'MessageBody' parameter
        send_response = sqs.send_message(QueueUrl=queue_url, MessageBody=msg)
    else:
        # If the message is to be sent to a fifo queue
        send_response = sqs.send_message(QueueUrl=queue_url, # Queue url
                                         MessageBody=msg,    # Message
                                         MessageGroupId=message_group_id,     # Group id of the message in string format
                                         MessageDeduplicationId=str(uuid4())) # A random unique message deduplication id as string 
    return send_response


# Send a message to the standard queue
msg_to_std = send_msg(QUEUE_NAME, 'Message to the standard queue')


# Send message to fifo queue with message group id as an argument
msg_to_fifo = send_msg(FIFO_QUEUE, 'Message to the fifo queue', message_group_id='fifo_1', fifo=True)


# Message to send a batch of messages
def send_msg_batch(queue_name, msg_list, msg_group_id=None, fifo=False):
    # Get the url of the queue using the queue name
    queue_url = queue_name_to_url(queue_name)
    # Create an empty list to hold the value for 'Entries' parameter for each message 
    msg_dict_list = []
    
    # If the message is to fifo queue
    if fifo:
        for msg in msg_list:
            # Do this for each message
            msg_dict_list.append(
                             {
                                  'Id': str(uuid4()),  # A unique for each message
                                  'MessageBody': msg,  # The message
                                  'MessageGroupId': msg_group_id,        # Message group id
                                  'MessageDeduplicationId': str(uuid4()) # Message deduplication id
                                       
                             }
                    )
    
    # If the message is to a standard queue
    else:
        for msg in msg_list:
            msg_dict_list.append({
                'Id': str(uuid4()), # Unique message id
                'MessageBody': msg  # Message
            })
    # Send the messagses as batch using the queue url and the entries list
    send_response = sqs.send_message_batch(QueueUrl=queue_url, Entries=msg_dict_list)
    return send_response
            
    
# Hold the messages in a list
msg_list = ['First msg', 'Second msg', 'Third msg', 'Fourth msg', 'Fifth msg', 'Sixth msg']


# Send the batch of messages to a fifo queue
batch_msg_to_fifo = send_msg_batch(FIFO_QUEUE, msg_list, msg_group_id='fifo_msg', fifo=True)


# Function to receive messages from a sqs queue
def receive_msg(queue_name, max_msg=5, delete=False):
    # Get the queue url
    queue_url = queue_name_to_url(queue_name)
    # Variable to check if the queue is intially empty or not 
    is_msg = False
    while True:
        # Receive messages continuously from the queue and set the number of messages it can receive at a time 
        messages = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=max_msg)
        # If there are messages in queue by checking the response
        if 'Messages' in messages:
            # Retreive the message
            for msg in messages['Messages']:
                # Set the varible to check if queue is initially empty, here queue is not empty
                is_msg = True
                print(msg['Body'])
                # If delete flas is set, delete the message from queue using the queue url and the receipt handle
                if delete:
                    sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=msg['ReceiptHandle'])
            
        else:
            # After all messages are read
            if is_msg:
                print('Reading completed ')
            # If the queue was empty initially
            else:
                print('Queue is empty')
            # Break from the while loop
            break
            
            
# Receive the messages stored in the queue
received_msg_std = receive_msg(QUEUE_NAME)


# Receive the messages stored in the fifo queue
received_msg_fifo = receive_msg(FIFO_QUEUE)


# Function to delete multiple queues
def delete_queues(*args):
    q_list = []
    for arg in args:
        q_list.append(arg)
    queue_url_list = []
    for q in q_list:
        # Get the urls of the queues to be deleted
        queue_url_list.append(sqs.get_queue_url(QueueName=q)['QueueUrl'])
    for queue in queue_url_list:
        # Delete the queues one by one
        sqs.delete_queue(QueueUrl=queue)
        
# Delete the two queues given as the arguments 
delete_queues(QUEUE_NAME, FIFO_QUEUE)

