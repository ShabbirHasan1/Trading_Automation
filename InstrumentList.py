import logging
from kiteconnect import KiteConnect
import json
import pandas as pd
from io import StringIO
import requests

logging.basicConfig(level=logging.DEBUG)


def GetInstrumentList(access_token):
    API_URL = "https://api.kite.trade/instruments"

    headers = {
        'X-Kite-Version': '3',
        'Authorization': f'token hr1osvvapq449uqf:{access_token}',
        'Content-Type': 'application/json'
    }

    r = requests.get(API_URL, headers=headers)
    # print(r.text)
    df = pd.read_csv(StringIO(r.text))
    print(df)
    df.to_csv('instruments.csv', index=False)
