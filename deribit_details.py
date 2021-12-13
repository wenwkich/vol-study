import json
import re
from dateutil import parser, tz
from datetime import datetime
import calendar

def get_next_season_end_month(month, year):
    end_month = (month + 3) // 3 * 3 % 12
    return (end_month if end_month != 0 else 12, year + 1 if month == 12 else year)

def get_last_friday(month, year):
    last_day = calendar.monthrange(year, month)[1]
    last_weekday = calendar.weekday(year, month, last_day)
    return last_day - ((7 - (4 - last_weekday)) % 7)

def round_to_nearest(x, level=5000):
    return (x+level//2)//level*level

def recursive_find_instrument(symbols, format, strike_price, dt, delta=1000, depth=0):
    instrument = format.format(strike = strike_price)
    # print(f"calling strike_price={strike_price}, depth={depth}, instrument={instrument}")
    # base case
    if instrument in symbols and dt > parser.parse(symbols[instrument]['availableSince']):
        return format.format(strike = strike_price)
    if depth >= 5: return None

    plus_delta_result = recursive_find_instrument(symbols, format, strike_price+delta, dt, delta, depth+1)
    if plus_delta_result != None: return plus_delta_result
    minus_delta_result = recursive_find_instrument(symbols, format, strike_price-delta, dt, delta, depth+1)
    if minus_delta_result != None: return minus_delta_result

def get_seasonal_expiry_dates_and_strike_price(instrument_name, prefix):
    result = re.search('^{prefix}-([0-9]{{1,2}}[A-Z]{{3}}([0-9]{{2}}))-([0-9]*)-(P|C)$'.format(prefix = prefix), instrument_name) 

    if result is not None: 
        expiry_date = result.group(1)

        # determine if this is the last friday of the month
        dt = parser.parse(expiry_date)
        if dt.day != get_last_friday(dt.month, dt.year):
            return

        strike_price = result.group(5)
        return (expiry_date, strike_price)

class DeribitDetails:

    def __init__(self, prefix='BTC', detail_json_path='../datasets/details.json'):
        with open(detail_json_path, 'r') as f_deribit_details:
            self.prefix = prefix
            json_deribit_details = json.load(f_deribit_details)
        
            symbols = { symbol['id']: {'availableSince': symbol['availableSince'] , 'availableTo': symbol['availableTo']} for symbol in json_deribit_details['datasets']['symbols'] }
            self.symbols = symbols

            # expiry_dates_strike_price = { get_seasonal_expiry_dates_and_strike_price(symbol, prefix) for symbol in symbols }
            # print(expiry_dates_strike_price)
            # self.expiry_dates_strike_price = expiry_dates_strike_price

    def determine_instruments(self, ts, price, delta=1000):
        # determine the date first
        dt = parser.parse(ts)
        dt = dt.replace(tzinfo=tz.UTC)
        end_month, end_year = get_next_season_end_month(dt.month, dt.year)
        end_day = get_last_friday(end_month, end_year)
        instrument_date = datetime(end_year, end_month, end_day).strftime('%d%b%y').upper()
        # print(instrument_date)

        # then the strike price
        initial_strike_price = round_to_nearest(price, delta)
        instrument_call = recursive_find_instrument(self.symbols, f'{self.prefix}-{instrument_date}-{{strike}}-C', initial_strike_price, dt, delta)
        instrument_put = recursive_find_instrument(self.symbols, f'{self.prefix}-{instrument_date}-{{strike}}-P', initial_strike_price, dt, delta)
        if instrument_call != None and instrument_put != None:
            return [instrument_call, instrument_put]

if __name__ == '__main__':
    deribit_details = DeribitDetails()
    print(deribit_details.determine_instruments('2020-12-08', 35015, delta=1000))

    # for i in range(1, 13):
    #     print(f"for month {i}: {get_next_season_end_month(i, 2021)}")