import argparse
import requests
import os
import json
import sys
import importlib
from glob import glob

class CGAPI:
  # API wrapper class for handling requests to CloudGuard.
  # Some processing for regions and IP tenants to alter endpoint URL
  # Instances of this class should be passed to each module to handle requests
  # and responses to CG.
  def __init__(self, connection_params):
    #setup internal variables
    self.cg_region = connection_params['cg_region']
    self.api_key = connection_params['api_key']
    self.api_secret = connection_params['api_secret']
    self.is_infinity = connection_params['infinity']
    self.auth = (self.api_key, self.api_secret)
    #build endpoint URL per region and consider Infinity Tenants
    match self.cg_region:
      case 'us':
        if self.is_infinity:
          self.api_endpoint = 'https://api.us1.cgn.portal.checkpoint.com'
        else:
          self.api_endpoint = 'https://api.dome9.com/v2'
      case 'eu':
        if self.is_infinity:
          self.api_endpoint = 'https://api.eu1.cgn.portal.checkpoint.com'
        else:
          self.api_endpoint = 'https://api.eu1.dome9.com/v2'
      case 'au':
        if self.is_infinity:
          self.api_endpoint = 'https://api.ap2.cgn.portal.checkpoint.com'
        else:
          self.api_endpoint = 'https://api.ap2.dome9.com/v2'
      case 'ca':
        if self.is_infinity:
          self.api_endpoint = 'https://api.cace1.cgn.portal.checkpoint.com'
        else:
          self.api_endpoint = 'https://api.cace1.dome9.com/v2'
      case 'in':
        if self.is_infinity:
          self.api_endpoint = 'https://api.ap3.cgn.portal.checkpoint.com'
        else:
          self.api_endpoint = 'https://api.ap3.dome9.com/v2'
      case 'sg':
        self.api_endpoint = 'https://api.ap1.dome9.com/v2'
      case _:
        raise ValueError("Error, invalid region supplied.")
    # Test credentials
    command = '/user'
    response = self.send_request(command, 'get')
    if response['ok'] == False:
      raise ConnectionError("Error accessing API. Please check endpoint and credentials match.")
    else:
      print("API initialised - connection ok ")

  def send_request(self, command, method, data=None):
    request_headers = {}
    request_headers['Content-Type'] = 'application/json'
    request_url = self.api_endpoint + command
    match method:
      case 'post':
        response = requests.post(request_url, data=data, auth=self.auth, header=request_headers)
      case 'put':
        response = requests.put(request_url, data=data, auth=self.auth, headers=request_headers)
      case 'delete':
        response = requests.delete(request_url, auth=self.auth, headers=request_headers)
      case 'get':
        response = requests.get(request_url, auth=self.auth, headers=request_headers)
      case default_:
        raise ValueError(f"Error: Invalid method supplied for API call - received {method}, expecting put, post, delete or get")
      #Process response and return new object with status code and response
    if response.ok:
      return_obj = {}
      return_obj['status_code'] = response.status_code
      return_obj['data'] = json.loads(response.text)
      return_obj['ok'] = response.ok
      return return_obj
    else:
      raise requests.RequestException(f"Error: request did not complete successfully. Status code {response.status_code} - {response.reason}")
    


def list_modules():
  # Look in the modules folder for new modules.
  # Each module should be passed an API client instance of CGAPI
  # and accept an input object (dict) and return an output object (dict)
  # The input object properties should be defined in its description.
  # The output should return an ok status (bool), error (str), and response(obj)
  # Each module should have a description function named describe which can be used
  # to inform the user of its purpose.
  

  for filename in glob('./extensions/*.py'):
    extension = importlib.import_module('extensions.' + (os.path.splitext(os.path.basename(filename)))[0], package='extensions')
    try:
      extension_description_output = extension.describe()
      del extension
      print(extension_description_output['response'])
    except:
      print(f"[ERROR] {filename} in extensions folder does not appear to be valid.")


def main():
  # Argparse settings for switches and flags
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-it", "--infinity-tenant",
    help="Specify if you are using an Infinity Portal tenant",
    action='store_true'
  )
  parser.add_argument(
    "-l", "--list-modules",
    help="List available modules",
    action='store_true'
  )
  parser.add_argument(
    "-r", "--region",
    help="CloudGuard tenant region (eu, us, au, in, ca, sg)",
    default='us'
  )
  args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
  if args.list_modules:
    list_modules()

  connection_params = {}
  connection_params['api_key'] = os.environ['CHKP_API_KEY']
  connection_params['api_secret'] = os.environ['CHKP_API_SECRET']
  connection_params['cg_region'] = args.region
  connection_params['infinity'] = args.infinity_tenant
  
  # Only create a wrapper if a module was selected
  #cgapi = CGAPI(connection_params)

main()