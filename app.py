import os
import time
import json
from random import choices
from string import ascii_lowercase

from binance.client import Client
from flask import Flask, request, jsonify

#BROKER_API_KEY = os.environ.get("BROKER_API_KEY")
#BROKER_API_SECRET = os.environ.get("BROKER_API_SECRET")

BROKER_API_KEY = os.getenv("BROKER_API_KEY")
BROKER_API_SECRET = os.getenv("BROKER_API_SECRET")

# Generate Binance tag
def random_letters(length):
    ret = ''.join(choices(ascii_lowercase, k=length))
    return(ret)

# Need to create this objects only one time
app = Flask(__name__)
binance_client = Client(BROKER_API_KEY, BROKER_API_SECRET)

raw_cryptopairs = binance_client.get_all_tickers()
cryptopairs = [crypto_currency["symbol"] for crypto_currency in raw_cryptopairs]


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

            binance_client.make_subaccount_universal_transfer(
                toId=get_subaccount_id,
                fromAccountType="SPOT",
                toAccountType="SPOT",
                asset="USDT",
                amount=2
            )

            time.sleep(2)

            binance_client.make_subaccount_universal_transfer(
                fromId=get_subaccount_id,
                fromAccountType="SPOT",
                toAccountType="SPOT",
                asset="USDT",
                amount=2
            )

        else:
            return jsonify({500: str(res)})

        return jsonify({200: summary})

    except Exception as e:
        return jsonify({500: str(e)})


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


# Get a currency pair rate
@app.route("/getCurrency", methods=["GET"])
def get_currency():
    get_symbol = request.args.get("symbol")

    try:
        res = binance_client.get_symbol_ticker(symbol=get_symbol)

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Get the rate of all currency pairs
@app.route("/getCurrencies", methods=["GET"])
def get_currencies():
    try:
        res = binance_client.get_all_tickers()

        return jsonify({200: res})

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


@app.route("/subMasterOrder", methods=["GET"])
def sub_master_order():
    try:
        get_have = request.args.get("have")
        get_need = request.args.get("need")
        get_quantity = request.args.get("quantity")
        get_from_id = request.args.get("from_id")

        get_old_quantity = get_quantity

        if get_have + get_need in cryptopairs:
            pair = get_have + get_need
            get_side = "SELL"
            
        elif get_need + get_have in cryptopairs:
            pair = get_need + get_have
            get_side = "BUY"

        else:
            return({500: "pair can be one of: {}".format(cryptopairs)})

        get_quantity = float(get_quantity)

        if get_side != "BUY" and get_side != "SELL":
            return jsonify({500: "side can be one of: [BUY, SELL]"})

    except Exception as e:
        return jsonify({500: "Server error: {}".format(str(e))})

    # (2) Sub SPOT -> Master SPOT
    try:
        binance_client.make_subaccount_universal_transfer(
            fromId=get_from_id,
            fromAccountType="SPOT",
            toAccountType="SPOT",
            asset=get_have,
            amount=get_old_quantity
        )

    except Exception as e:
        return jsonify({500: "Error Sub SPOT -> Master SPOT: {}".format(str(e))})
    
    time.sleep(1)

    # *(2.5) Get symbol ticker
    # Replace get_quantity before order if side == SELL
    if get_side == "SELL":
        try:
            res = binance_client.get_symbol_ticker(symbol=pair)
            get_currency = float(res["price"])
            get_quantity = "{:.2f}".format(0.97 * (get_quantity * get_currency))

        except Exception as e:
            try:
                binance_client.make_subaccount_universal_transfer(
                    toId=get_from_id,
                    fromAccountType="SPOT",
                    toAccountType="SPOT",
                    asset=get_have,
                    amount=get_old_quantity
                )

            except Exception as e:
                return jsonify({500: "Double error: {}".format(str(e))})
            
            return jsonify({500: "Error getting currency from Binance: {}".format(str(e))})
    
    time.sleep(1)

    # (3) Order on master account
    try:
        res = binance_client.create_order(
            symbol=pair,
            side=get_side,
            type="MARKET",
            quoteOrderQty=get_quantity
        )

        summary = res
        
        if get_side == "SELL":
            get_need_amount = summary["cummulativeQuoteQty"]
        else:
            get_need_amount = summary["executedQty"]

    except Exception as e:
        try:
            binance_client.make_subaccount_universal_transfer(
                toId=get_from_id,
                fromAccountType="SPOT",
                toAccountType="SPOT",
                asset=get_have,
                amount=get_old_quantity
            )

        except Exception as e:
            return jsonify({500: "Double error: {}".format(str(e))})
    
        return jsonify({500: "Error in order: {}".format(str(e))})

    time.sleep(1.3)

    # (5) Master SPOT -> Sub SPOT
    try:
        res = binance_client.make_subaccount_universal_transfer(
            toId=get_from_id,
            fromAccountType="SPOT",
            toAccountType="SPOT",
            asset=get_need,
            amount=get_need_amount
        )

        return jsonify({200: summary})

    except Exception as e:
        try:
            binance_client.make_subaccount_universal_transfer(
                toId=get_from_id,
                fromAccountType="SPOT",
                toAccountType="SPOT",
                asset=get_need,
                amount=get_need_amount
            )

        except Exception as e:
            return jsonify({500: "Double error: {}".format(str(e))})

        return jsonify({500: "Error Master SPOT -> Sub SPOT {}".format(str(e))})


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


