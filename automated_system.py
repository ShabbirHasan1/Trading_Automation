import os
import sys
import time
import logging
from kiteconnect import KiteTicker
import pandas as pd
import datetime
import psycopg2
from putorders import PutOrders
from threaded_ticker import GetTickerData
from helpers import GetCurrentWeeklyOptions, fetch_ltp, GetATMStrike, FetchPositionsInfo, GetBNFTokens, GetStoplossTargetValues


def RunSystem(kite, access_token, lots):
    trade_start_time = datetime.time(9, 45)
    trade_end_time = datetime.time(14, 15)
    positions_info = FetchPositionsInfo(kite)

    # this takes care of restartng from middle runs
    if not positions_info:
        position_flag = False
    else:
        position_flag = True

    fixed_stoploss = -3000
    stoploss = 0
    target = 0
    step = 0
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= trade_start_time and position_flag == False:
            atm_strike = GetATMStrike('NIFTY BANK')
            contract_ce, contract_pe = GetCurrentWeeklyOptions(atm_strike, 'BANKNIFTY')
            order_status = PutOrders(access_token, contract_ce, contract_pe, "SELL", 25*lots)
            print(order_status)
            if order_status[0]['status'] == 'success' and order_status[1]['status'] == 'success':
                positions_info = FetchPositionsInfo(kite)
                stoploss, target, step = GetStoplossTargetValues(positions_info)
                position_flag = True
            else:
                continue

        # uncomment this for subsequent iteranious without putting orders
        if positions_info:
            positions_info = FetchPositionsInfo(kite)
            stoploss, target, step = GetStoplossTargetValues(positions_info)

        pnl=0
        print(f"CURRENT TIME: {current_time} ")
        for instrument, instrument_info in positions_info.items():
            ltp = fetch_ltp(instrument_info['token'])
            print(f"{instrument} ltp: {ltp}")
            pnl = pnl + instrument_info['value_change'] + (instrument_info['quantity']*ltp*instrument_info['multiplier'])

        print(f"pnl = {pnl}")
        print(f"fixed stoploss = {fixed_stoploss}")
        print(f"stoploss = {stoploss}")
        print(f"target = {target}")
        time.sleep(2)
        os.system('clear')

        # stoploss = -10000
        instruments = list(positions_info.keys())
        if pnl < fixed_stoploss or pnl < stoploss:
            order_status = PutOrders(access_token, instruments[0], instruments[1], "BUY", 25*lots)
            return order_status
        elif pnl >= target:
            stoploss = stoploss + step
            target = target + step
        elif current_time >= trade_end_time:
            order_status = PutOrders(access_token, instruments[0], instruments[1], "BUY", 25*lots)
            return order_status

        time.sleep(1)







