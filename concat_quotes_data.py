import os, re, glob
import pandas as pd
from datetime import timedelta
import re
from dateutil import parser, tz
from os import path
from py_vollib_vectorized.implied_volatility import vectorized_implied_volatility as iv

def glob_re(pattern, strings):
    return filter(re.compile(pattern).match, strings)

def concat_option_price(prefix="BTC", datatype='quotes', basepath='../datasets'):
    filenames = glob_re(path.join(basepath, f"deribit_{datatype}_([0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}})_({prefix}-[0-9]{{1,2}}[A-Z]{{3}}[0-9]{{2}}-[0-9]*-(C|P)).csv.gz"), glob.glob(os.path.join(basepath, "*.csv.gz")))

    df = pd.concat(
        (
            pd.read_csv(filename, compression="gzip", index_col=0, header=0)
            for filename in filenames
        ),
        axis=0,
        ignore_index=True,
    )

    return df

if __name__ == "__main__":
    df = concat_option_price(datatype="trades")
    print(df.head())
    df.to_csv('../outs/deribit_trades_history.csv.gz', compression='gzip')
