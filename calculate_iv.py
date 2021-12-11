from datetime import timedelta
import pandas as pd
import re
from dateutil import parser, tz
from os import path
from py_vollib_vectorized.implied_volatility import vectorized_implied_volatility as iv

from deribit_details import DeribitDetails

def format_unix(unix):
    return parser.parse(unix).strftime('%Y-%m-%d')

def get_deribit_data_path(instrument_name, ts, datatype='quotes', basepath='./datasets'):
    fn = f'deribit_{datatype}_{ts}_{instrument_name}.csv.gz'
    return path.join(basepath, fn)

def get_iv_result_path(instrument_name, ts, basepath='./outs'):
    fn = f'deribit_iv_{ts}_{instrument_name}.csv'
    return path.join(basepath, fn)

def calculate_iv_per_file(prefix='BTC'):
    # for each day, i need to download the ATM option trades data at that season
    # if the seasonal contract is from the next month, i will download the seasonal contract at the next month
    deribit = DeribitDetails()
    df = pd.read_csv('./outs/bitcoin_historical_vol.csv')
    df_1m = pd.read_csv('./datasets/Binance_BTCUSDT_minute.csv', header=1,)
    df_1m['datetime'] = pd.to_datetime(df_1m['unix'], unit='ms')
    df_1m = df_1m.set_index('datetime')
    df_1m.sort_values(by="datetime", inplace=True, ascending=True)

    df_ret = pd.DataFrame()
    for _, row in df.iterrows():
        ts = row['datetime']
        instruments = deribit.determine_instruments(ts, int(row['close']))

        for instr in instruments:
            path_deribit = get_deribit_data_path(instr, ts)

            if not path.exists(path_deribit): 
                continue

            df_vol = pd.read_csv(path_deribit)
            df_vol['datetime'] = pd.to_datetime(df_vol['timestamp'], unit='us')
            df_vol = df_vol.set_index('datetime')
            df_vol.sort_values(by="datetime", inplace=True, ascending=True)
            re_res = re.search('^{prefix}-([0-9]{{1,2}}[A-Z]{{3}}[0-9]{{2}})-([0-9]*)-(P|C)$'.format(prefix = prefix), instr) 

            date_to_expiry = re_res.group(1)
            dt_to_expiry = parser.parse(date_to_expiry)

            dt_moment = parser.parse(ts)

            dt_delta = dt_to_expiry - dt_moment
            delta_1_year = dt_delta / timedelta(days=365)

            df_vol = pd.merge_asof(df_vol, df_1m['close'], on='datetime', tolerance=pd.Timedelta(seconds=1000))
            df_vol['strike_price'] = float(re_res.group(2))
            df_vol['call_or_put'] = re_res.group(3).lower()
            df_vol['time_to_expiry'] = delta_1_year
    
            df_ret = df_ret.append(df_vol)

    df_ret['ask_iv'] = iv(df_ret['ask_price']*df_ret['close'], df_ret['close'], df_ret['strike_price'], df_ret['time_to_expiry'], 0.02, df_ret['call_or_put'])
    df_ret['bid_iv'] = iv(df_ret['bid_price']*df_ret['close'], df_ret['close'], df_ret['strike_price'], df_ret['time_to_expiry'], 0.02, df_ret['call_or_put'])

    return df_ret

if __name__ == "__main__":
    print(calculate_iv().tail())