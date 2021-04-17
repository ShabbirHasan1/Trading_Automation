import time
import logging
from kiteconnect import KiteTicker
import pandas as pd
import datetime
import psycopg2
from putorders import PutOrders


def fetch_ltp(token_ce, token_pe):
    conn = psycopg2.connect(database="postgres", user="postgres", password="password", host="127.0.0.1", port="5432")
    cursor = conn.cursor()
    # current_time = datetime.datetime.now()
    cursor.execute(f"SELECT last_price from ticks where instrument_token = {token_ce} order by date desc limit 1")
    result_ce = cursor.fetchall()[0][0]

    cursor.execute(f"SELECT last_price from ticks where instrument_token = {token_pe} order by date desc limit 1")
    result_pe = cursor.fetchall()[0][0]
    return result_ce, result_pe


def RunSystem(kite, access_token):
    count = 0
    positions = kite.positions()
    instruments = pd.read_csv('instruments.csv', index_col=0)
    daily_positions = positions['day']
    for position in daily_positions:
        print(position)
        trading_symbol = position['tradingsymbol']
        if 'CE' in trading_symbol:
            pnl_ce = position['sell_value'] - position['buy_value']
            quantity_ce = position['quantity']
            multiplier_ce = position['multiplier']
            token_ce = instruments.index[instruments['tradingsymbol'] == trading_symbol].tolist()[0]
            tradingsymbol_ce = trading_symbol
        if 'PE' in trading_symbol:
            pnl_pe = position['sell_value'] - position['buy_value']
            quantity_pe = position['quantity']
            multipier_pe = position['multiplier']
            token_pe = instruments.index[instruments['tradingsymbol'] == trading_symbol].tolist()[0]
            tradingsymbol_pe = trading_symbol

    while True:
        current_time = datetime.datetime.now().time()
        trade_time = datetime.time(1, 10)
        if current_time > trade_time:
            order_status = PutOrders(access_token, 'BANKNIFTY2141532500CE', 'BANKNIFTY2141532500PE', "SELL")
            return order_status

        count = count + 1
        ltp_ce, ltp_pe = fetch_ltp(token_ce, token_pe)
        pnl_call = pnl_ce + (quantity_ce*ltp_ce*multiplier_ce)
        pnl_put = pnl_pe + (quantity_pe*ltp_pe*multipier_pe)
        total_pnl = pnl_call + pnl_put
        # print(total_pnl)
        if total_pnl < -1000 or count > 20:
            order_status = PutOrders(access_token, tradingsymbol_ce, tradingsymbol_pe, "BUY")
            return order_status
        time.sleep(1)







