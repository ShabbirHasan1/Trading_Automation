import pandas as pd
import json
from nsepy.derivatives import get_expiry_date
from datetime import datetime
import psycopg2
import requests
import math


def fetch_ltp(token):
    conn = psycopg2.connect(database="postgres", user="postgres", password="password", host="127.0.0.1", port="5432")
    cursor = conn.cursor()
    # current_time = datetime.datetime.now()
    cursor.execute(f"SELECT last_price from ticks where instrument_token = {token} order by date desc limit 1")
    result = cursor.fetchall()[0][0]
    return result


def GetCurrentWeekExpiry():

    now = datetime.now().date()
    curr_year = now.year
    curr_month = now.month
    month_expiries = get_expiry_date(year=curr_year, month=curr_month)
    closest_expiry = datetime(2050, 1, 1).date()
    month_expiries.add(datetime(2021, 4, 22).date())
    for date in month_expiries:
        if date >= now:
            closest_expiry = min(date, closest_expiry)
    expiry_year = str(closest_expiry.year)[2:]
    expiry_month = str(closest_expiry.month).replace('0', '')
    expiry_day = str(closest_expiry.day)
    expiry = expiry_year + expiry_month + expiry_day
    return expiry


def GetCurrentWeeklyOptions(strike_price=None, symbol=None):
    # 'BANKNIFTY2141532500CE'
    expiry = GetCurrentWeekExpiry()
    contract_ce = symbol + expiry + str(strike_price) + 'CE'
    contract_pe = symbol + expiry + str(strike_price) + 'PE'

    # contract_ce = 'BANKNIFTY2142230500CE'
    # contract_pe = 'BANKNIFTY2142230500PE'
    print(contract_ce)
    print(contract_pe)
    return contract_ce, contract_pe


def GetATMStrike(symbol):
    instruments = pd.read_csv('instruments.csv', index_col=0)
    token = instruments.index[instruments['tradingsymbol'] == symbol].tolist()[0]
    ltp = fetch_ltp(token)
    strike_price = int(math.ceil(ltp / 100.0)) * 100
    return strike_price
    # print(strike_price)


def GetBNFTokens():
    instruments = pd.read_csv('instruments.csv', index_col=0)
    expiry = GetCurrentWeekExpiry()
    tokens = []
    token_BNF = instruments.index[instruments['tradingsymbol'] == 'NIFTY BANK'].tolist()[0]
    tokens.append(token_BNF)
    BNFOptions = instruments[instruments['tradingsymbol'].str.contains("BANKNIFTY"+expiry)]
    tokens = BNFOptions.index.tolist()
    tokens.append(token_BNF)
    return tokens


def FetchPositionsInfo(kite):
    instruments = pd.read_csv('instruments.csv', index_col=0)
    positions = kite.positions()
    daily_positions = positions['day']
    positions_info = {}
    if len(daily_positions) != 0:
        for position in daily_positions:
            individual_info = {}
            trading_symbol = position['tradingsymbol']
            individual_info['value_change'] = position['sell_value'] - position['buy_value']
            individual_info['quantity'] = position['quantity']
            individual_info['multiplier'] = position['multiplier']
            individual_info['token'] = instruments.index[instruments['tradingsymbol'] == trading_symbol].tolist()[0]
            individual_info['tradingsymbol'] = trading_symbol
            positions_info[trading_symbol] = individual_info

    return positions_info


def GetStoplossTargetValues(positions_info):
    combined_premium = 0
    for instrument, instrument_info in positions_info.items():
        ltp = fetch_ltp(instrument_info['token'])
        combined_premium = combined_premium + ltp
        quantity = abs(instrument_info['quantity'])

    stoploss = -0.10 * quantity * combined_premium
    target = 0.10 * quantity * combined_premium
    step = 0.10 * quantity * combined_premium
    return stoploss, target, step



























import time
import datetime
import json
import time

from helpers import GetCurrentWeeklyOptions, fetch_ltp, GetATMStrike, FetchPositionsInfo, GetStoplossTargetValues
from putorders import PlaceMarketOrders


def RunSystem(kite, access_token, lots):
    trade_start_time = datetime.time(18, 45)
    trade_end_time = datetime.time(14, 45)

    fixed_stoploss = -3000
    stoploss = 0
    target = 0
    step = 0

    positions_info = FetchPositionsInfo(kite)

    # this takes care of restartng from middle runs
    if not positions_info:
        position_flag = False
    else:
        #TODO Change this to true
        position_flag = False
        positions_info = FetchPositionsInfo(kite)
        stoploss, target, step = GetStoplossTargetValues(positions_info)

    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= trade_start_time and position_flag == False:
            atm_strike = GetATMStrike('NIFTY BANK')
            contract_ce, contract_pe = GetCurrentWeeklyOptions(atm_strike, 'BANKNIFTY')
            order_status_ce = PlaceMarketOrders(access_token, contract_ce, "SELL", "MIS", 25 * lots)
            print(order_status_ce)
            yield order_status_ce + "\n"
            order_status = json.loads(order_status_ce)

            if order_status['status'] == 'success' and order_status['status'] == 'success':
                positions_info = FetchPositionsInfo(kite)
                stoploss, target, step = GetStoplossTargetValues(positions_info)
                position_flag = True
            else:
                """remove this"""
                # position_flag = True
                continue

        pnl = 0
        yield f"CURRENT TIME: {current_time}" + "\n"
        for instrument, instrument_info in positions_info.items():
            ltp = fetch_ltp(instrument_info['token'])
            print(f"{instrument} ltp: {ltp}")
            pnl = pnl + instrument_info['value_change'] + (
                    instrument_info['quantity'] * ltp * instrument_info['multiplier'])

        yield f"pnl = {pnl}" + "\n"
        yield f"fixed stoploss = {fixed_stoploss}" + "\n"
        yield f"stoploss = {stoploss}" + "\n"
        yield f"target = {target}" + "\n"
        # time.sleep(2)
        # os.system('clear')

        # stoploss = -10000
        instruments = list(positions_info.keys())
        if pnl < fixed_stoploss or pnl < stoploss:
            order_status = PlaceMarketOrders(access_token, instruments[0], "BUY", "MIS", 25 * lots)
            return order_status
        elif pnl >= target:
            stoploss = stoploss + step
            target = target + step
        elif current_time >= trade_end_time:
            order_status = PlaceMarketOrders(access_token, instruments[0], "BUY", "MIS", 25 * lots)
            return order_status

        time.sleep(1)
