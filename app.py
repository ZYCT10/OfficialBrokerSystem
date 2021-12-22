#
# Main entry point to the backend module.
# This module provides Binance api calls and cryptocurrency exchange.
#
# Example running:
# flask run -p 6125
#
# TODO: Need to listen on routes and pass only verified calls.
# TODO: Need to verify calls (they should at least contain real user id)
#
# On this side we also need:
# TODO: Catch 418's from Binance and immediately warn about it in some way
# TODO: Catch 403's from Binance and warn about it in some way.
# TODO: Contain requests to Binance in some kind of queue
# TODO: Catch 429's from Binance and jump on other API-KEY.
# TODO: Also we can accumulate requests weight and move requests to queue.

import os
import time
from random import choices
from string import ascii_lowercase

from binance.client import Client
from flask import Flask, request, jsonify

BROKER_API_KEY = os.environ.get("BROKER_API_KEY")
BROKER_API_SECRET = os.environ.get("BROKER_API_SECRET")

# Generate Binance tag
def random_letters(length):
    ret = ''.join(choices(ascii_lowercase, k=length))
    return(ret)

# Need to create this objects only one time
app = Flask(__name__)
binance_client = Client(BROKER_API_KEY, BROKER_API_SECRET)

raw_cryptopairs = binance_client.get_all_tickers()
cryptopairs = [e["symbol"] for e in raw_cryptopairs]

#   Routes in Flask - special kind of the functions that
##  listen calls to URI's on the server. They can get
### request params and call another object code.

# Test route
@app.route("/")
def test():
    return(jsonify({200: "Test ok o..o"}))


# Get master account information
@app.route("/getAccount")
def get_account():
    try:
        res = binance_client.get_account()

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Create subaccount, enable futures.
@app.route("/createSubaccount")
def create_subaccount():
    try:
        res = binance_client.create_broker_sub_account(tag=random_letters(12))

        if "subaccountId" in res:
            get_subaccount_id = res["subaccountId"]
            summary = res

            time.sleep(1)

            res = binance_client.enable_subaccount_futures(subAccountId=get_subaccount_id, futures="true")
            summary.update(res)

        else:
            return jsonify({500: str(res)})

        return jsonify({200: summary})

    except Exception as e:
        return jsonify({500: str(e)})


# Activate subaccount futures
@app.route("/enableFutures")
def enable_futures():
    try:
        get_subaccount_id = request.args.get("subaccount_id")
        res = binance_client.enable_subaccount_futures(subAccountId=get_subaccount_id, futures="true")

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Create assets
@app.route("/createAssets")
def create_assets():
    get_on_id = request.args.get("on_id")

    # (1) -> Sub Future
    try:
        binance_client.make_subaccount_universal_transfer(
            toId=get_on_id,
            fromAccountType="SPOT",
            toAccountType="USDT_FUTURE",
            asset="USDT",
            amount=2
        )

    except Exception as e:
        return jsonify({500: "Error Master SPOT -> Sub Future: {}".format(str(e))})

    time.sleep(1.3)

    # (2) Sub Future -> Sub SPOT
    try:
        binance_client.make_subaccount_universal_transfer(
            fromId=get_on_id,
            toId=get_on_id,
            fromAccountType="USDT_FUTURE",
            toAccountType="SPOT",
            asset="USDT",
            amount=2
        )

    except Exception as e:
        return jsonify({500: "Error Sub Future -> Sub SPOT: {}".format(str(e))})

    time.sleep(0.8)

    # (3) Sub SPOT -> Sub Future
    try:
        binance_client.make_subaccount_universal_transfer(
            fromId=get_on_id,
            toId=get_on_id,
            fromAccountType="SPOT",
            toAccountType="USDT_FUTURE",
            asset="USDT",
            amount=2
        )
        
    except Exception as e:
        return jsonify({500: "Error Sub SPOT -> Sub Future: {}".format(str(e))})

    time.sleep(1.3)

    # (4) Sub Future -> Master SPOT
    try:
        binance_client.make_subaccount_universal_transfer(
            fromId=get_on_id,
            fromAccountType="USDT_FUTURE",
            toAccountType="SPOT",
            asset="USDT",
            amount=2
        )
        
        return jsonify({200: "Created"})

    except Exception as e:
        return jsonify({500: "Error Sub Future -> Master SPOT: {}".format(str(e))})


