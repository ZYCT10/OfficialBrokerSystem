#
# Time sync between environment and Binance servers.
# Fails if there is difference between Binance time and
#  local environment time more than 5000 ms.
#
import re
import json
import time
from subprocess import Popen, PIPE


# Time on local PC
def local_time():
    return(int(time.time() * 1000))

# Simple bash interpreter
def unix(command):
    # Also catching stderror
    output = command + " 2>&1"
    res, err = Popen(output, shell = True,
                     stdout = PIPE, stderr = PIPE).communicate()
    return(res.decode())

# Request and extract Binance server time
def binance_time(command):
    res = unix(command)
    res_json = json.loads(re.findall(r'[\{][^\n]*', res)[0])
    return(int(res_json["serverTime"]))


command = 'curl -X GET "https://api.binance.com/api/v3/time"'

difference = abs(binance_time(command) - local_time())
if difference < 5000: # In milliseconds
    print("OK: time sync with Binance. Diff: {}".format(difference))
else:
    print("WARNING: Time unsynced with Binance: {}".format(difference))
