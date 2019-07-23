#!/usr/bin/env python
# coding: utf-8

# In[25]:


#Import necessary modules
import boto3
from boto3.s3.transfer import TransferConfig
import json
import uuid

# Create a S3 client
s3_client = boto3.client('s3')
# Create a boto3 session
session = boto3.session.Session()


# In[119]:


# Function to create random bucket names with a fixed prefix
def create_bucket_name(bucket_prefix_name):
    # Add both the prefix string and the uuid to make a unique bucket name
    return bucket_prefix_name + str(uuid.uuid4())


# In[130]:


# Function to create bucket in S3
def create_bucket(bucket_prefix='s3-aws'):
    # Use the create_bucket_name to get a unique bucket name
    bucket_name = create_bucket_name(bucket_prefix)
    # Get the current aws region using the session
    current_region = session.region_name
    # Create a bucket with the name in the current region using the s3 client
    bucket_create = s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': current_region})
    return bucket_name, bucket_create


# In[132]:


# Create the first bucket and the save the bucket name
BUCKET_NAME, bucket_response = create_bucket('s2-aws')


# In[133]:


print(BUCKET_NAME)


# In[125]:


print(bucket_response)


# In[173]:


# Create a bucket policy to determine the permissions
bucket_policy = {
    
    'Statement': [
        {
            'Sid': 'Permission',  # A random string id 
            'Effect': 'Allow',    # Whether this policy is allowing or denying, here it is allowing 
            'Principal': '*',     # The beneficiaries of this policy, here every users in the aws account
            'Action': ['s3:*'],   # The actions that the benefeciaries can do, here, all the operations
            'Resource': ['arn:aws:s3:::' + BUCKET_NAME + '/*'] # Here the permission to do the action on the resources in s3
        }
    ]
}


# In[174]:


# Convert the bucket policy dict into json as s3 is expecting it in json format
bucket_policy_json = json.dumps(bucket_policy)


# In[175]:


# Put the bucket policy to the specific bucket
s3_bucket_policy = s3_client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=bucket_policy_json)


# In[138]:


# Get the policy associated the bucket 
bucket_policy_from_s3 = s3_client.get_bucket_policy(Bucket=BUCKET_NAME)


# In[52]:


print(bucket_policy_from_s3)


# In[139]:


# Bucket policy to update the existing one or if no existing one, create new one.  
update_bucket_policy = {
    'Version': '2012-10-17', # The updation is the version, as the default version is '2008-10-17'
    'Statement': [
        {
            'Sid': 'AddPerm',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:*'],
            'Resource': ['arn:aws:s3:::' + BUCKET_NAME + '/*']
        }
    ]
}

# Convert the new policy to json
update_bucket_policy_json = json.dumps(update_bucket_policy)


# In[140]:


# Put the update bucket policy to the bucket, the version will be changed  
update_s3_bucket_policy = s3_client.put_bucket_policy(Bucket=BUCKET_NAME, Policy=update_bucket_policy_json)


# In[141]:


# Get all the buckets in the s3
buckets = s3_client.list_buckets()


# In[50]:


print(buckets)


# In[142]:


# Encrypt the data stored in the specific bucket on the server side by applying the aes encrptyion 
encrypt_response = s3_client.put_bucket_encryption(Bucket=BUCKET_NAME,
                                                   ServerSideEncryptionConfiguration={
                                                       'Rules':[
                                                           {
                                                               'ApplyServerSideEncryptionByDefault': {
                                                                   'SSEAlgorithm': 'AES256'
                                                               }
                                                           }
                                                       ]
                                                   })


# In[143]:


# Get the encryption details associated with a specific bucket
encrypt_policy = s3_client.get_bucket_encryption(Bucket=BUCKET_NAME)


# In[77]:


print(encrypt_policy)


# In[145]:


# Create a text with the following string to upload to a bucket
s = 'S3 upload text file'
with open('word.txt', 'w') as w:
    w.write(s)


# In[146]:


# Upload the file
s3_client.upload_file('word.txt',          # The file path 
                      Bucket=BUCKET_NAME,  # Bucket name
                      Key='word.txt')      # The key or name of the file in the bucket