# Get a rate for a pair of currencies (safe)
@app.route("/getSafeRateCurrencyPair")
def get_safe_rate_currency_pair():
    get_first = request.args.get("first")
    get_second = request.args.get("second")

    try:
        if get_first + get_second in cryptopairs:
            pair = get_first + get_second
            res = binance_client.get_symbol_ticker(symbol=pair)

        elif get_second + get_first in cryptopairs:
            pair = get_second + get_first
            res = binance_client.get_symbol_ticker(symbol=pair)
        
        else:
            return jsonify({500: "Not found!"})

        return jsonify({200: res})
        
    except Exception as e:
        return jsonify({500: str(e)})


# Get reverse rate of currency pairs (safe)
@app.route("/getSafeRateReverseCurrencyPair", methods=["GET"])
def get_reverse_currency():
    get_first = request.args.get("first")
    get_second = request.args.get("second")

    try:
        if get_first + get_second in cryptopairs:
            pair = get_first + get_second
            res = binance_client.get_symbol_ticker(symbol=pair)

        elif get_second + get_first in cryptopairs:
            pair = get_second + get_first
            res = binance_client.get_symbol_ticker(symbol=pair)
     
        else:
            return jsonify({500: "Not found!"})

        summary = res
        reverse_currency = "{:.16f}".format(1.0 / float(res['price']))
        summary['price'] = reverse_currency
        
        return jsonify({200: summary})

    except Exception as e:
        return jsonify({500: str(e)})


# Get a rate currency (Buy/Sell)
@app.route("/rate")
def get_rate():
    get_from = request.args.get("from")
    get_to = request.args.get("to")

    try:
        if get_from + get_to in cryptopairs:
            pair = get_from + get_to
            res = binance_client.get_symbol_ticker(symbol=pair)

        elif get_to + get_from in cryptopairs:
            pair = get_to + get_from
            res = binance_client.get_symbol_ticker(symbol=pair)

            rev_curency = "{:.16f}".format(1.0 / float(res['price']))
            res['price'] = rev_curency

        else:
            return jsonify({500: "Not found!"})
    
        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Get the entire list of networks
@app.route("/wholeNetworkList")
def whole_network_list():
    try:
        res = binance_client.get_margin_all_pairs()
        res = sorted(set([el["base"] for el in res]))

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Get a list of available networks
@app.route("/allNetworks")
def all_networks():
    try:
        arr = ["BSC", "ETH", "TRX", "BTC"]

        return jsonify({200: arr})

    except Exception as e:
        return jsonify({500: str(e)})


# Get all coin list with networks
@app.route("/getAllCoinsInformation")
def get_subaccount_transfer_history():
    try:
        res = binance_client.get_all_coins_info()

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


@app.route("/getHistory", methods=["GET"])
def get_history():
    get_fromEmail = request.args.get('fromEmail')
    get_toEmail = request.args.get('toEmail')
    get_startTime = request.args.get('startTime')
    get_endTime = request.args.get('endTime')
    get_page = request.args.get("page")
    get_limit = request.args.get("limit")
    
    try:
        res = binance_client.get_sub_account_transfer_history(
              
        )
        
        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


@app.route("/getNetworksAddress", methods=["GET"])
def get_networks_address():
    get_coin = request.args.get("coin")
    get_email = request.args.get("email")

    try:
        res = []

        get_all_info = binance_client.get_all_coins_info()

        get_networks = [x for x in get_all_info if x["coin"] == get_coin]

        for get_network in get_networks[0]["networkList"]:
            try:
                get_result = binance_client.get_subaccount_deposit_address(
                    email=get_email,
                    coin=get_coin,
                    network=get_network["network"]
                )

                get_result["network"] = get_network["network"]
            
                res.append(get_result)
            except:
                pass

        return jsonify({200: res})

    except Exception as e:
        return jsonify({500: str(e)})


# Program entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12000, debug=True)
