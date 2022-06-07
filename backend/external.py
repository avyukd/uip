from utils import parse_date
import os 
import datetime 
import requests
from bs4 import BeautifulSoup
from enums import Commodity
from typing import List
import json 
import re
from utils import get_tickers

def get_stock_prices():
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

    current_time = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    wrapper = {
        "data": data,
    }

    with open(f"cache/{commodity_name}/{current_time}.json", "w+") as f:
        json.dump(wrapper, f)

    return data
