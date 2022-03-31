#
# Test connection to Binance apis using requests
# If something goes wrong with Binance, you can try
#  fastly change api gw somewhere in other script to
#  one of working from that script.
#

import time
import requests


URLS = ['https://api.binance.com',
        'https://api1.binance.com',
        'https://api2.binance.com',
        'https://api3.binance.com']

for url in URLS:
    res = requests.get(url)

    if "Test OK" not in res.text:
        print("UNAVAILABLE: {}".format(url))
    else:
        print("OK: {}".format(url))

    time.sleep(1)
