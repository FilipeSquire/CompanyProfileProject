import time
from azure.identity import ClientSecretCredential
# from azure.mgmt.datafactory import DataFactoryManagementClient
# import azure.functions as func
import requests
import os 
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=True)



# SUBSCRIPTION_ID = "<sub-id>"
RESOURCE_GROUP  = os.getenv("RESOURCE_GROUP")
FACTORY_NAME    = os.getenv("FACTORY_NAME")
PIPELINE_NAME   = os.getenv("PIPELINE_NAME")

TENANT_ID = os.getenv("BLOB_TENANT_ID")
CLIENT_ID = os.getenv("BLOB_CLIENT_ID")
CLIENT_SECRET = os.getenv("BLOB_CLIENT_SECRET")
FUNCTION_URL = os.getenv("FUNCTION_URL")

def trigger_function(companyNumber):
    r = requests.post(FUNCTION_URL, json={"company_number": companyNumber})
    r.raise_for_status()
    print(r.text)
    
