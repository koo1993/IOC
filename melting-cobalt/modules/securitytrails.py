import requests
import json
import time
API_URL = 'https://api.securitytrails.com/v1/query/scroll'

def search(search, API_KEY, log):
    open_instances = []
    data = {'query': search}
    headers = {'apikey': API_KEY, 'Content-Type': 'application/json'}
    r = requests.post(API_URL, headers=headers, data=json.dumps(data))
    r_json = r.json()

    page_number = 1
    if 'total' in r_json:
        total_results = r_json['total']['value']
    else:
        # if there are no results return 0
        total_results = 0
        log.info('Securitytrails total results: {0}'.format(total_results))
        return open_instances

    total_pages = round(total_results/100)
    # need to caculate pages from here
    log.info('Securitytrails total results: {0}'.format(total_results))
    log.info("Processing page: {0} out of {1}".format(page_number,total_pages))

    # process page 1
    r_json = r.json()
    for result in r_json['records']:
        open_instance = dict()
        if result['ports']['port']:
            log.debug("Found matching {0}:{1}".format(result['address'],",".join(str(i) for i in result['ports']['port'])))
            open_instance ['ip'] = result['address']
            open_instance['port'] = ",".join(str(i) for i in result['ports']['port'])
            open_instances.append(open_instance)

    # now paginate through the rest
    for page_number in range(2, total_pages):
        log.info("Processing page: {0} out of {1}".format(page_number,total_pages))
        if 'value' in r_json['total']:
            if (r_json['total']['value'] > 100):
                r = requests.get('https://api.securitytrails.com/v1/query/scroll/' + r_json['id'], headers=headers)
                r_json = r.json()
                for result in r_json['records']:
                    open_instance = dict()
                    if result['ports']['port']:
                        log.debug("Found matching {0}:{1}".format(result['address'],",".join(str(i) for i in result['ports']['port'])))
                        open_instance ['ip'] = result['address']
                        open_instance['port'] = ",".join(str(i) for i in result['ports']['port'])
                        open_instances.append(open_instance)
        # need to sleep to not hit api rate limits
        time.sleep(5)

    return open_instances
