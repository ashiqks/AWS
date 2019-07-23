#!/usr/bin/env python
# coding: utf-8

# In[119]:


# Import the boto3 package for aws
import boto3


# From boto3 create an ec2 service client with the given region 
ec2_client = boto3.client('ec2', region_name='us-east-2')

# Create a vpc using the client and the ip address range to be allocated to it 
vpc = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
print(vpc)

# Get the vpc id from the response
vpc_id = vpc['Vpc']['VpcId']
print(vpc_id)


# Create tag for the vpc by passing in the vpc id and the expected variables
ec2_client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name',
                                                 'Value': 'vpc_ec2_'}])

# Create an internet gateway using the client
internet_gateway = ec2_client.create_internet_gateway()

print(internet_gateway)

# Get the internet gateway id from the response for the gateway
gateway_id = internet_gateway['InternetGateway']['InternetGatewayId']

# Attach the gateway to the vpc by passing in the gateway and corresponding vpc ids
gateway_attach = ec2_client.attach_internet_gateway(InternetGatewayId=gateway_id, VpcId=vpc_id)
print(gateway_attach)

# Create tag for the gateway
ec2_client.create_tags(Resources=[gateway_id], Tags=[{'Key': 'Name',
                                                      'Value': 'igw_vpc_'}])

# Define a function to create subnets with the parameters vpc id and the ip address range for the subnet
def create_subnet(vpc_id, cidr_block):
    return ec2_client.create_subnet(VpcId=vpc_id, CidrBlock=cidr_block)

# Create a subnet with the following ip address range within the vpc
public_subnet = create_subnet(vpc_id, '10.0.1.0/24')

print(public_subnet)

# Create a custom route table with the vpc id as the parameter to connect to the subnet 
route_table = ec2_client.create_route_table(VpcId=vpc_id)
print(route_table)

# Get the generated route table id
route_table_id = route_table['RouteTable']['RouteTableId']

# Create a route between the route table and the gateway for all the ip addresses
igw_route_to_route_table = ec2_client.create_route(RouteTableId=route_table_id, GatewayId=gateway_id, DestinationCidrBlock='0.0.0.0/0')

# Get the id of the subnet created 
public_subnet_id = public_subnet['Subnet']['SubnetId']

# Define a function to associate the route table with the subnet to make the subnet public
def subnet_route_table_connection(route_table_id, subnet_id):
    return ec2_client.associate_route_table(RouteTableId=route_table_id, SubnetId=subnet_id)

# Associate the route table with the subnet with the route table and subnet ids
associate_route = subnet_route_table_connection(route_table_id, public_subnet_id)

print(associate_route)

# Modify the the MapPublicOnLaunch to set it to true by specifiying the subnet id to assign ip addressses automatically while being launced
auto_assign_ip = ec2_client.modify_subnet_attribute(MapPublicIpOnLaunch={'Value': True}, SubnetId=public_subnet_id)

print(auto_assign_ip)

# Create a subnet which is intended to be private
private_subnet = create_subnet(vpc_id, '10.0.2.0/24')

print(private_subnet)

# Get the id of the private subnet
private_subnet_id = private_subnet['Subnet']['SubnetId']

# Create tags for both the public and private subnets
ec2_client.create_tags(Resources=[public_subnet_id, private_subnet_id],
                       Tags=[{'Key': 'Name', 'Value': 'Public Subnet VPC EC2'},
                             {'Key': 'Name', 'Value': 'Private Subnet VPC EC2'}])

