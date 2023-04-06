import asyncio
import time

import colorama
from bs4 import BeautifulSoup
import aiohttp

import re

def remove_comma(text) -> float:


    numeric = re.findall(r"^[-+]|[\d.]*\d+", str(text))

    if len(numeric) == 0 or (len(numeric) == 1 and numeric[0] == '-'):
        return -1
    alphabet = re.findall("[a-zA-Z]*", str(text))
    alpha = [i for i in alphabet if i != '']

    n = ''

    for s in numeric:
        n += s

    if len(alpha) != 0:

        if alpha[0] == 'M':
            return float(n) * (10 ** 6)
        elif alpha[0] == 'B':
            return float(n) * (10 ** 9)
        elif alpha[0] == 'T':
            return float(n) * (10 ** 12)
    else:
        return float(n)


def item_finder(web_content,item,field,data_type):

    fin_streamer = web_content.select_one(f'{item}[{field}={data_type}]')


    return fin_streamer

def web_content_div(web_content, class_path):

    web_content_div = web_content.find_all('div', {'class': class_path})

    try:
        spans = web_content_div[0].find_all('span')
        texts = [span.get_text() for span in spans]
    except IndexError:
        texts = []


    return texts




def get_data(r: str):

    try:

        # print(f'{symbol}\n{r}')
        web_content = BeautifulSoup(r, 'html.parser')

        #class_path for price and change: My(6px) Pos(r) smartphone_Mt(6px)
        ############change
        texts = web_content_div(web_content, 'D(ib) Mend(20px)')
        ############price
        price_item = item_finder(web_content, "fin-streamer","data-test","qsp-price")
        ############volume
        volume_item = item_finder(web_content, "fin-streamer","data-field", "regularMarketVolume")
        # print(f'volume item: {volume_item}')
        ############average volume
        avgVolume_item = item_finder(web_content, "td", "data-test", "AVERAGE_VOLUME_3MONTH-value")
        ############prev_close
        prev_close_item = item_finder(web_content, "td", "data-test", "PREV_CLOSE-value")
        ############market-cap
        market_cap_item = item_finder(web_content, "td", "data-test", "MARKET_CAP-value")
        ############day range
        day_range_item = item_finder(web_content, "td", "data-test", "DAYS_RANGE-value")
        ############open value
        open_value_item = item_finder(web_content, "td", "data-test", "OPEN-value")




        if price_item is not None:
            price= price_item.get_text()
        else:
            price = -1
        if len(texts) != 0:
            change = texts[0]
        else:
            change = -1
        if volume_item is not None:
            volume = volume_item.get_text()
        else:
            volume = -1
        if avgVolume_item is not None:
            avg_volume = avgVolume_item.get_text()
        else:
            avg_volume = []
        if prev_close_item is not None:
            prev_close= prev_close_item.get_text()
        else:
            prev_close = []
        if market_cap_item is not None:
            market_cap= market_cap_item.get_text()
        else:
            market_cap = -1
        if day_range_item is not None:
            day_range= day_range_item.get_text()
        else:
            day_range = -1
        if day_range_item is not None:
            open_value= open_value_item.get_text()
        else:
            open_value = []
        if prev_close_item is not None and open_value_item is not None:
            gap_item = item_finder(web_content, 'div', 'id', 'mrt-node-Lead-5-QuoteHeader')
            gap_change_item = gap_item.findChildren('fin-streamer', {'data-field':'regularMarketChangePercent'})
            # print(f'gap_change_item: {gap_change_item}')
            # print(f'len of gap_change_item: {len(gap_change_item)}')
            # gap = round((remove_comma(open_value)/remove_comma(prev_close)) - 1, 2)
            if gap_change_item is not None:
                new_s = ''
                for sth in gap_change_item:
                    for char in sth.text:
                        if char!='(' and char!=')':
                            new_s += char
                gap = new_s
            else:
                gap = -1
        else:
            gap = -1
        if volume_item is not None and avgVolume_item is not None:
            rv = round(remove_comma(volume)/remove_comma(avg_volume), 2)
        else:
            rv = -1

    except ConnectionError:

        price, change, volume, avg_volume, prev_close, market_cap, day_range, open_value, gap, rv = -1, -1, -1, -1, -1, -1, -1, -1, -1, -1




    return gap, price, change, volume, rv, market_cap, day_range #rv-min


def get_url(ticker: str) -> str:
    return f'https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch'


async def get_html(ticker: str) -> str:
    url = get_url(ticker)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            resp.raise_for_status()

            return await resp.text()


async def run_for_a_list_of_symbols(symbols: list):

    tasks = []
    for s in symbols:

        tasks.append(asyncio.create_task(get_html(s)))

    for idx, t in enumerate(tasks):

        try:

            html = await t
            info = get_data(html)

            print(colorama.Fore.MAGENTA + f'info for ticker={symbols[idx]}:')
            print(colorama.Fore.YELLOW+f'{info}')
            print('-----------------------------------------------------------------')

            if idx % 10 == 0 and idx != 0:
                time.sleep(2)

        except aiohttp.client_exceptions.ClientPayloadError:
            print(colorama.Fore.RED+ f'tried but could not')


