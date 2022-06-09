
from typing import Dict, List
from exceptions import InvalidParameterException
from assets.stocks import *
from utils import get_tickers, cached, load_param_from_cache, parse_date
import json
import inspect
from importlib import import_module

"""
Load all asset information. Methods are called by API to display on frontend.
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
        module = import_module(f"assets.stocks.{ticker}")
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


if __name__ == "__main__":
    print(load_all_intrinsic_values())