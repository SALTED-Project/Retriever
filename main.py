import json, requests
from datetime import date, datetime
from urllib import parse
from dateutil.relativedelta import relativedelta

from flask import Flask, request, abort, Response
from waitress import serve

from tokenhandler.handler import TokenHandler


# --------- Global Variables ---------
DEAFULT_CONTEXT = "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context-v1.7.jsonld"
# Configuration
with open('config.json', 'r') as f:
  config = json.load(f)

  broker_dir = config.get("context_broker").get("url", {})
  if not broker_dir:
    raise ValueError("Context Broker url is None. Please, provide a valid URL.")
  broker_dir = broker_dir +"/ngsi-ld/v1/"

  auth = config.get("context_broker").get("auth", False)
  if auth:
    # Token Handler --> keycloak
    url = config.get("authentication").get("url", {})
    if not url:
      raise ValueError("Authentication url is None. Please, provide a valid URL.")
    
    client_id = config.get("authentication").get("client_id", {})
    if not client_id:
      raise ValueError("Authentication client_id is None. Please, provide a valid client_id.")

    client_secret = config.get("authentication").get("client_secret", {})
    if not client_secret:
      raise ValueError("Authentication client_secret is None. Please, provide a valid client_secret.")

    th = TokenHandler(url, client_id, client_secret)
    
# -------------------------------------------------------------

# Temporal object
temporal_obj = {}
temporal_units = ['years', 'months', 'weeks', 'days', 'hours']
# ------------------------------------

def create_temporal_url_resource(entity_type, temporal_obj):
  current_date = datetime.now()

  if temporal_obj['unit'] == 'years':
    relative_delta_value = relativedelta(years = temporal_obj['value'])
  elif temporal_obj['unit'] == 'months':
    relative_delta_value = relativedelta(months = temporal_obj['value'])
  elif temporal_obj['unit'] == 'weeks':
    relative_delta_value = relativedelta(weeks = temporal_obj['value'])
  elif temporal_obj['unit'] == 'days':
    relative_delta_value = relativedelta(days = temporal_obj['value'])
  else:
    abort(400, "Invalid temporal unit")

  return "temporal/entities/?type=" + entity_type + "&timerel=after&timeAt=" + (current_date - relative_delta_value).strftime('%Y-%m-%dT%H:%M:%SZ')

def create_url(entity_type, temporal_obj):
  entity_type = parse.quote(entity_type, safe='')
  url = (
    broker_dir + create_temporal_url_resource(entity_type, temporal_obj)
    if temporal_obj['is_temporal']
    else broker_dir+"entities/?type=" + entity_type
  )
  return url

def make_get_request(entity_type, representation_format, temporal_obj):
  # --- URL ---
  url = create_url(entity_type, temporal_obj) + "&limit=999"

  # --- Headers ---
  # "Accept"
  accept_header =(
    "application/json"
    if representation_format == "json"
    else "application/ld+json"
  )
  
  headers = {
    'Accept': accept_header
  }

  if auth:
    # "Authorization"
    access_token = th.get_token()
    headers["Authorization"] = 'Bearer ' + access_token

  # --- Request ---
  response = requests.request("GET", url, headers=headers, data={}, verify=False)
  return response.json()
  
def make_head_request(entity_type, representation_format, temporal_obj):
  # --- URL ---
  url = create_url(entity_type, temporal_obj) + "&limit=0&count=true"

  # --- Headers ---
  headers = {}
  
  if auth:
    # "Authorization"
    access_token = th.get_token()
    headers["Authorization"] = 'Bearer ' + access_token

  # --- Request ---
  response = requests.request("HEAD", url, headers=headers, data={}, verify=False)
  
  custom_response = Response()
  # response.headers fields are strings
  if int(response.headers.get('ngsild-results-count', "0")):
    custom_response.status_code = 200
  else:
    custom_response.status_code = 404
      
  return custom_response

app = Flask(__name__)

@app.route('/realtime/__<path:entity_type>__.<representation_format>', methods=['GET', 'HEAD'])
def realtime(entity_type, representation_format):
  # print(request, flush=True)

  temporal_obj['is_temporal'] = False # no need to define the rest of key-values
  if request.method == "HEAD":
    response = make_head_request(entity_type, representation_format, temporal_obj)
  else:
    response = make_get_request(entity_type, representation_format, temporal_obj)
  
  return response

@app.route('/temporal/__<path:entity_type>__.<representation_format>', methods=['GET', 'HEAD'])
def temporal(entity_type, representation_format):
  # print(request, flush=True)

  temporal_obj['is_temporal'] = True
  try:
    params = request.url.split("?")[-1]
    temporal_obj['unit'] = params.split("=")[0]; temporal_obj['value'] = params.split("=")[1]
  except:
    temporal_obj['unit'] = "days"; temporal_obj['value'] = 5 # default values

  if temporal_obj['unit'] not in temporal_units:
    abort(400, "invalid temporal unit param")
  
  if request.method == "HEAD":
    response = make_head_request(entity_type, representation_format, temporal_obj)
  else:
    response = make_get_request(entity_type, representation_format, temporal_obj)

  return response

@app.route('/', methods=['GET'])
def default():
  abort(400)

if __name__ == '__main__':
  serve(app, host="0.0.0.0", port=5012)