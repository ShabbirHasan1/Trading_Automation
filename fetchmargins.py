import logging
from kiteconnect import KiteConnect
import json
import requests

logging.basicConfig(level=logging.DEBUG)

# kite = KiteConnect(api_key='hr1osvvapq449uqf')

def FetchMargins(kite):
    order_param_single = [
        {
            "exchange": "NFO",
            "tradingsymbol": "BANKNIFTY2140832700CE",
            "transaction_type": "SELL",
            "variety": "regular",
            "product": "MIS",
            "order_type": "MARKET",
            "quantity": 25,
            "price": 0,
            "trigger_price": 0
        },
        {
            "exchange": "NFO",
            "tradingsymbol": "BANKNIFTY2140832700PE",
            "transaction_type": "SELL",
            "variety": "regular",
            "product": "MIS",
            "order_type": "MARKET",
            "quantity": 25,
            "price": 0,
            "trigger_price": 0
        }
    ]

    margin_details = kite.order_margins(order_param_single)
    return margin_details


def FetchMarginsRequests(access_token):
    API_URL = "https://api.kite.trade/margins/basket?consider_positions=true"
    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token hr1osvvapq449uqf:{access_token}',
        'Content-Type': 'application/json'
    }
    payload = [{
        "exchange": "NFO",
        "tradingsymbol": "BANKNIFTY2141532500CE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "MIS",
        "order_type": "MARKET",
        "quantity": 25,
        "price": 0,
        "trigger_price": 0
    },
    {
        "exchange": "NFO",
        "tradingsymbol": "BANKNIFTY2141532500PE",
        "transaction_type": "SELL",
        "variety": "regular",
        "product": "MIS",
        "order_type": "MARKET",
        "quantity": 25,
        "price": 0,
        "trigger_price": 0
    }
    ]
    r = requests.post(API_URL, headers=headers, json=payload)
    response_json = json.loads(r.text)
    return response_json
