
from typing import Dict, List
from pandas import get_option

from yaml import load_all
from exceptions import InvalidParameterException
from assets.stocks import *
from utils import get_tickers, parse_date
import json
import inspect
from importlib import import_module
from external import get_stock_prices, get_option_data
from model import Model
from base import Option

"""
Load all asset information. Methods are called by API to display on frontend.
"""

def load_all_options(user_input: Dict) -> Dict:
    stock_classes = load_all_stock_classes(user_input)
    options = json.load(open("assets/options/options.json"))
    
    trades_to_display = ["long_call"] # figure out warrants later

    rows = []
    for trade_type in trades_to_display:
        for option in options[trade_type]:
            ticker, expiry, strike, lookback = option["ticker"], option["expiry"], option["strike"], option["lookback"]
            underlying_value = stock_classes[ticker].get_intrinsic_value()                

            option_data = get_option_data(ticker, expiry, strike)

            iv = option["target_iv"]
            bid = option_data["bid"]
            ask = option_data["ask"]
            volume = option_data["volume"]
            open_interest = option_data["openInterest"]
            price = ( bid + ask ) / 2

            print(ticker, underlying_value, strike, expiry, lookback, iv)

            if ticker not in stock_classes:
                raise InvalidParameterException(f"Ticker {ticker} not found in stock classes.")
            else:
                intrinsic_value = Option(ticker, underlying_value, strike, expiry, lookback, iv).get_intrinsic_value()
                if intrinsic_value < 0:
                    intrinsic_value = 0
                if intrinsic_value != 0:
                    discount = max(1 - price / intrinsic_value, 0)
                else:
                    discount = 0
                upside = intrinsic_value / price - 1
                rows.append({
                    "ticker": ticker,
                    "expiry": expiry,
                    "strike": strike,
                    "lookback": lookback,
                    "iv": iv,
                    "bid": bid,
                    "ask": ask,
                    "intrinsic_value": intrinsic_value,
                    "discount": discount,
                    "upside": upside,
                    "volume": volume,
                    "open_interest": open_interest,
                })
    return rows

def load_all_stocks(user_input: Dict) -> Dict:
    # get margin of safety
    defaults = json.load(open("defaults.json"))
    if user_input["generics"] is not None and "margin_of_safety" in user_input["generics"] and user_input["generics"]["margin_of_safety"] is not None:
        margin_of_safety = user_input["generics"]["margin_of_safety"]
    elif "margin_of_safety" in defaults["generics"]:
        margin_of_safety = defaults["generics"]["margin_of_safety"]
    else:
        raise InvalidParameterException("margin_of_safety not found.")

    stock_classes = load_all_stock_classes(user_input)
    stock_prices = get_stock_prices()

    stocks = []
    for ticker in stock_classes:
        name = stock_classes[ticker].company_name
        sector = stock_classes[ticker].sector
        industry = stock_classes[ticker].industry        
        share_price = stock_prices[ticker]
        intrinsic_value = stock_classes[ticker].get_intrinsic_value() * (1 - margin_of_safety)
        if intrinsic_value < 0:
            intrinsic_value = 0
        if intrinsic_value != 0:
            discount = max(1 - share_price / intrinsic_value, 0)
        else:
            discount = 0
        upside = intrinsic_value / share_price - 1
        stocks.append({
            "ticker": ticker,
            "name": name,
            "sector": sector,
            "industry": industry,
            "share_price": share_price,
            "intrinsic_value": intrinsic_value,
            "discount": discount,
            "upside": upside
        })
    
    return stocks

def load_all_stock_classes(user_input: Dict) -> Dict:
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
    stock_classes = {}
    for ticker in tickers:
        module = import_module(f"assets.stocks.{ticker}")
        stock_class = getattr(module, ticker)
        params = [x.name for x in inspect.signature(stock_class.__init__).parameters.values()][1:]

        arguments = {}
        for param in params:
            if user_input["generics"] is not None and param in user_input["generics"] and user_input["generics"][param] is not None:
                arguments[param] = user_input["generics"][param]
            elif user_input[ticker] is not None and param in user_input[ticker] and user_input[ticker][param] is not None:
                arguments[param] = user_input[ticker][param]
            elif param in defaults[ticker]:
                arguments[param] = defaults[ticker][param]
            elif param in defaults["generics"]:
                arguments[param] = defaults["generics"][param]
            # elif cached(param):
            #     arguments[param] = load_param_from_cache(param)
            else:
                raise InvalidParameterException(f"Parameter {param} not found.")
        
        stock = stock_class(**arguments)
        stock_classes[ticker] = stock
    
    return stock_classes


if __name__ == "__main__":
    # test intrinsic values
    # print([[k, v.get_intrinsic_value()] for k, v in load_all_stock_classes().items()])

    # test stocks object
    # print(json.dumps({"stocks" : load_all_stocks(Model().dict())}))
    
    # test options object
    print(json.dumps({"options" : load_all_options(Model().dict())}))