# Get subaccount list
@app.route("/getSubaccountList")
def get_subaccounts():
    try:
        res = binance_client.get_sub_account_list()

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Get subaccount balance (there is some other balance types in docs)
@app.route("/getSubaccountAssets", methods=["GET"])
def get_subacc_assets():
    get_email = request.args.get("email")
    
    try:
        res = binance_client.get_sub_account_assets(email=get_email, version="v3")

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Get currency. In original library this method gets all cryptocurrencies
# and get needed one from JSON.
# This method would be called very often so we can call it periodically in
# other place and contain cryptocurrincies in Redis, so we don't need to
# make a real calls to Binance api's.
@app.route("/getCurrency", methods=["GET"])
def get_currency():
    get_symbol = request.args.get("symbol")

    try:
        res = binance_client.get_symbol_ticker(symbol=get_symbol)

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


@app.route("/getCurrencies", methods=["GET"])
def get_currencies():
    try:
        res = binance_client.get_all_tickers()

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})
 

@app.route("/getReverseCurrency", methods=["GET"])
def get_reverse_currency():
    get_symbol = request.args.get("symbol")

    try:
        res = binance_client.get_symbol_ticker(symbol=get_symbol)
        summary = res
        reverse_currency = "{:.16f}".format(1.0 / float(res['price']))
        summary['price'] = reverse_currency

        return jsonify({200: summary})

    except Exception as e:
        return jsonify({500: str(e)})


# Get subaccount deposit address (need to check if we can simply use it for input money transfer)
@app.route("/getSubaccountDepositAddress", methods=["GET"])
def get_subaccount_deposit_address():
    get_email = request.args.get("email")
    get_coin = request.args.get("coin")
    get_network = request.args.get("network")

    try:
        res = binance_client.get_subaccount_deposit_address(
            email=get_email,
            coin=get_coin,
            network=get_network
        )

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Master -> Sub withdraw
@app.route("/withdrawOnSubaccount", methods=["GET"])
def withdraw_on_subaccount():
    get_to_id = request.args.get("to_id")
    get_from_type = request.args.get("from_type")
    get_to_type = request.args.get("to_type")
    get_asset = request.args.get("asset")
    get_amount = request.args.get("amount")

    try:
        res = binance_client.make_subaccount_universal_transfer(
            toId=get_to_id,
            fromAccountType=get_from_type,
            toAccountType=get_to_type,
            asset=get_asset,
            amount=get_amount
        )

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Sub -> sub withdraw
@app.route("/withdrawSubToSub", methods=["GET"])
def withdraw_sub_to_sub():
    get_from_id = request.args.get("from_id")
    get_to_id = request.args.get("to_id")
    get_from_type = request.args.get("from_type")
    get_to_type = request.args.get("to_type")
    get_asset = request.args.get("asset")
    get_amount = request.args.get("amount")

    try:
        res = binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            toId=get_to_id,
            fromAccountType=get_from_type,
            toAccountType=get_to_type,
            asset=get_asset,
            amount=get_amount
        )
        
        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Sub -> Master withdraw
