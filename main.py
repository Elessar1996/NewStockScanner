import asyncio

import colorama
import pandas as pd
import datetime
from utils import run_for_a_list_of_symbols


def main():

    t = datetime.datetime.now()
    stocks = pd.read_csv('stocks.csv', delimiter=',')
    print(stocks)
    symbols = [i[0] for i in stocks.values]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_for_a_list_of_symbols(symbols))

    print(colorama.Fore.WHITE + f'the whole thing run in {datetime.datetime.now() - t} secs')

main()









