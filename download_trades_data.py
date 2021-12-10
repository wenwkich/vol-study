import pandas as pd
from dateutil import parser

from download_tardis import download_tardis
from deribit_details import DeribitDetails

def format_unix(unix):
    return parser.parse(unix).strftime('%Y-%m-%d')

def download_trades_data(start_date):
    # for each day, i need to download the ATM option trades data at that season
    # if the seasonal contract is from the next month, i will download the seasonal contract at the next month
    deribit = DeribitDetails()
    df = pd.read_csv('./outs/bitcoin_historical_vol.csv')

    for _, row in df.iterrows():
        dt = row['datetime']
        if dt < start_date: 
            continue
        instruments = deribit.determine_instruments(dt, int(row['close']))
        download_tardis(dt, instruments)

if __name__ == "__main__":
    download_trades_data('2021-06-08')