#!/usr/bin/env python
# coding: utf-8

# In[136]:


# Import necessary packages
import boto3
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


# Create a boto3 session and retrieve the region name from it
session = boto3.session.Session()
region_name = session.region_name

# Create a rds client with region retrieved by boto3 
rds = boto3.client('rds', region_name=region_name)

# Create a ec2 client with region retrieved by boto3
ec2 = boto3.client('ec2', region_name=region_name)

# Get the details of the default vpc of the amazon account inorder to attach the rds databse inside the vpc
default_vpc = ec2.describe_vpcs(Filters=[
                                    {
                                        'Name': 'isDefault',
                                        'Values': ['true']
                                    }
])

# Get the default vpc's id
vpc_id = default_vpc['Vpcs'][0]['VpcId']
print(vpc_id)

RDS_SECURITY_GROUP = 'rds-db-security-group'
RDS_SECURITY_DESC = 'Description for rds security group'
# Create a security group with group name, description and vpc id parameters
security_group = ec2.create_security_group(GroupName=RDS_SECURITY_GROUP,
                                           Description=RDS_SECURITY_DESC,
                                           VpcId=vpc_id)


# Get the security group id
security_group_id = security_group['GroupId']
print(security_group_id)

# Set a rule for the tcp traffic flow for the rds database port 5432 for all ip addresses
ip_permission = [
                    {
                        'FromPort': 5432,
                        'ToPort': 5432,
                        'IpProtocol': 'tcp',
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
]

security_rule_response = ec2.authorize_security_group_ingress(GroupId=security_group_id,
                                                              IpPermissions=ip_permission)

print(security_rule_response)

# Find the subnets in the default vpc
subnets = ec2.describe_subnets(Filters=[
                                    {
                                        'Name': 'vpc-id',
                                        'Values': [vpc_id]
                                    }
])

subnet_list = []
# Retreive the subnet ids of the subnet in the vpc
for subnet in subnets['Subnets']:
    subnet_list.append(subnet['SubnetId'])
    
print(subnet_list)

RDS_DB_SUBNET = 'rds-db-subnet-group'
RDS_DB_DESC = 'RDS subnet group'
# Create a database subnet group for rds
db_subnet = rds.create_db_subnet_group(DBSubnetGroupName=RDS_DB_SUBNET,        # rds subnet group name
                                       DBSubnetGroupDescription=RDS_DB_SUBNET, # rds subnet group description
                                       SubnetIds=subnet_list)                  # List of subnets 


print(db_subnet)

# Initialise some constants for the database creation
db_instance_identifier = 'rdspostgres'
database_name = 'RDS_Postgres'
user = 'postgresrds'
password = 'postgrespassword'

# Create the database instance
db_instance = rds.create_db_instance(DBName=database_name,  # Database name
                                     DBInstanceIdentifier=db_instance_identifier, # Database indentifier
                                     DBInstanceClass='db.t2.micro',  # Database instance type
                                     Engine='postgres',              # Kind of database, here postgres
                                     EngineVersion='11.4',           # Version of the database
                                     Port=5432,                      # Desired port number
                                     MasterUsername=user,            # User name for the database
                                     MasterUserPassword=password,    # Password for the database
                                     AllocatedStorage=10,            # Storage space in Gigibytes
                                     MultiAZ=False,                  # Should span over multiple regions or not
                                     StorageType='standard',         # Storage type
                                     PubliclyAccessible=True,        # Should be public or not 
                                     VpcSecurityGroupIds=[security_group_id],  # List of ids of subnets in the group
                                     DBSubnetGroupName=RDS_DB_SUBNET) # Subnet group name  


print(db_instance)

# Retreive the rds instance url
rds_url = rds.describe_db_instances()['DBInstances'][0]['Endpoint']['Address']
print(rds_url)

# Save the rds_url to another variable
host = rds_url

# Create a sqlalchemy engine with the necessary information to test the database is actually created
engines = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}/{database_name}', echo=True)

meta = MetaData()
# Create a table with four columns
students = Table(
   'student', meta, 
   Column('id', Integer, primary_key = True), 
   Column('name', String), 
   Column('lastname', String),
)
print(meta.create_all(engines))

# Insert the values, connect to the database engine and execute the insert operation 
ins = students.insert()
ins = students.insert().values(nam = 'Ravi', lastname = 'Kapoor')
conn = engines.connect()
result = conn.execute(ins)
print(result)

# Update the storage space of the database to 20 gigibytes   
modify_response = rds.modify_db_instance(DBInstanceIdentifier='rdspostgres', AllocatedStorage=20)

# Define a function to take a snapshot the database for back up
def take_snapshot(db_instance_identifier, db_snapshot_identifier, tag_name):
    tag = [{'Key': 'Name', 'Value': tag_name}]
    # Create the snapshot 
    return rds.create_db_snapshot(DBInstanceIdentifier=db_instance_identifier, # Database identifier
                                  DBSnapshotIdentifier=db_snapshot_identifier, # Snapshot identifier
                                  Tags=tag)

snapshot_response = take_snapshot(db_instance_identifier, 'FirstSnapshot', 'snapshot_1')

print(snapshot_response)

desc_snapshot = rds.describe_db_snapshots(DBInstanceIdentifier=db_instance_identifier)

# Get the description of the snapshot
snap_shot_identifier = desc_snapshot['DBSnapshots'][-1]['DBSnapshotIdentifier']

# Delete the databse using the database identifier  
delete_response = rds.delete_db_instance(DBInstanceIdentifier=db_instance_identifier,
                                         SkipFinalSnapshot=True)

