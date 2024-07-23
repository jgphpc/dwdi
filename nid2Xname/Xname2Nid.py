import requests
import pandas as pd
import datetime as dt
from requests.auth import HTTPBasicAuth
import pytz
import json
import os

ti=dt.datetime.now()

base_url = 'https://sole.cscs.ch:9200'
index_name = '.ds-logs-accounting.platform-alps.v02*'

user = 'cscs_user'
passw = 'XXXXXXXXXXXXXXX'

scroll_time='1m'

### ELASTISEARCH TIME UTC= TO SUBTRACT 1H TO REGULAR TIME FOR THE TWO TIMESTAMPS###
delta=dt.timedelta(hours=2)
timestampE_=dt.datetime.now() - delta
timestampE=(timestampE_).strftime("%Y-%m-%dT%H:%M:%S")
timestampS_=(timestampE_-dt.timedelta(hours=24))
timestampS=timestampS_.strftime("%Y-%m-%dT%H:%M:%S")

## define scroll search which does the loop in ES and is faster than search after

def scroll_search(index_name, base_url,timestamp1,timestamp2,user,passw,scroll_time):
  query={
    "bool": { 
      "filter": [
        {
          "range": {
            "@timestamp": {
              "format": "strict_date_optional_time",
              "gte": timestamp1,
              "lt": timestamp2
            }
          }
        }
      ]
      }
      }
  # Set up the initial search request
  endpoint = f"{base_url}/{index_name}/_search?scroll="+scroll_time

    # Set up the search parameters
  search_params = {
        "size": 10000,  # Adjust this number based on your needs
        "query": query
    }

    # Make the initial search request
  response = requests.get(endpoint, json=search_params,auth=HTTPBasicAuth(user,passw))
  search_results = response.json()
 
    # Extract the scroll_id from the response
  all_hits=search_results["hits"]["hits"]
  # print(len(all_hits))
  if len(all_hits)==10000:
    scroll_id = search_results.get("_scroll_id")
    # Keep scrolling until there are no more results
    while True:
        # Set up the scroll request
        scroll_params = {
            "scroll": scroll_time,
            "scroll_id": scroll_id
        }

        # Make the scroll request
        scroll_response = requests.get(f"{base_url}/_search/scroll",json=scroll_params,auth=HTTPBasicAuth(user,passw))
        scroll_results = scroll_response.json()
        #print(scroll_results)

        all_hits.extend(scroll_results["hits"]["hits"])
        # Check if there are no more results
        if len(scroll_results["hits"]["hits"]) == 0:
          break
        
        # Update the scroll_id for the next scroll request
        scroll_id = scroll_results.get("_scroll_id")

  return all_hits

# Application of scroll_search

results=scroll_search(index_name,base_url,timestampS,timestampE,user,passw,scroll_time)
df_data=pd.json_normalize(results)
xname=df_data["_source.Entry.NodeId"].unique()
df_data_def=df_data[['_source.Entry.NodeNid','_source.Entry.NodeId']]

df_data_def=df_data_def.drop_duplicates()

#df_data_def['new_col'] = df_data_def.apply(lambda row : "nid00"+str(row[0]), axis=1)
df_data_def['nidName'] = df_data_def.apply(lambda row : "nid00"+str(row[0]) if row[0] != 0 else "0", axis=1)
df_data_def.drop(df_data_def.loc[df_data_def['nidName']=="0"].index, inplace=True)

df_data_def.drop(columns=['_source.Entry.NodeNid'], axis=1, inplace=True)
df_data_def.to_csv('nid_xanme.csv',header=False,index=False)
print(df_data_def)