@app.route("/withdrawOnMaster", methods=["GET"])
def withdraw_to_master():
    get_from_id = request.args.get("from_id")
    get_from_type = request.args.get("from_type")
    get_to_type = request.args.get("to_type")
    get_asset = request.args.get("asset")
    get_amount = request.args.get("amount")

    try:
        res = binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            fromAccountType=get_from_type,
            toAccountType=get_to_type,
            asset=get_asset,
            amount=get_amount
        )

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Call binance order endpoint
@app.route("/newOrder", methods=["GET"])
def new_order():
    get_pair = request.args.get("symbol")
    get_side = request.args.get("side")
    get_quantity = request.args.get("quantity")

    try:
        get_quantity = float(get_quantity)

        res = binance_client.create_order(
            symbol=get_pair,
            side=get_side,
            type="MARKET",
            quoteOrderQty=get_quantity
        )

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Transfer from Sub, order on Master, and transfer back
@app.route("/subMasterOrder")
def sub_master_order():
    try: 
        get_have = request.args.get("have")
        get_need = request.args.get("need")
        get_quantity = request.args.get("quantity")
        get_from_id = request.args.get("from_id")
        futures_type = "COIN_FUTURE"
  
        if get_have + get_need in cryptopairs:
            pair = get_have + get_need
            get_side = "SELL"
        
        elif get_need + get_have in cryptopairs:
            pair = get_need + get_have
            get_side = "BUY"

        else:
            return({500: "pair can be one of: {}".format(cryptopairs)})

        get_quantity = float(get_quantity)

        if get_have == "USDT": # Change futures type in case of USDT
            futures_type = "USDT_FUTURE"
        
        if get_side != "BUY" and get_side != "SELL":
            return jsonify({500: "side can be one of: [BUY, SELL]"})

    except Exception as e:
        return jsonify({500: "Server error: {}".format(str(e))})

    # (1) Sub SPOT -> Sub Future
    try:
        res = binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            toId=get_from_id,
            fromAccountType="SPOT",
            toAccountType=futures_type,
            asset=get_have,
            amount=get_quantity
        )

    except Exception as e:
        return jsonify({500: "Error Sub SPOT -> Sub Future: {}".format(str(e))})

    time.sleep(1.3)

    # (2) Sub Future -> Master SPOT
    try:
        res = binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            fromAccountType=futures_type,
            toAccountType="SPOT",
            asset=get_have,
            amount=get_quantity
        )

    except Exception as e:
        return jsonify({500: "Error Sub Future -> Master SPOT: {}".format(str(e))})

    time.sleep(1)

    # *(2.5) Get symbol ticker
    # Replace get_quantity before order if side == SELL
    if get_side == "SELL":
        try:
            res = binance_client.get_symbol_ticker(symbol=pair)
            get_currency = float(res["price"])
            get_quantity = "{:.2f}".format(0.97 * (get_quantity * get_currency))

        except Exception as e:
            return jsonify({500: "Error getting currency from Binance: {}".format(str(e))})

    # (3) Order on master account
    try:
        res = binance_client.create_order(
            symbol=pair,
            side=get_side,
            type="MARKET",
            quoteOrderQty=get_quantity
        )

        summary = res
        get_need_amount = summary["executedQty"]

    except Exception as e:
        return jsonify({500: "Error in order: {}".format(str(e))})

    time.sleep(1.5)

    # (4) -> Sub Future
    # Change futures type on runtime if needed
    if get_need == "USDT": # Change futures type in case of USDT
        futures_type = "USDT_FUTURE"
        
    # Change amount to transfer on runtime
    if get_side == "SELL":
        get_need_amount = get_quantity

    try:
        res = binance_client.make_subaccount_universal_transfer(
            toId=get_from_id,
            fromAccountType="SPOT",
            toAccountType=futures_type,
            asset=get_need,
            amount=get_need_amount
        )

    except Exception as e:
        return jsonify({500: "Error Master SPOT -> Sub Future {}".format(str(e))})

    time.sleep(1.3)

    # (5) Sub Future -> Sub SPOT
    try:
        res = binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            toId=get_from_id,
            fromAccountType=futures_type,
            toAccountType="SPOT",
            asset=get_need,
            amount=get_need_amount
        )

        return jsonify({200: summary})

    except Exception as e:
        return jsonify({500: "Error Sub Future -> Sub SPOT {}".format(str(e))})


# Withdraw outside (BSC)
@app.route("/withdraw", methods=["GET"])
def withdraw():
    coin = request.args.get("coin")
    network = request.args.get("network")
    address = request.args.get("address")
    amount = request.args.get("amount")

    try:
        res = binance_client.withdraw(
            coin=coin,
            network=network,
            address=address,
            amount=float(amount)
        )

        return jsonify({200: res})
    
    except Exception as e:
        return jsonify({500: str(e)})

@app.route("/allPairs")
def all_pairs():
    try:
        res = binance_client.get_margin_all_pairs()
        res = sorted(set([el["base"] for el in res]))

        return jsonify({200: res})
    
    except Exception as e:
        return jsonify({500: str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)