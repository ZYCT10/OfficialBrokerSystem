import os
import time
import json
import requests

URL_ADDRESS = os.environ['URL_ADDRESS']

def test_main_page():
    r = requests.get(f"{URL_ADDRESS}/")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_account():
    r = requests.get(f"{URL_ADDRESS}/getAccount")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_create_subaccount():
    r = requests.get(f"{URL_ADDRESS}/createSubaccount")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_create_assets(on_id):
    r = requests.get(f"{URL_ADDRESS}/createAssets?on_id={on_id}")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_subaccount_list():
    r = requests.get(f"{URL_ADDRESS}/getSubaccountList")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_subaccount_assets(email):
    r = requests.get(f"{URL_ADDRESS}/getSubaccountAssets?email={email}")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_currency(symbol):
    r = requests.get(f"{URL_ADDRESS}/getCurrency?symbol={symbol}")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_currencies():
    r = requests.get(f"{URL_ADDRESS}/getCurrencies")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_reverse_currency(symbol):
    r = requests.get(f"{URL_ADDRESS}/getReverseCurrency?symbol={symbol}")

    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


def test_get_subaccount_deposit_address(email, coin):
    r = requests.get(f"{URL_ADDRESS}/getSubaccountDepositAddress?email={email}&coin={coin}")
    get_json = json.loads(r.text)
    status_ok = "200" in get_json.keys()

    if status_ok:
        return (True, get_json["200"])
    else:
        return (False, )


if __name__ == "__main__":
    main_page = test_main_page()
    print(f"[/] - {main_page[0]}")

    time.sleep(1.2)

    get_account = test_get_account()
    print(f"[/getAccount] - {get_account[0]}")

    time.sleep(0.7)

    create_subaccount = test_create_subaccount()
    print(f"[/createSubaccount] - {create_subaccount[0]}")

    time.sleep(1.1)

    create_assets = test_create_assets(create_subaccount[1]["subaccountId"]) if create_subaccount[0] else (False, )
    print(f"[/createAssets] - {create_assets[0]}")

    time.sleep(0.9)

    get_subaccount_list = test_get_subaccount_list()
    print(f"[/getSubaccountList] - {get_subaccount_list[0]}")

    time.sleep(1.3)

    get_subaccount_assets = test_get_subaccount_assets(create_subaccount[1]["email"]) if create_subaccount[0] else (False, )
    print(f"[/getSubaccountAssets] - {get_subaccount_assets[0]}")

    time.sleep(0.9)

    get_currency = test_get_currency('BTCUSDT')
    print(f"[/getCurrency] - {get_currency[0]}")

    time.sleep(1.2)

    get_currencies = test_get_currencies()
    print(f"[/getCurrencies] - {get_currencies[0]}")

    time.sleep(1.0)

    get_reverse_currency = test_get_reverse_currency('BTCUSDT')
    print(f"[/getReverseCurrency] - {get_reverse_currency[0]}")
