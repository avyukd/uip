
from typing import Dict, List
from exceptions import InvalidParameterException
from stocks import *
from utils import get_tickers, cached, load_param_from_cache, parse_date
import json
import inspect
from importlib import import_module
import requests
from bs4 import BeautifulSoup
from enums import Commodity
import re 
import os
import datetime

"""
Load all stocks from /stocks and return a JSON object of their intrinsic values and delayed prices
Cache everything?
"""

def load_all_intrinsic_values(user_input: Dict = {}) -> Dict:
    """
    For each stock in /stocks, get its intrinsic value. 
    First, check **kwargs. If parameter is there, use that. 
    Second, check defaults.json. If parameter is under ticker name, use that.
    If parameter is under generics in default.json, use that.  
    Third, check cache. If parameter is there, use that. 
    If not found, raise error. 
    """
    
    defaults = json.load(open("defaults.json"))

    tickers = get_tickers()
    intrinsic_values = {}
    for ticker in tickers:
        module = import_module(f"stocks.{ticker}")
        stock_class = getattr(module, ticker)
        params = [x.name for x in inspect.signature(stock_class.__init__).parameters.values()][1:]

        arguments = {}
        for param in params:
            if ticker in user_input and param in user_input[ticker]:
                arguments[param] = user_input[ticker][param]
            elif param in defaults[ticker]:
                arguments[param] = defaults[ticker][param]
            elif param in defaults["generics"]:
                arguments[param] = defaults["generics"][param]
            elif cached(param):
                arguments[param] = load_param_from_cache(param)
            else:
                raise InvalidParameterException(f"Parameter {param} not found.")
        
        stock = stock_class(**arguments)
        intrinsic_values[ticker] = stock.get_intrinsic_value()
    
    return intrinsic_values

def load_stock_prices():
    """
    Load stock prices from EOD API. Check cache first.
    """
    keys = json.load(open("keys.json"))

    tickers = get_tickers()
    base_URL = "https://eodhistoricaldata.com/api/real-time/"
    prices = []
    for i in range(0, len(tickers), 10):
        tickers_str = ",".join(tickers[i+1:i+10])
        
        URL = base_URL + tickers[i] + "?api_token=" + keys["EOD_API_KEY"] + "&fmt=json&s="
        URL += tickers_str + "&filter=close"
        
        prices += requests.get(URL).text.replace("[","").replace("]","").split(",")

    wrappedQuotes = {}
    for i in range(len(tickers)):
        wrappedQuotes[tickers[i]] = float(prices[i])
    
    return wrappedQuotes

def get_curve(symbol: Commodity) -> List[List[str]]:
    """
    Get curve from cache or from esignal.
    """
    commodity_name = str(symbol).split(".")[1]
    files = os.listdir(f"cache/{commodity_name}")
    files.sort()
    if len(files) > 0:
        mostrecentdate = files[-1].split(".")[0]
        mostrecentdate = datetime.datetime.strptime(mostrecentdate, "%Y%m%d-%H%M%S")
        today = datetime.datetime.today()
        if (today - mostrecentdate).total_seconds() / 3600 < 3:
            with open(f"cache/{commodity_name}/{files[-1]}", "r") as f:
                data = json.load(f)
            return data["data"]
    return esignal_request(symbol)


def esignal_request(symbol: Commodity):
    """
    Scrape esignal quotes and return relevant commodity curve.
    """
    commodity_name = str(symbol).split(".")[1]
    symbol = symbol.value
    URL = "https://quotes.esignal.com/esignalprod/quote.action?symbol=" + symbol
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("div", {"class": "datagrid padding"}).find("table")
    rows = table.find_all("tr")
    data = []
    for row in rows:
        cells = row.find_all("td")
        pair = []
        for cell in cells:
            content = cell.text.strip()
            if re.match("[A-Za-z]{3}'[0-9]{2}", content):
                pair.append(parse_date(content))
            price_table = cell.find("table", {"class": "last_settle"})
            if price_table:
                pair.append(float(price_table.find("td").text.strip()))
                break
        if len(pair) == 2:
            data.append(pair)
    
    data.sort(key=lambda x: (int(x[0][-2:]), int(x[0][:2])))

    if not os.path.exists(f"cache/{commodity_name}"):
        os.makedirs(f"cache/{commodity_name}")

    # only include 
    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    wrapper = {
        "data": data,
    }

    with open(f"cache/{commodity_name}/{current_time}.json", "w+") as f:
        json.dump(wrapper, f)

    return data
