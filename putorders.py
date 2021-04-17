import logging
from kiteconnect import KiteConnect
import json
import requests

logging.basicConfig(level=logging.DEBUG)


def PutOrders(access_token, tradingsymbol_ce, tradingsymbol_pe, order_type, quantity):
    API_URL = "https://api.kite.trade/orders/regular"

    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token hr1osvvapq449uqf:{access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payloads = [{
        "exchange": "NFO",
        "tradingsymbol": tradingsymbol_ce,
        "transaction_type": order_type,
        "product": "MIS",
        "order_type": "MARKET",
        "quantity": quantity,
        "validity": "DAY"
    },
        {
        "exchange": "NFO",
        "tradingsymbol": tradingsymbol_pe,
        "transaction_type": order_type,
        "product": "MIS",
        "order_type": "MARKET",
        "quantity": quantity,
        "validity": "DAY"
        }]

    orders_response = []
    for payload in payloads:
        r = requests.post(API_URL, headers=headers, data=payload)
        response = json.loads(r.text)
        orders_response.append(response)
    print(orders_response)
    res = json.dumps(orders_response)
    return res
