import os
import pandas as pd
import json
import logging
from datetime import date, datetime
from decimal import Decimal
from flask import Flask, request, jsonify, session, Response, render_template
from kiteconnect import KiteConnect
from fetchmargins import FetchMargins, FetchMarginsRequests
from putorders import PlaceMarketOrders
from InstrumentList import GetInstrumentList
from threaded_ticker import GetTickerData
from automated_system import RunSystem
from helpers import GetBNFTokens, GetATMStrike
from BNF_straddle import GetBNFStraddleTrades
from logging.config import dictConfig

logging.basicConfig(level=logging.DEBUG)
serializer = lambda obj: isinstance(obj, (date, datetime, Decimal)) and str(obj)  # noqa

PORT = 5010
HOST = "127.0.0.1"

kite_api_key = "API KEY"
kite_api_secret = "API SECRET"

redirect_url = "http://{host}:{port}/login".format(host=HOST, port=PORT)

# login_url = "https://kite.zerodha.com/connect/login?v=3&api_key={api_key}".format(api_key=kite_api_key)
login_url = "https://kite.trade/connect/login?v=3&api_key={api_key}".format(api_key=kite_api_key)
console_url = "https://developers.kite.trade/apps/{api_key}".format(api_key=kite_api_key)

app = Flask(__name__)
app.secret_key = os.urandom(24)

index_template = """<div>Make sure your app with api_key - <b>{api_key}</b> has set redirect to <b>{redirect_url}</b>.</div>
    <div>If not you can set it from your <a href="{console_url}">Kite Connect developer console here</a>.</div>
    <a href="{login_url}"><h1>Login to generate access token.</h1></a>"""

login_template = """ <h2 style="color: green">Success</h2>
    <div>Access token: <b>{access_token}</b></div>
    <h4>User login data</h4>
    <pre>{user_data}</pre>
    <a target="_blank" href="/holdings.json"><h4>Fetch user holdings</h4></a>
    <a target="_blank" href="/orders.json"><h4>Fetch user orders</h4></a>
    <a target="_blank" href="/margins.json"><h4>Fetch user margins</h4></a>
    <a target="_blank" href="/put_orders.json"><h4>Put Orders</h4></a>
    <a target="_blank" href="/positions.json"><h4>Fetch user positions</h4></a>
    <a target="_blank" href="/get_instrument_list.json"><h4>Fetch instrument list</h4></a>
    <a target="_blank" href="/get_ticker_data"><h4>Fetch ticker data</h4></a>
    <a target="_blank" href="/run_bnf_straddle_automated_system"><h4>Run BANKNIFTY straddle automated system</h4></a>
    <a target="_blank" href="https://kite.trade/docs/connect/v1/"><h4>Checks Kite Connect docs for other calls.</h4></a>
    """


def get_kite_client():
    """returns a kite client object"""
    kite = KiteConnect(api_key=kite_api_key)
    print("**********")
    print(session)
    if "access_token" in session:
        kite.set_access_token(session["access_token"])
    return kite


@app.route("/")
def index():
    return index_template.format(api_key=kite_api_key,
                                 redirect_url=redirect_url,
                                 console_url=console_url,
                                 login_url=login_url)


@app.route("/login")
def login():
    request_token = request.args.get("request_token")
    print(request_token)
    if not request_token:
        return """<span style="color: red">Error while generating request token.</span><a href='/'>
            Try again.<a>"""

    kite = get_kite_client()
    print(kite)
    print(kite.login_url())
    data = kite.generate_session(request_token, api_secret=kite_api_secret)
    print(data)
    session["access_token"] = data["access_token"]

    holdings_url = ("https://api.kite.trade/portfolio/holdings"
                    "?api_key={api_key}&access_token={access_token}").format(
        api_key=kite_api_key,
        access_token=session["access_token"])

    orders_url = ("https://api.kite.trade/orders"
                  "?api_key={api_key}&access_token={access_token}").format(
        api_key=kite_api_key,
        access_token=session["access_token"])

    # return login_template.format(
    #     access_token=data["access_token"],
    #     user_data=json.dumps(
    #         data,
    #         indent=4,
    #         sort_keys=True,
    #         default=serializer
    #     )
    # )
    return render_template('index.html',
                           access_token=data["access_token"],
                           user_data=json.dumps(
                               data,
                               indent=4,
                               sort_keys=True,
                               default=serializer
                           ))


@app.route("/holdings.json")
def holdings():
    kite = get_kite_client()
    return jsonify(holdings=kite.holdings())


@app.route("/orders.json")
def orders():
    kite = get_kite_client()
    return jsonify(orders=kite.orders())


@app.route("/positions.json")
def positions():
    kite = get_kite_client()
    return jsonify(positions=kite.positions())


@app.route("/margins.json")
def margins():
    kite = get_kite_client()
    margins = FetchMarginsRequests(session["access_token"])
    return jsonify(margins=margins)


@app.route("/put_orders.json")
def put_orders():
    order_status = PlaceMarketOrders(session["access_token"])
    return jsonify(order_status=order_status)


@app.route("/get_instrument_list.json")
def get_instrument_list():
    instrument_list = GetInstrumentList(session["access_token"])
    return jsonify(instruments=instrument_list)


@app.route("/get_ticker_data", methods=["GET"])
def get_ticker_data():
    tokens = GetBNFTokens()
    GetTickerData(session["access_token"], tokens)
    # return Response(GetTickerData(session["access_token"], tokens), mimetype="text/plain",
    #                 content_type="text/event-stream")


@app.route("/run_bnf_straddle_automated_system")
def run_automated_system():
    kite = get_kite_client()
    trades = GetBNFStraddleTrades()
    output = RunSystem(kite, session["access_token"], trades)
    # return jsonify(output=output)
    return Response(output, mimetype="text/plain", content_type="text")


if __name__ == '__main__':
    print("Starting server: http://{host}:{port}".format(host=HOST, port=PORT))
    app.run(host=HOST, port=PORT, debug=True)
