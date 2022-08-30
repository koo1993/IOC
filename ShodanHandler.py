import requests
import json
from KeysConstant import *

def get_from_shodan():
    search_url = "https://api.shodan.io/shodan/host/search?key=" + shodan_api_key

    query_params = {
        'query': 'product:cobalt strike country:SG'
    }

    response = requests.request("GET", search_url, params=query_params)

    result_json = response.json()

    shodan_sg_ip = set()

    for eachdata in result_json["matches"]:
        shodan_sg_ip.add(eachdata["ip_str"])

    return shodan_sg_ip
