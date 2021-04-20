import pandas as pd
import datetime
import json
import time
from helpers import GetCurrentWeeklyOptions, fetch_ltp, GetATMStrike, FetchPositionsInfo, fetch_token


def GetBNFStoplossTargetValues(contract_ce, contract_pe, lots):
    token_ce = fetch_token(contract_ce)
    token_pe = fetch_token(contract_pe)
    combined_premium = fetch_ltp(token_ce) + fetch_ltp(token_pe)
    quantity = lots * 25
    stoploss = -0.15 * quantity * combined_premium
    target = 0.15 * quantity * combined_premium
    step = 0.15 * quantity * combined_premium
    return stoploss, target, step


def GetBNFStraddleTrades():
    entry_trades = []
    exit_trades = []
    lots = 1
    trade_start_time = datetime.time(9, 45)
    trade_end_time = datetime.time(14, 45)
    fixed_stoploss = -2000

    atm_strike = GetATMStrike('NIFTY BANK')
    contract_ce, contract_pe = GetCurrentWeeklyOptions(atm_strike, 'BANKNIFTY')
    stoploss, target, step = GetBNFStoplossTargetValues(contract_ce, contract_pe, lots)
    entry_trades = {'symbols': [contract_ce, contract_pe],
                    'trade_time': trade_start_time,
                    'fixed_stoploss': fixed_stoploss,
                    'stoploss': stoploss,
                    'target': target,
                    'step': step,
                    'quantity': lots * 25,
                    'transaction_type': 'SELL',
                    'exit_time': trade_end_time,
                    'product_type': 'MIS',
                    'info': 'BANKNIFTY STRADDLE ATM OPTION SELL'
                    }
    # exit_trades = {'symbols': [contract_ce, contract_pe],
    #                'trade_time': trade_start_time,
    #                'fixed_stoploss': fixed_stoploss,
    #                'stoploss': stoploss,
    #                'target': target,
    #                'step': step,
    #                'quantity': lots * 25,
    #                'transaction_type': 'BUY',
    #                'exit_time': trade_end_time,
    #                'product_type': 'MIS',
    #                'info': 'BANKNIFTY STRADDLE ATM OPTION BUY'}

    return entry_trades
