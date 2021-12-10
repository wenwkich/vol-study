# testing for tarvis
# import environmental variables first
import os, json, logging
from tardis_dev import datasets, get_exchange_details

from dotenv import load_dotenv
load_dotenv()
TARDIS_KEY = os.environ.get('TARDIS_KEY')

# comment out to disable debug logs
logging.basicConfig(level=logging.DEBUG)

# function used by default if not provided via options
def default_file_name(exchange, data_type, date, symbol, format):
    return f"{exchange}_{data_type}_{date.strftime('%Y-%m-%d')}_{symbol}.{format}.gz"

def download_tardis(from_date, to_date, symbols, data_types=["quotes", "trades"]): 
    datasets.download(
        exchange="deribit",
        data_types=data_types,
        from_date=from_date,
        to_date=to_date,
        symbols=symbols,
        api_key=TARDIS_KEY,
        download_dir="./datasets",
        get_filename=default_file_name,
    )

def download_details(path='./datasets/details.json'):
    with open(path, 'w') as f_details:
        json.dump(f_details, get_exchange_details('deribit'))

if __name__ == '__main__':
    download_details()
    download_tardis('2021-12-09', '2021-12-09', ['BTC-24JUN22-50000-C'])