import logging
from kiteconnect import KiteConnect
import json
import requests

logging.basicConfig(level=logging.DEBUG)


def PlaceMarketOrders(access_token, tradingsymbol, transaction_type, product_type, quantity):
    API_URL = "https://api.kite.trade/orders/regular"

    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token hr1osvvapq449uqf:{access_token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    payload = {
        "exchange": "NFO",
        "tradingsymbol": tradingsymbol,
        "transaction_type": transaction_type,
        "product": product_type,
        "order_type": "MARKET",
        "quantity": quantity,
        "validity": "DAY"
    }

    r = requests.post(API_URL, headers=headers, data=payload)
    response = json.loads(r.text)
    res = json.dumps(response)
    return res
