from TwitterHandler import *
from KeysConstant import *
import geoip2.database

# to import back dataset
import ast

def get_ip_country(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()['country_name']

def get_ip_information(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()


# twitterhandler = TwitterHandler(twitter_bearer_token)
#
# twitterhandler.add_tracking_user("cobaltstrikebot")
# twitterhandler.add_tracking_user("drb_ra")
# twitterhandler.add_tracking_user("Unit42_Intel")
# twitterhandler.add_tracking_user("KorbenD_Intel")
# twitterhandler.add_tracking_user("cpardue09")
# twitterhandler.add_tracking_user("malware_traffic")
# twitterhandler.get_tweetdata_from_users(7)
#
# ip_ioc = twitterhandler.ip_ioc
#
# with open('datasetip.txt', 'w') as f:
#     f.write(str(ip_ioc))
#
# # =======
#
# ip_ioc = {}
#
# with open('datasetip.txt','r') as f:
#    ip_ioc = ast.literal_eval(f.read())
#
# for ip in ip_ioc:
#     ip_country = get_ip_country(ip)
#     print (ip_country)
#     if(ip_country == "Singapore"):
#         print("write ip to file")
#         with open('./melting-cobalt/ips.txt', 'a') as f:
#             f.write(ip + "\n")


# ===


# f = open('./melting-cobalt/results.json.log', 'r')
# data = json.load(f)
# f.close()
# for eachscan in data:
#     ip_info = get_ip_information(eachscan["ip"])
#     eachscan["country_name"] = ip_info["country_name"]
#     eachscan['isp'] = ip_info['isp']
#
#
# with open("result.json", "w") as f:
#     json.dump(data, f, indent=4, sort_keys=True)


reader = geoip2.database.Reader('./GeoLite/GeoLite2-Country.mmdb')
response = reader.country('128.101.101.101')
print(response.country.iso_code)
ip_ioc = {}

with open('datasetip.txt','r') as f:
   ip_ioc = ast.literal_eval(f.read())

for ip in ip_ioc:
    try:
        ip_country = reader.country(ip).country.iso_code
    except:
        continue
    print (ip_country)
    if(ip_country == "SG"):
        print("write ip to file")
        with open('./melting-cobalt/ips2.txt', 'a') as f:
            f.write(ip + "\n")