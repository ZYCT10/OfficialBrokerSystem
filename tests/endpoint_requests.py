#
# Test connection to Binance API with keys and creds
#
# TODO: catch 418 errors and warn someone that we have got IP ban on Binance.
# TODO: catch 429 errors and warn someone about repeatedly reaching Binance limits.
#   Repeatedly 429-s errors will result in an automated IP ban (HTTP status 418).
#

import os
import ssl
import requests

BASE_URL = 'https://api.binance.com'
API_GW = 'api/v1/userDataStream' # for usual acc we have a api route
                                 # for corporate acc we have a sapi route
                                 # change to corp after base security settings
                                 # right now testing on my acc.
KEY = os.environ['USER_API_KEY']
URL = "{}/{}".format(BASE_URL, API_GW)


print("Connecting to url: {}".format(URL))


res = requests.post(URL, headers={'X-MBX-APIKEY': KEY})
if res.status_code == 200:
    listen_key = res.json()["listenKey"]
    print("OK: api request. code 200. listenKey: {}".format(listen_key))
else:
    print("WARNING: api request. PROBABLY BANNED IP: {}".format(res))
    for e in res: print(e)
