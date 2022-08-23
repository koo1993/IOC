from TwitterHandler import *
from KeysConstant import *
import geoip2.database
# to import back dataset
import ast
from subprocess import Popen, PIPE, CalledProcessError

# todo: organise code


def get_ip_country(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()['country_name']

def get_ip_information(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()

def empty_file_content(filelocation):
    open(filelocation, 'w').close()



#=== start

# insert twitter bearer tokken
twitterhandler = TwitterHandler(twitter_bearer_token)

# insert user for the bot to track
twitterhandler.add_tracking_user("cobaltstrikebot")
twitterhandler.add_tracking_user("drb_ra")
twitterhandler.add_tracking_user("Unit42_Intel")
twitterhandler.add_tracking_user("KorbenD_Intel")
twitterhandler.add_tracking_user("cpardue09")
twitterhandler.add_tracking_user("malware_traffic")

# insert number of days you want the bot to look up to
twitterhandler.get_tweetdata_from_users(7)

# get all the ip ioc
ip_ioc = twitterhandler.ip_ioc

with open('datasetip.txt', 'w') as f:
    f.write(str(ip_ioc))

# =======

empty_file_content("./melting-cobalt/sgips_iplocation.txt")
empty_file_content("./melting-cobalt/sgips_maxmind.txt")
empty_file_content("./melting-cobalt/ips.txt")
empty_file_content("./melting-cobalt/results.json.log")

sg_ioc = set()
ip_ioc = {}

with open('datasetip.txt','r') as f:
   ip_ioc = ast.literal_eval(f.read())


# check for sg ip from iplocation.net
for ip in ip_ioc:
    ip_country = get_ip_country(ip)
    print (ip_country)
    if(ip_country == "Singapore"):
        print("write ip to file")
        sg_ioc.add(ip)
        with open('./melting-cobalt/sgips_iplocation.txt', 'a') as f:
            f.write(ip + "\n")

#==========

# check for sg ip from maxmind geolite2
reader = geoip2.database.Reader('./GeoLite/GeoLite2-Country.mmdb')

for ip in ip_ioc:
    try:
        ip_country = reader.country(ip).country.iso_code
    except:
        continue
    print (ip_country)
    if(ip_country == "SG"):
        print("write ip to file")
        sg_ioc.add(ip)
        with open('./melting-cobalt/sgips_maxmind.txt', 'a') as f:
            f.write(ip + "\n")


# write sg ip to ips.txt for verification
for ip in sg_ioc:
    print(ip)
    with open('./melting-cobalt/ips.txt', 'a') as f:
        f.write(ip + "\n")

# ======

# run melting cobalt to verify if ip is a cobalt strike server
with Popen(["python", "./melting-cobalt.py", "-i", "ips.txt"], stdout=PIPE, bufsize=1, universal_newlines=True, cwd="./melting-cobalt") as p:
    for line in p.stdout:
        print(line, end='') # process line here

if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)


print("verificaiton done")

f = open('./melting-cobalt/results.json.log', 'r')
data = json.load(f)
f.close()

for eachscan in data:
    ip_info = get_ip_information(eachscan["ip"])
    eachscan["country_name"] = ip_info["country_name"]
    eachscan['isp'] = ip_info['isp']


with open("result.json", "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)

print("result is in result.json")