# In[147]:


# Create  a transfer configuration to upload large files as multipart
transfer_config = TransferConfig(multipart_threshold=1024*10, # The minimum size of the file to be uploaded as multipart in MB
                                 max_concurrency=5,           # The number of threads
                                multipart_chunksize=1024* 5)  # The size of chunked file parts in MB


# In[148]:


# Upload a large file utilizing the multipart feature
s3_client.upload_file('Networking.pdf',                       # The file path
                      BUCKET_NAME, Key='Networking_book.pdf', # The bucket name 
                      ExtraArgs={'ACL': 'public-read',        # Make the file public-read using the access control list
                                 'ContentType': 'text/pdf'},  # Specify the content of the file
                      Config=transfer_config)                 # Pass in the transfer configuration 


# In[150]:


# Enable versioning on the bucket 
version_bucket = s3_client.put_bucket_versioning(Bucket=BUCKET_NAME, VersioningConfiguration={'Status': 'Enabled'})


# In[151]:


# Make changes in the small file we have already to see the versioning effect
with open('wod.txt', 'a') as w:
    w.write('\n' + 'New version')


# In[152]:


# Upload the changed file to make this file as the latest version
s3_client.upload_file('word.txt', Bucket=BUCKET_NAME, Key='word.txt')


# In[153]:


# Create a life policy structure for objects in the bucket
life_cycle_policy = {
    'Rules': [
        {'Status': 'Enabled',   # Enable the rules
        'Prefix': '',           # Applicable to all objects
        'NoncurrentVersionExpiration': {'NoncurrentDays': 100},        # Delete non current version files after 100 days
        'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 5}}  # Delete non complete uploads afer 5 days
    ]
}


# In[154]:


# Put the life cycle configuration to the bucket
s3_client.put_bucket_lifecycle_configuration(Bucket=BUCKET_NAME, LifecycleConfiguration=life_cycle_policy)


# In[155]:


# Download a file from the bucket
s3_client.download_file(BUCKET_NAME, 
                        'word.txt',            # Key name of the file 
                        'downloaded_word.txt') # Destination file path


# In[156]:


# Create a function to copy file from one bucket to another 
def copy_file(source_bucket, source_key, destination_bucket, destination_key):
    copy_source = {
        'Bucket': source_bucket, # Source bucket
        'Key': source_key        # Source file
    }
    
    # Copy using the file using the s3 client
    s3_client.copy(copy_source, destination_bucket, destination_key)


# In[ ]:


# Create another bucket 
second_bucket, _ = create_bucket()


# In[157]:


# Copy the file from the first bucket to the second bucket
copy_file(BUCKET_NAME, 'word.txt', second_bucket, 'word.txt')


# In[158]:


# Download a file from the specified bucket
s3_client.download_file(second_bucket,    # Bucket name
                        'word.txt',       # Key name on the bucket
                        'second_word.txt')# Destination file path 


# In[165]:


# Create a function to delete multiple files at a time from a bucket
def delete_files(bucket_name, *args):
    key_list = []
    # Specify the files to be deleted in *args and insert all into a list
    for arg in args:
        key_list.append({'Key': arg})
    # Delete the files using the bucket name the list of the files to be deleted
    delete_response = s3_client.delete_objects(Bucket=bucket_name, 
                                               Delete={'Objects': key_list})
    return delete_response


# In[166]:


# Delete two files from the first bucket
delete_files(BUCKET_NAME, 'Networking_book.pdf', 'word.txt')


# In[176]:


# Function to delete a bucket from s3
def delete_bucket(bucket_name):
    # Create an s3 resource
    s3_resource = boto3.resource('s3')
    # Get the bucket instance 
    bucket = s3_resource.Bucket(bucket_name)
    # Delete all the version of the objects in the bucket inorder to successfully delete a bucket
    bucket.object_versions.delete()
    # Finally delete the bucket
    bucket.delete()
    
# Delete the first bucket
delete_bucket(BUCKET_NAME)


# In[ ]:




