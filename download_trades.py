from tardis_dev import datasets
import pandas as pd
from datetime import datetime
import json

from download_tardis import download_tardis
from deribit_details import DeribitDetails

from dotenv import load_dotenv
import os
load_dotenv()
TARDIS_KEY = os.environ.get('TARDIS_KEY')

def calculate_iv_for_trades():
    pass

def calculate_iv_for_quotes():
    pass

def main():
    # for each day, i need to download the ATM option trades data at that season
    # if the seasonal contract is from the next month, i will download the seasonal contract at the next month

    # download from tardis
    pass

    # for each csv, calculate the trades iv & quotes iv


if __name__ == "__main__":
    main()