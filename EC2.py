#!/usr/bin/env python
# coding: utf-8

# In[68]:


# Import the necessary packages
import boto3
# Import all the objects from the VPC module so that we can use the existing vpc attributes to create the ec2 instances
from VPC import *


# In[57]:


key_name = 'secret_key_vpc_ec2_1'
# Create a secret key pair with the key name as the parameter using the ec2 client loaded from the vpc module
key_pair = ec2_client.create_key_pair(KeyName=key_name)


# In[28]:


print(key_pair)


# In[59]:


description = 'Security group for public subnet'
group_name = 'Security Group VPC EC2 1'
# Create a security group with the parameters group name, description and the vpc id
security_group = ec2_client.create_security_group(Description=description, GroupName=group_name, VpcId=vpc_id)


# In[60]:


print(security_group)


# In[61]:


# Get the security group id
security_group_id = security_group['GroupId']


# In[62]:


# Define an http rule by the allowing traffic on the port number 80 for tcp protocol for all ip addresses 
http_rule = {'FromPort': 80,
             'IpProtocol': 'tcp',
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
             'ToPort': 80}

# Define an ssh rule by allowing traffic on the port number 22 for tcp protocol for all ip addresses
ssh_rule = {'FromPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
            'ToPort': 22}

# Define an outbound traffic rule for the securtiy group with the above rules
outbound_response = ec2_client.authorize_security_group_egress(GroupId=security_group_id,
                                                               IpPermissions=[http_rule, ssh_rule])


# In[63]:


print(outbound_response)


# In[64]:


# Like outbound rule create the same rule for inbound traffic for an example
inbound_response = ec2_client.authorize_security_group_ingress(GroupId=security_group_id,
                                                               IpPermissions=[http_rule, ssh_rule])


# In[65]:


print(inbound_response)


# In[66]:


# Create a bash script to be passed on the ec2 instances upon being launced to launch a web server
data = """#!/bin/bash
          yum update -y
          yum install -y httpd24
          service httpd start
          chkconfig httpd on
          echo "<html><body><h1>Boto3 - Python SDK for AWS</h1></body></html>" > /var/www/html/index.html"""


# In[ ]:


image_id = 'ami-02f706d959cedf892'


# In[67]:


# Create an ec2 instance on the public subnet with the following parameters
public_ec2_instance = ec2_client.run_instances(
                            ImageId=image_id, # Image id of the ec2 instance
                            KeyName=key_name, # Security keypair's key name
                            MinCount=1,       # Minimum number of instances to be launched
                            MaxCount=1,       # Maximum number of instances to be launched
                            InstanceType='t2.micro', # The type of the instance
                            SecurityGroupIds=[security_group_id], # List of the security groups
                            SubnetId=public_subnet_id, # Subnet of which the ec2 instance to be launched on
                            UserData=data) # The bash script


# In[ ]:


# Create an ec2 instance on the private subnet with the following parameters
# Note we are not launching the web server from the ec2 instance because the private ec2 is not accessible from the outside world
private_ec2_instance = ec2_client.run_instances(
                            ImageId=image_id, # Image id of the ec2 instance
                            KeyName=key_name, # Security keypair's key name
                            MinCount=1,       # Minimum number of instances to be launched
                            MaxCount=1,       # Maximum number of instances to be launched
                            InstanceType='t2.micro', # The type of the instance
                            SecurityGroupIds=[security_group_id], # List of the security groups
                            SubnetId=private_subnet_id) # Subnet id of which the ec2 isntance to be launched on
 


# In[ ]:


# Define a function to stop the running instances by passing on the list of instance id of instances to be stoped
def stop_ec2_instances(*args):
    instances_list = []
    for arg in args:
        instances_list.append(arg)
    ec2_client.stop_instances(InstanceIds=instances_list)

# Stop both the public and private ec2 instances
stop_response = stop_ec2_instances(public_ec2_instance['Instances'][0]['InstanceId'], private_ec2_instance['Instances'][0]['InstanceId'])


# In[ ]:


# Define a function to restart instances by passing on the list of instance id of instances to be restarted
def restart_ec2_instances(*args):
    instances_list = []
    for arg in args:
        instances_list.append(arg)
    ec2_client.start_instances(InstanceIds=instances_list)
# Restart both the stopped instances    
restart_ec2_instances(public_ec2_instance['Instances'][0]['InstanceId'], private_ec2_instance['Instances'][0]['InstanceId'])


# In[ ]:


# Define a function to terminate instances by passing on the list of instance id of instances to be terminated
def terminate_ec2_instances(*args):
    instances_list = []
    for arg in args:
        instances_list.append(arg)
    ec2_client.terminate_instances(InstanceIds=instances_list)
    
# Terminate the public instance
terminate_ec2_instances(public_ec2_instance['Instances'][0]['InstanceId'])

