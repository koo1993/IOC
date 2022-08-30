# For sending GET requests from the API
import requests
# For saving access tokens and for file management when creating and adding to the dataset
import os
# For dealing with json responses we receive from the API
import json
# For displaying the data after
import pandas as pd
# For saving the response data in CSV format
import csv
# For parsing the dates received from twitter in readable formats
import datetime
import dateutil.parser
import unicodedata
# To add wait time between requests
import time
import urllib3


class TwitterHandler:
    auth_token = "empty"
    url_ioc = set()
    ip_ioc = set()
    domain_ioc = set()
    session = requests.Session()  # so connections are recycled
    # ioc_mapper = {{}}
    twitter_users = []
    urllib3.disable_warnings()  # ignore warning

    def __init__(self, token):
        self.auth_token = token

    def check_auth_empty(self):
        if self.auth_token == "empty":
            return True
        else:
            return False

    def auth(self):
        return os.getenv('TOKEN')

    def __get_header(self):
        return {"Authorization": "Bearer {}".format(self.auth_token)}

    def add_tracking_user(self, user):
        self.twitter_users.append(user)

    def get_user_id(self, user_name):
        search_url = "https://api.twitter.com/2/users/by/username/" + user_name
        headers = self.__get_header()
        response = requests.request("GET", search_url, headers=headers, verify=False)

        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        if "errors" in response.json().keys():
            raise Exception(user_name + " not found", response.text)

        return response.json()["data"]["id"]

    def get_unshorten_link(self, url):
        print("====== Attempt to unshorten url {} ========".format(url))
        try:
            resp = self.session.head(url, allow_redirects=True, verify=False, timeout=3)
        except:
            print("failed to unshorten: " + url)
            return url
        print("====== After shorten url {} ===============".format(resp.url))
        return resp.url

    def get_tweet_list(self, user_id, daysbefore):
        search_url = "https://api.twitter.com/2/users/" + user_id + "/tweets"
        headers = self.__get_header()

        #get date to stop at
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=daysbefore)

        query_params = {
            'tweet.fields': 'created_at', #show created field in the return data
            'start_time': start_time.isoformat()[:-13] + 'Z', #tweet that is between now to start_time
            'max_results': 100  # max retrieval result == 100
        }

        response = requests.request("GET", search_url, params=query_params, headers=headers, verify=False)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def get_tweet_list_nexttoken(self, user_id, daysbefore, nexttoken):
        search_url = "https://api.twitter.com/2/users/" + user_id + "/tweets"
        headers = self.__get_header()

        #get date to stop at
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=daysbefore)

        query_params = {
            'tweet.fields': 'created_at', #show created field in the return data
            'start_time': start_time.isoformat()[:-13] + 'Z', #tweet that is between now to start_time
            'max_results': 100,  # max retrieval result == 100
            'pagination_token': nexttoken
        }

        response = requests.request("GET", search_url, params=query_params, headers=headers, verify=False,)
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def get_json_iocparser_url(self, url):
        api_url = "https://api.iocparser.com/url"
        payload = {
            "url": url
        }
        headers = {
            'Content-Type': 'application/json',
        }
        response = requests.request("POST", api_url, headers=headers, json=payload, verify=False,)
        if response.status_code == 204:  # 204 no content
            print("empty response from IOCparser with url: " + url)
            return None
        elif response.status_code != 200:
            print(url + " response code: " + str(response.status_code))
            return None
        return response.json()

    def get_json_iocparser_text(self, text):
        api_url = "https://api.iocparser.com/text"
        payload = {
            "data": text
        }
        headers = {
            'Content-Type': 'application/json',
        }
        try:
            response = requests.request("POST", api_url, headers=headers, json=payload, verify=False)
        except:
            print("failed to pull from iocparser")
            return None
        if response.status_code == 204:
            return None
        elif response.status_code != 200:
            raise Exception(response.status_code, response.text)
        return response.json()

    def process_tweet_data(self, user_tweet_data):
        if user_tweet_data['meta']['result_count'] == 0:
            return

        for data in user_tweet_data['data']:
            tweeter_text = data['text']
            if "strike" in tweeter_text.lower():
                print("~~~~~~~~~~~~~PARSING DATA WITH Word \"STRIKE\"~~~~~~~~~~")
                iocparser_data = self.get_json_iocparser_text(tweeter_text)

                if iocparser_data == None:
                    continue

                print(iocparser_data)

                if iocparser_data['status'] == "error":
                    print("failed to parse from iocparser.com: " + tweeter_text)
                    continue

                is_processed_with_url = False

                # process https://twitter.com/cobaltstrikebot format
                for url in iocparser_data['data']['URL']:
                    url_to_parse = self.get_unshorten_link(url)
                    data_to_add = self.get_json_iocparser_url(url_to_parse)
                    print(data_to_add)

                    if data_to_add == None:
                        continue

                    if data_to_add['status'] == "error":
                        print("failed to parse from iocparser.com: " + url_to_parse)
                        continue

                    if len(data_to_add['data']['URL']) > 0 or len(data_to_add['data']['IPv4']) > 0 or len(
                            data_to_add['data']['DOMAIN']) > 0:
                        is_processed_with_url = True

                    self.url_ioc.update(data_to_add['data']['URL'])
                    self.ip_ioc.update(data_to_add['data']['IPv4'])
                    self.domain_ioc.update(data_to_add['data']['DOMAIN'])

                # additional to fit https://twitter.com/drb_ra format
                if not is_processed_with_url:
                    self.url_ioc.update(iocparser_data['data']['URL'])
                    self.ip_ioc.update(iocparser_data['data']['IPv4'])
                    self.domain_ioc.update(iocparser_data['data']['DOMAIN'])

        print("end of loop printing all the set")
        print(self.url_ioc)
        print(self.ip_ioc)
        print(self.domain_ioc)

    def get_tweetdata_from_users(self, no_of_days):
        lookup_days = no_of_days
        for user in self.twitter_users:
            userid = self.get_user_id(user)
            data = self.get_tweet_list(userid, lookup_days)
            print(data)
            self.process_tweet_data(data)

            # fetch more tweets if theres more than 100 tweets
            while "next_token" in data['meta']:
                print("GETTING MORE TWEETS")
                data = self.get_tweet_list_nexttoken(userid, lookup_days, data['meta']['next_token'])
                print(data)
                self.process_tweet_data(data)


