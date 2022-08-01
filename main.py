from TwitterHandler import *
from KeysConstant import *

# to import back dataset
import ast

def get_ip_country(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()['country_name']


# twitterhandler = TwitterHandler(twitter_bearer_token)
#
# twitterhandler.add_tracking_user("cobaltstrikebot")
# twitterhandler.add_tracking_user("drb_ra")
# twitterhandler.add_tracking_user("Unit42_Intel")
#
# twitterhandler.get_tweetdata_from_users()
#
# ip_ioc = twitterhandler.ip_ioc
#
# with open('dataset.txt', 'w') as f:
#     f.write(str(ip_ioc))

ip_ioc = {}

with open('dataset.txt','r') as f:
   ip_ioc = ast.literal_eval(f.read())

for ip in ip_ioc:
    ip_country = get_ip_country(ip)
    print (ip_country)
    if(ip_country == "Singapore"):
        print("write ip to file")
        with open('./melting-cobalt/ips.txt', 'a') as f:
            f.write(ip + "\n")


