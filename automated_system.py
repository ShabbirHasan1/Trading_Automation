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
