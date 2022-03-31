#
# Test correct HMAC SHA256 signature calculating.
#
import hmac
import hashlib

def calc_hmac_sha256(params, secret_key):
    signature = hmac.new(secret_key, params, hashlib.sha256).hexdigest()
    return(signature)


total_params = b"symbol=LTCBTC&side=BUY&type=LIMIT&timeInForce=GTC&quantity=1&price=0.1&recvWindow=5000&timestamp=1499827319559"
secret_key = b"NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
signature = calc_hmac_sha256(total_params, secret_key)


if signature == "c8db56825ae71d6d79447849e617115f4a920fa2acdcab2b053c4b2838bd6b71":
    print("OK: test calculation of HMAC SHA256")
else:
    print("WARNING: HMAC SHA256 calculates wrong. \
           Probably you have upgraded Python")
