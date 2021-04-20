import time
import datetime
import json
import time

from helpers import GetCurrentWeeklyOptions, fetch_ltp, GetATMStrike, FetchPositionsInfo
from putorders import PlaceMarketOrders


def RunSystem(kite, access_token, trades):
    fixed_stoploss = trades['fixed_stoploss']
    stoploss = trades['stoploss']
    target = trades['target']
    step = trades['step']
    transaction_types = ['BUY', 'SELL']
    transaction_types.remove(trades['transaction_type'])
    exit_transaction_type = transaction_types[0]
    positions_info = FetchPositionsInfo(kite)

    # this takes care of restartng from middle runs
    if not positions_info:
        position_flag = False
    else:
        #TODO Change this to true
        position_flag = True

    # TODO remove this counter
    # count = 0
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= trades['trade_time'] and position_flag == False:
            all_orders_status = []
            for contract in trades['symbols']:
                order_status = PlaceMarketOrders(access_token, contract, trades['transaction_type'], trades['product_type'], trades['quantity'])
                print(order_status)
                yield order_status + "\n"
                order_status = json.loads(order_status)
                all_orders_status.append(order_status)
            if all(d['status'] == 'success' for d in all_orders_status):
                yield "################### ALL THE ORDERS ARE SUCCESSFUL ###################" + "\n"
                positions_info = FetchPositionsInfo(kite)
                position_flag = True
            elif any(d['status'] == 'error' for d in all_orders_status):
                yield "################### ONE OF THE ORDERS FAILED ###################" + "\n"
                # TODO Remove this line
                # position_flag = True
            else:
                # TODO Remove this line
                # position_flag = True
                continue

        pnl = 0
        # TODO remove this line
        # count += 1

        yield f"CURRENT TIME: {current_time}" + "\n"
        for instrument, instrument_info in positions_info.items():
            ltp = fetch_ltp(instrument_info['token'])
            yield f"{instrument} ltp: {ltp}" + "\n"
            pnl = pnl + instrument_info['value_change'] + (
                    instrument_info['quantity'] * ltp * instrument_info['multiplier'])

        yield f"pnl = {pnl}" + "\n"
        yield f"fixed stoploss = {fixed_stoploss}" + "\n"
        yield f"stoploss = {stoploss}" + "\n"
        yield f"target = {target}" + "\n"
        yield "======================================" + "\n"

        if pnl < fixed_stoploss or pnl < stoploss:
            all_orders_status = []
            for instrument, instrument_info in positions_info.items():
                order_status = PlaceMarketOrders(access_token, instrument, exit_transaction_type, trades['product_type'], trades['quantity'])
                all_orders_status.append(order_status)
            yield str(all_orders_status)
            return all_orders_status
        elif pnl >= target:
            stoploss = stoploss + step
            target = target + step
        elif current_time >= trades['exit_time']:
            all_orders_status = []
            for contract in trades['symbols']:
                order_status = PlaceMarketOrders(access_token, contract, exit_transaction_type, trades['product_type'], trades['quantity'])
                all_orders_status.append(order_status)
            yield str(all_orders_status)
            return all_orders_status

        time.sleep(1)
