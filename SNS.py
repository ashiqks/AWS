#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import necessary packages
import boto3
import json


# Create a sns cliet with the region name set
sns = boto3.client('sns', region_name='us-east-2')

TOPIC_NAME = 'First_Topic_SNS'
topic_arn = {}

# Create a sns topic with optinally attributes
def create_topic(topic_name, attr=None):
    # If attributes are not passed in
    if not attr:
        # Create the topic wiht the name given
        response = sns.create_topic(Name=topic_name)
    # If the attributes parameter is given create the topic wiht the given attribues
    else:
        response = sns.create_topic(Name=topic_name, Attributes=attr)
    # Store the topic's arn in a dictionary with the topic name as the key
    topic_arn[topic_name] = response['TopicArn']
    return response


topic_response = create_topic(TOPIC_NAME)

print(topic_response)

print(topic_arn) 

SECOND_TOPIC = 'Second-Topic-SNS'

create_topic(SECOND_TOPIC)

# Get the list of topics associated with sns
topics_list = sns.list_topics()

print(topics_list)

# Get the attributes of the topic
def get_topic_attr(topic_name):
    # Get the topic arn from the dictionary
    topic_name_arn = topic_arn[topic_name]
    # Return the attributes of the topic
    return sns.get_topic_attributes(TopicArn=topic_name_arn)


print(get_topic_attr(SECOND_TOPIC))

# Update a single attribute of a topic
def update_topic_attr(topic_name, attr_name, attr_value):
    # Get the topic arn 
    topic_name_arn = topic_arn[topic_name]
    # Update the attribute of the topic using the given attribute name and value
    sns.set_topic_attributes(TopicArn=topic_name_arn, AttributeName=attr_name, AttributeValue=attr_value)
    
    
# Update the 'DisplayName' attribute of the topic to the value 'First'
update_topic_attr(TOPIC_NAME, 'DisplayName', 'First')



# Create a function to subscribe using email
def email_subscribe(topic_name, email_id):
    # Get the topic arn
    topic_name_arn = topic_arn[topic_name]
    # Subscribe to the topics using the following parameters
    response = sns.subscribe(TopicArn=topic_name_arn, # Topic's arn
                             Protocol='email',        # Protocol, here it is email
                             Endpoint=email_id)       # The subscriber's email id
    return response

# Subscribe to the given topic with the given email
sub_response = email_subscribe(SECOND_TOPIC, 'ashiqgiga07@gmail.com')

print(sub_response)


# Subscribe to the sqs queue
def sqs_subscription(topic_name, sqs_arn):
    # Get the topic arn
    topic_name_arn = topic_arn[topic_name]
    response = sns.subscribe(TopicArn=topic_name_arn, # Topic arn
                             Protocol='sqs',          # The protocol, here it is sqq
                             Endpoint=sqs_arn,        # The arn of the sqs queue
                             Attributes= {'RawMessageDelivery': 'true'}) # Set the attribute 'RawMessageDelivery' to receive the message raw
                                        
    return response
    
    
# Subscribe to a sqs queue with its arn given to a topic
sqs_response = sqs_subscription(SECOND_TOPIC, 'arn:aws:sqs:us-east-2:458375213711:First-Queue')

print(sqs_response)



# Get the subscribers of a topic with an option to filter using the protocol
def get_subscriptions_topic(topic_name, filter_by=None):
    # Get the topic arn
    topic_name_arn = topic_arn[topic_name]
    # Make an empty list to hold the subscribers
    sub_list = []
    # If fitlering by protocol is enabled
    if filter_by:
        # List all the subscriptions 
        response = sns.list_subscriptions_by_topic(TopicArn=topic_name_arn)['Subscriptions']
        # Loop over all the subscriptions
        for res in response:
            # Select only subscriptions that match the specified protocol
            if filter_by == res['Protocol']:
                sub_list.append(res)
    # If filtering is not enabled
    else:
        # Receive all the subscriptions
        response = sns.list_subscriptions_by_topic(TopicArn=topic_name_arn)['Subscriptions']
        # Loop over all the subscriptions and append it to the list
        for res in response:
            sub_list.append(res)
    return sub_list


# List all the subscriptions to the given topic
list_sub_topic = get_subscriptions_topic(SECOND_TOPIC)

print(list_sub_topic)

# Filter the subscriptions by the protocol sqs
filtered_sub_topic = get_subscriptions_topic(SECOND_TOPIC, 'sqs')



print(filtered_sub_topic)


# Publish messages to a topic
def publish_msg(topic_name, msg):
    # Get the topic arn
    topic_name_arn = topic_arn[topic_name]
    # Publish the message using
    return sns.publish(TopicArn=topic_name_arn, # Topic arn
                       Message=msg)             # The message

# Publish message to the given topic
publish_msg(SECOND_TOPIC, msg='Message to all the subscribers')


# Unsubscribe from the topic for a subsciber
def opt_out(topic_name, subscriber):
    # Get the topic name
    topic_name_arn = topic_arn[topic_name]
    # Get all the subcribers of the topic
    subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_name_arn)['Subscriptions']
    # Loop over all the subscriptions
    for sub in subscriptions:
        # If the subscriber has really subsribed to the given topic
        if subscriber == sub['Endpoint']:
            # Get the subscription arn
            sub_arn = sub['SubscriptionArn']
            # Unubscribe from the topic using the subsriber's arn
            sns.unsubscribe(SubscriptionArn = sub_arn)
            

# Let the sqs queue opt out from its subscribed topic
opt_out(SECOND_TOPIC, 'arn:aws:sqs:us-east-2:458375213711:First-Queue')

# Let the email opt out from its subscribed topic
opt_out(SECOND_TOPIC, 'ashiqgiga07@gmail.com')


# Delete the topic
def delete_topic(topic_name):
    # Get the topic arn
    topic_name_arn = topic_arn[topic_name]
    # Delete the topic using the topic's arn
    sns.delete_topic(TopicArn=topic_name_arn)
    
delete_topic(TOPIC_NAME)

