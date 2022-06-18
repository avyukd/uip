
from typing import Any, List
import os
from math import log, sqrt, pi, exp
from scipy.stats import norm
import numpy as np

def discount(val: float, rate: float, yrs: float) -> float:
    """
    Returns discounted value.
    """
    return val / (1 + rate) ** yrs

def NPV(discount_rate: float, fcfs: List[float]) -> float:
    """
    Returns net present value of a cash flow series.
    """
    return sum([fcfs[i] / (1 + discount_rate) ** i for i in range(len(fcfs))])

def TV(terminal_growth_rate: float, last_yr_fcf: float, discount_rate: float) -> float:
    """
    Returns terminal value of a cash flow series.
    """
    return last_yr_fcf * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)

def exit_TV(exit_multiple: float, last_yr_ebitda: float) -> float:
    """
    Returns terminal value based on exit multiple.
    """
    return last_yr_ebitda * exit_multiple

def get_tickers():
    """
    Returns list of tickers of all companies in /stocks/*.py.
    """
    tickers = []
    for filename in os.listdir("assets/stocks"):
        if filename[-3:] == ".py":
            tickers.append(filename[:-3]) # remove .py
    return tickers

def delete_scenario(name: str):
    """
    Deletes scenario with given name.
    """
    os.remove(f"scenarios/{name}.json")

def get_scenarios():
    """
    Returns list of all scenarios in /scenarios/*.py.
    """
    scenarios = []
    for filename in os.listdir("scenarios/"):
        if filename[-5:] == ".json":
            scenarios.append(filename[:-5]) # remove .json
    return scenarios

# def cached(param: str) -> bool:
#     """
#     Returns True if param is in cache.
#     """
#     pass

# def load_param_from_cache(param: str) -> Any:
#     """
#     Assumes param is in cache. Loads the param. 
#     May have to wrap in object. Ex: CommodityCurve(RawCachedData)
#     """
#     pass



def parse_date(date: str) -> str:
    """
    Returns date in format MM.YY. Given date in form "Aug'19".
    """
    year = date[-2:]
    month = date[:-3]
    month_dict = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12"
    }
    return month_dict[month] + "." + year

# option pricing
def d1(S,K,T,r,sigma):
    return(log(S/K)+(r+sigma**2/2.)*T)/(sigma*sqrt(T))

def d2(S,K,T,r,sigma):
    return d1(S,K,T,r,sigma)-sigma*sqrt(T)

def bs_call(S,K,T,r,sigma):
    return S*norm.cdf(d1(S,K,T,r,sigma))-K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma))