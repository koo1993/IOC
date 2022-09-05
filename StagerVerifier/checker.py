
import requests
import tempfile
from subprocess import call
import argparse

parser = argparse.ArgumentParser(description='Download stager and evaluate against 1768.py')
parser.add_argument("-u", "--URI", type=str, required=True, help='FULL URI')

args = parser.parse_args()

url = args.URI

x = requests.get(url, verify=False)

with tempfile.NamedTemporaryFile() as tmp:
    tmp.write(x.content)
    call(["python3", "1768.py", tmp.name])
