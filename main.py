from TwitterHandler import *
from KeysConstant import *
from ShodanHandler import *
import geoip2.database
# to import back dataset
import ast
from subprocess import Popen, PIPE, CalledProcessError


# todo: organise code

# preload maxmind_database
maxmind_database = geoip2.database.Reader('./GeoLite/GeoLite2-Country.mmdb')

def get_ip_country(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()['country_name']


def get_ip_information(ips):
    r = requests.get("https://api.iplocation.net/?ip=" + ips)
    return r.json()

def get_maxmind_ip_information(ip):
    ip_country = "None"
    try:
        ip_country = maxmind_database.country(ip).country.iso_code
    except:
        pass
    return ip_country


def empty_file_content(filelocation):
    open(filelocation, 'w').close()


def update_cobaltstrike_ip_tracker(list_ip):
    ip_temp = set()

    try:
        with open('CobaltStrikeSGIPTracker.txt', 'r') as f:
            ip_temp = ast.literal_eval(f.read())
    except:
        print()  # do nth

    ip_temp.update(list_ip)
    with open('CobaltStrikeSGIPTracker.txt', 'w') as f:
        f.write(str(ip_temp))


# === start
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

with open('datasetip.txt', 'r') as f:
    ip_ioc = ast.literal_eval(f.read())

# check for sg ip from iplocation.net
for ip in ip_ioc:
    ip_country = get_ip_country(ip)
    print("iplocation.net: " + ip + " " + ip_country)
    if (ip_country == "Singapore"):
        print("write ip to file")
        sg_ioc.add(ip)
        with open('./melting-cobalt/sgips_iplocation.txt', 'a') as f:
            f.write(ip + "\n")

# ==========

# check for sg ip from maxmind geolite2
reader = geoip2.database.Reader('./GeoLite/GeoLite2-Country.mmdb')

for ip in ip_ioc:
    ip_country = get_maxmind_ip_information(ip)
    print("maxmind: " + ip + " " + ip_country)
    if (ip_country == "SG"):
        sg_ioc.add(ip)
        with open('./melting-cobalt/sgips_maxmind.txt', 'a') as f:
            f.write(ip + "\n")


twitter_cs_sgip = sg_ioc.copy()


#fetch sg ip that shodan indicates cobalt strike
shodan_cs_sgip = get_from_shodan()

#condense all ip into on common list
sg_ioc.update(shodan_cs_sgip)

# add sg ip from previous sg ip tracker to sg_ioc
try:
    with open('CobaltStrikeSGIPTracker.txt', 'r') as f:
        ip_temp = ast.literal_eval(f.read())
        sg_ioc.update(ip_temp)
except:
    print()  # do nth


# write sg ip to ips.txt for verification
for ip in sg_ioc:
    print("sg ip: " + ip)
    with open('./melting-cobalt/ips.txt', 'a') as f:
        f.write(ip + "\n")


# ======

# run melting cobalt to verify if ip is a cobalt strike server
with Popen(["python", "./melting-cobalt.py", "-i", "ips.txt"], stdout=PIPE, bufsize=1, universal_newlines=True,
           cwd="./melting-cobalt") as p:
    for line in p.stdout:
        print(line, end='')  # process line here
if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)

print("verificaiton done")

# enrich ip with country_name, isp name
cs_ioc = set()
f = open('./melting-cobalt/results.json.log', 'r')
data = json.load(f)
f.close()

shortened_json = []

for eachscan in data:
    ip = eachscan["ip"]
    cs_ioc.add(ip)
    ip_info = get_ip_information(ip)
    eachscan["country_iplocation_net"] = ip_info["country_name"]
    eachscan['isp_iplocation_net'] = ip_info['isp']

    maxmind_ip_loc = get_maxmind_ip_information(ip)
    eachscan['country_maxmind'] = maxmind_ip_loc

    #trace which source this ip is from
    ip_loc = get_ip_country(ip)
    ip_source = ""
    if ip in twitter_cs_sgip:
        ip_source = ip_source + "twitter "
    if ip in shodan_cs_sgip:
        ip_source = ip_source + "shodan "
    if ip_source.__eq__(""):
        ip_scource = ip_scource + "SGIPTracker.txt"
    eachscan['ip_source'] = ip_source

    element = {}
    element["ip"] = eachscan["ip"]
    element["ip_source"] = eachscan["ip_source"]
    element["country_iplocation_net"] = eachscan["country_iplocation_net"]
    element["isp_iplocation_net"] = eachscan["isp_iplocation_net"]
    element["country_maxmind"] = eachscan["country_maxmind"]
    shortened_json.append(element)

with open("result.json", "w") as f:
    json.dump(data, f, indent=4, sort_keys=True)

with open("result_shorten.json", "w") as f:
    json.dump(shortened_json, f, indent=4, sort_keys=True)



update_cobaltstrike_ip_tracker(cs_ioc)

print("result is in result.json")
