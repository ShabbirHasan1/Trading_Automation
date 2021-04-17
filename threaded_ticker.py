import time
import logging
from kiteconnect import KiteTicker
from functools import partial
from db import insert_ticks
# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', filename='/home/parallax/PycharmProjects/Strategy_Automation/ticks.log',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')


def on_ticks(ws, ticks):
    if len(ticks) > 0:
        # logging.info("Current Mode: {}".format(ticks[0]['mode']))
        # logging.info(ticks)
        insert_ticks.delay(ticks)
    return ticks


def on_connect(tokens, ws, response):
    # tokens = [11005954]
    logging.info("Successfully connected. Response: {}".format(response))
    ws.subscribe(tokens)
    ws.set_mode(ws.MODE_FULL, tokens)
    logging.info("Subscribe to tokens in Full mode: {}".format(tokens))


def on_close(ws, code, reason):
    logging.info("Connection closed: {code} - {reason}".format(code=code, reason=reason))


def on_error(ws, code, reason):
    logging.info("Connection error: {code} - {reason}".format(code=code, reason=reason))


def on_reconnect(ws, attempts_count):
    logging.info("Reconnecting: {}".format(attempts_count))


def on_noreconnect(ws):
    logging.info("Reconnect failed")


# def create_df(tick):


def GetTickerData(access_token, tokens):
    kws = KiteTicker('hr1osvvapq449uqf', access_token)
    # tokens = [11005954]

    kws.on_ticks = on_ticks
    kws.on_close = on_close
    kws.on_error = on_error
    kws.on_connect = partial(on_connect, tokens)
    kws.on_reconnect = on_reconnect
    kws.on_noreconnect = on_noreconnect

    kws.connect(threaded=True, disable_ssl_verification=True)
    logging.info("This is main thread. Will change webosocket mode every 5 seconds.")

    count = 0
    while True:
        if kws.is_connected():
            kws.set_mode(kws.MODE_QUOTE, tokens)

        time.sleep(1)
