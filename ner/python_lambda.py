#!/usr/bin/env python
# coding: utf-8

# In[1]:

import os

def handler(event, context):
    return {
        'status_code': 200,
        'message': os.getenv('ENV_KEY')
    }


# In[ ]:




