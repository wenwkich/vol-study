from tardis_dev import datasets
import pandas as pd
from datetime import datetime
import json

from download_tardis import download_tardis
from deribit_details import DeribitDetails

def main():
    # for each day, i need to download the ATM option trades data at that season
    # if the seasonal contract is from the next month, i will download the seasonal contract at the next month
    deribit = DeribitDetails()
    pd.read_csv('./outs/bitcoin_historical_vol.csv')

    # download from tardis
    pass

if __name__ == "__main__":
    main()