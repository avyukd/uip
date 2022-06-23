from enums import Commodity
from utils import parse_date
import os 
import datetime 
import requests
from bs4 import BeautifulSoup
from enum import Enum
from typing import List
import json 
import re
from utils import get_tickers, get_option_name
from exceptions import NoOptionsFoundForTicker
import yfinance as yf

def get_option_data(ticker: str, expiry: str, strike: float):
    expiry = expiry.split("-")
    expiry_dashed = expiry[2]+"-"+expiry[0]+"-"+expiry[1]

    option_name = get_option_name(ticker, expiry, strike)
    
    if not os.path.exists(f"cache/options/{option_name}"):
        os.makedirs(f"cache/options/{option_name}")
    
    files = os.listdir(f"cache/options/{option_name}")
    files.sort()
    if len(files) > 0:
        mostrecentdate = files[-1].split(".")[0]
        mostrecentdate = datetime.datetime.strptime(mostrecentdate, "%Y%m%d-%H%M%S")
        today = datetime.datetime.today()
        if (today - mostrecentdate).total_seconds() / 60 < 15: # prices are within 15 min 
            with open(f"cache/options/{option_name}/{files[-1]}", "r") as f:
                data = json.load(f)
            return data["data"]
    
    keys = json.load(open("keys.json"))
    URL = "https://eodhistoricaldata.com/api/options/" + ticker + "?api_token=" + keys["EOD_API_KEY"]
    chain = requests.get(URL).json()["data"]

    if chain == []:
        raise NoOptionsFoundForTicker(ticker)

    for optionset in chain:
        if optionset["expirationDate"] == expiry_dashed:
            for option in optionset["options"]["CALL"]:
                if option["contractName"] == option_name:
                    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
                    with open(f"cache/options/{option_name}/{current_time}.json", "w+") as f:
                        json.dump({"data": option}, f)
                    return option

def get_unknown_asset_price(asset_name: str): 
    keys = json.load(open("keys.json"))
    base_URL = "https://eodhistoricaldata.com/api/real-time/"
    URL = base_URL + asset_name + "?api_token=" + keys["EOD_API_KEY"] + "&fmt=json&filter=close"
    str_price = requests.get(URL).text.replace("[","").replace("]","")
    try:
        price = float(str_price)
    except ValueError:
        price = 0
    return price

def get_stock_prices():
    """
    Load stock prices from EOD API. Check cache first.
    Maximum total delay of stock price is 30 minutes (15 min in cache + 15 min in delayed API).
    """
    tickers = get_tickers()
    
    files = os.listdir(f"cache/quotes")
    files.sort()
    if len(files) > 0:
        filename = files[-1].split(".")[0]
        mostrecentdate = filename.split("_")[0]
        num_cached_tickers = int(filename.split("_")[1])
        if len(tickers) == num_cached_tickers:
            mostrecentdate = datetime.datetime.strptime(mostrecentdate, "%Y%m%d-%H%M%S")
            today = datetime.datetime.today()
            if (today - mostrecentdate).total_seconds() / 60 < 15: # prices are within 15 min 
                with open(f"cache/quotes/{files[-1]}", "r") as f:
                    data = json.load(f)
                return data["data"]

    keys = json.load(open("keys.json"))

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

    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    wrapper = {
        "data": wrappedQuotes,
    }

    with open(f"cache/quotes/{current_time}_{len(tickers)}.json", "w+") as f:
        json.dump(wrapper, f)
    
    return wrappedQuotes

def get_curve(symbol: Enum) -> List[List]:
    """
    Get curve from cache or from esignal.
    """
    commodity_name = str(symbol).split(".")[1]

    if not os.path.exists(f"cache/{commodity_name}"):
        os.makedirs(f"cache/{commodity_name}")
    
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


def esignal_request(symbol: Enum):
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
                raw = price_table.find("td").text.strip()
                try:
                    pair.append(float(raw))
                    break
                except ValueError:
                    continue
        if len(pair) == 2:
            data.append(pair)
    
    data.sort(key=lambda x: (int(x[0][-2:]), int(x[0][:2])))

    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    wrapper = {
        "data": data,
    }

    with open(f"cache/{commodity_name}/{current_time}.json", "w+") as f:
        json.dump(wrapper, f)

    return data
