import sys
import time
from subprocess import Popen, PIPE


# Simple bash interpreter
def unix(command):
    # Also catching stderror
    output = command + " 2>&1"
    res, err = Popen(output, shell = True,
                     stdout = PIPE, stderr = PIPE).communicate()
    return(res.decode())


tests = ['python3 release.py']

for test in tests:
    print("{}:\n{}".format(test, unix(test)))
    time.sleep(1)
