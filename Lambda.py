#!/usr/bin/env python
# coding: utf-8

# In[54]:


'''
A tutorial on creating an AWS lambda function for serverless configuration with Python.

Following are the actions in the example.

- Creating helper functions for lambda function
- Creating IAM policy, lambda role and attaching together for lambda to execute
- Create and deploy the lambda function
- Invoking the lambda function
- Updating the lambda function configuration by passing environment variables
- Updating the lambda function code and invoking it
- Versioning the lambda function
- Creating aliases for the lambda function and invoking with the alias name
- Getting the full configuration of the lambda function
- Deleting the lambda function
'''
# Import necessary functions

import boto3
import json
import os
import io
import os

# Create utility functions to zip the contents in the file
class Utils:
    # Function to retreive all the files
    @staticmethod
    def make_zip(path):
        # Walk through all the files
        for root, dirs, files in os.walk(path):
            for file in files:
                # Concatenate the root and file names together
                full_path = os.path.join(root, file)
                archive_name = full_path[len(path) + len(os.sep):]
                # Yield the values 
                yield full_path, archive_name
    
    # Function to make buffer of the contents and zip 
    @staticmethod
    def zipper(path):
        # Create a BytesIO object
        buffer = io.BytesIO()
        # Zip the contents in binary
        with ZipFile(buffer, 'w') as z:
            for full_path, archive_name in Utils.make_zip(path):
                z.write(full_path, archive_name)
        return buffer.getvalue()
    
    
# Create a boto3 session 
session = boto3.session.Session()
# Get the region name from the session
region_name = session.region_name
# Create a lambda client with the region name
lambda_client = boto3.client('lambda', region_name=region_name)

# Create an IAM client for creating policy, role and attaching together
iam = boto3.client('iam')

# Create a policy document for the lambda to use the S3 and CloudWatch logs
policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["s3:*", "logs:*"], # Allow all s3 and logs actions 
                    "Effect": "Allow",
                    "Resource": "*"  # Allow the actions for all the resources
                }
            ]
}

# Create the iam policy using the policy document
iam_policy = iam.create_policy(PolicyName='lambdapolicy',
                               PolicyDocument=json.dumps(policy),
                               Description='Lambda to S3 access for serverless application')

# Get the policy arn
policy_arn = iam_policy['Policy']['Arn']
print(policy_arn)



# Create a lambda execution role document
lambda_exec_role = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal":  {
                                    "Service": "lambda.amazonaws.com" # Allow the service for lambda
                                },
                                "Action": "sts:AssumeRole" # Allow the action for temporary security credentials to access AWS resources
                            }
                        ]
}

lambda_role_name = 'lambdasrole'
# Create the lambda role with the role document
lambda_role = iam.create_role(RoleName=lambda_role_name,
                              AssumeRolePolicyDocument=json.dumps(lambda_exec_role),
                              Description="Permissions for AWS Lambda function")

# Get the lambda role arn
role_arn = lambda_role['Role']['Arn']
print(role_arn)

# Attach the role to the policy
attach_role = iam.attach_role_policy(RoleName=lambda_role_name,
                                     PolicyArn=policy_arn)

function_name = 'lambda-functionpython'
handler = 'python_lambda.handler'
runtime = 'python3.6'
time_out = 10
memory_size = 128

# Define a function to create a lambda function
def deploy_fn(fn_name, runtime, handler, role_arn, source_folder):
    # Path to the folder containing the handler
    folder_path = os.path.join(os.path.dirname(os.path.abspath("__file__")), source_folder)
    # Get the zipped file of the folder
    zip_file = Utils.zipper(path=folder_path)
    # Create a lambda function
    fn_create = lambda_client.create_function(FunctionName=function_name, # Function name
                              Role=role_arn,    # The execution role arn
                              Handler=handler,  # The handler function to be invoked
                              Runtime=runtime,  # The runtime source
                              Code={
                                  'ZipFile': zip_file  # The zip file containing the code
                              },
                              Timeout=time_out, # Amount of time allowed for the function to run before being stopped
                              MemorySize=memory_size, # Memory for the function (Multiple of 64)
                              Publish=False)    # Blocking versioning upon creating the function
    return fn_create

# Deploy the function in the folder named ner
deploy = deploy_fn(function_name, runtime, handler, role_arn, 'ner')

print(deploy)

# Function to invoke the lambda function
def invoke_fn(fn_name):
    # Invoke the function with its function name
    response = lambda_client.invoke(FunctionName=fn_name)
    # Return the decoded payload of the version
    return response['Payload'].read().decode()

# Invoke the function
s = invoke_fn(function_name)
print(s)

# Update the lambda function configuration by setting environment variable as an example
update_env = lambda_client.update_function_configuration(FunctionName=function_name,
                                                         Environment={
                                                             'Variables':
                                                             {
                                                                 'ENV_KEY': 'New Environment variable' # Set the env variable key and value
                                                             }
                                                         })

print(update_env)


# Define a function to update the lambda function code
def update_fn(fn_name, source_folder):
    folder_path = os.path.join(os.path.dirname(os.path.abspath("__file__")), source_folder)
    # Get the zipped content
    zip_file = Utils.zipper(path=folder_path)
    # Update the code with the updated zip file 
    return lambda_client.update_function_code(FunctionName=fn_name,
                                              ZipFile=zip_file)

# Update the lambda function with the env variable
update_fn(function_name, 'ner')

# Invoke the update function
invoke_fn(function_name)

# Define a function version the lambda function
def version_publish(fn_name=function_name):
    # Apply new version to the lambda function
    return lambda_client.publish_version(FunctionName=function_name)

print(version_publish())

# Create a function to apply alias for the lambda function version
def create_alias(fn_name, alias, version):
    return lambda_client.create_alias(FunctionName=fn_name, # The function name
                                      Name=alias,           # The new alias name
                                      FunctionVersion=version, # The version to which alias name to be applied 
                                      Description=alias+'alias name for '+fn_name) # Description for the alias
    
    
# Create an alias 'DEV' for the version 1 of the lambda function
alias_response = create_alias(function_name, 'DEV', '1')
print(alias_response)

# Function to invoke the lambda function with the alias name
def invoke_with_alias(fn_name, alias):
    response = lambda_client.invoke(FunctionName=fn_name,  # Lambda function name
                                    Qualifier=alias)       # The alias name
    # Return the decoded payload response
    return response['Payload'].read().decode()


# Invoke the lambda function with the alias name
alias_fn = invoke_with_alias(function_name, 'DEV')

print(alias_fn)

# Get the configuration details of the lambda functions
def get_fn_config(fn_name=function_name):
    return lambda_client.get_function(FunctionName=function_name)

fn_config = get_fn_config()
print(fn_config)

# Delete the lambda function
def delete_fn(fn_name=function_name):
    return lambda_client.delete_function(FunctionName=function_name)

delete_response = delete_fn()

