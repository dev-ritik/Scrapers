import datetime
import json
import os
import sys

import requests

# Class of different styles
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


paths = sys.argv[1:]

PAGE = paths[0]
print(PAGE)

url = "https://internet.channeli.in/api/noticeboard/new/?page=%d" % int(PAGE)

payload = {}
headers = {
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'DNT': '1',
    'Accept': '*/*',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://internet.channeli.in/noticeboard/',
    'Accept-Language': 'en-US,en;q=0.9,hi-IN;q=0.8,hi;q=0.7,he-IL;q=0.6,he;q=0.5',
    'Cookie': '<cookie>'
}

response = requests.request("GET", url, headers=headers, data=payload)
parsed = response.json()
# print(json.dumps(parsed, indent=4, sort_keys=True))
if len(parsed["results"]) > 1:
    print("Processing")
for result in parsed["results"]:
    if result["banner"]["name"] == "Placement & Internship Cell":
        print("https://internet.channeli.in/noticeboard/notice/%s" % str(result["id"]).strip())
        print(style.BLUE + result["title"] + style.RESET)
        print(datetime.datetime.fromisoformat(result["datetimeCreated"]).strftime("%d %b, %Y , %H:%M:%S"))
        print()
