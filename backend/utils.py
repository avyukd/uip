
from typing import Any, Dict, List
import os
from math import log, sqrt, pi, exp
from scipy.stats import norm
import numpy as np
import pandas as pd

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

def read_fidelity_csv(filename: str):
    df = pd.read_csv(filename)

    pending_activity = df.loc[df["Symbol"] == "Pending Activity", "Last Price Change"].values[0] 

    pending_activity = pending_activity.replace("$", "")
    pending_activity = pending_activity.replace(",", "")
    if pending_activity[0] == "(" and pending_activity[-1] == ")":
        pending_activity = pending_activity[1:-1]
        pending_activity = -float(pending_activity)
    else:
        pending_activity = float(pending_activity)

    print(pending_activity)

    df = df[["Symbol", "Quantity", "Cost Basis"]]
    
    df["Quantity"] = df.groupby(["Symbol"])["Quantity"].transform("sum")
    df["Cost Basis"] = df["Cost Basis"].replace('[\$,]', '', regex=True).astype(float)
    df["Cost Basis"] = df.groupby(["Symbol"])["Cost Basis"].transform("sum")

    df = df.drop_duplicates(subset=["Symbol"])
    df = df.replace("SPAXX**", "Cash")
    df.loc[df["Symbol"] == "Cash", "Quantity"] += pending_activity
    # df.loc[df["Symbol"] == "Cash", "Cost Basis"] = df["Quantity"]
    df = df[df["Quantity"] > 0]
    df["Cost Basis Per Share"] = df["Cost Basis"] / df["Quantity"]

    return df

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

# pass in self object + list of details to populate
# need to make fcfs and stuff like that in self, need standard vocabulary
def detail_factory(class_obj):
    vars = class_obj.__dict__

    for key in class_obj.detail:
        if key in vars:
            class_obj.detail[key] = vars[key]

    if "shs" in vars:
        class_obj.detail["shs"] = class_obj.shs
        if "fcfs" in vars:
            class_obj.detail["fcf_ps"] = class_obj.fcfs[0] / class_obj.shs
        elif "fcf" in vars:
            class_obj.detail["fcf_ps"] = class_obj.fcf / class_obj.shs
        
        if "divs" in vars:
            class_obj.detail["div_ps"] = class_obj.divs[0] / class_obj.shs
        elif "div" in vars:
            class_obj.detail["div_ps"] = class_obj.div[0] / class_obj.shs

    if "cash" in vars and "debt" in vars:
        class_obj.detail["net_cash"] = class_obj.cash - class_obj.debt
    elif "cash" in vars and "current_debt" in vars:
        class_obj.detail["net_cash"] = class_obj.cash - class_obj.current_debt

    
    if "ebitdas" in vars:
        class_obj.detail["ebitda"] = class_obj.ebitdas[0]
    elif "ebitda" in vars:
        class_obj.detail["ebitda"] = class_obj.ebitda

def build_indicators(detail: Dict, share_price: float):
    """
    Returns dictionary of indicators for given ticker.
    """
    indicators = {}
    if detail["fcf_ps"] is not None:
        indicators["fcf_yield"] = detail["fcf_ps"] / share_price
    if detail["div_ps"] is not None:
        indicators["div_yield"] = detail["div_ps"] / share_price
    if detail["ebitda"] is not None and detail["shs"] is not None and detail["net_cash"] is not None:
        ev = share_price * detail["shs"] - detail["net_cash"]
        indicators["ev_ebitda"] = ev / detail["ebitda"]
    if detail["net_cash"] is not None:
        if detail["net_cash"] > 0:
            indicators["net_cash"] = True
        if detail["shs"] is not None:
            if detail["net_cash"] > share_price * detail["shs"]:
                indicators["negative_EV"] = True
    return indicators

def get_option_name(ticker, expiry, strike) -> str:
    expiry = expiry.split("-")
    expiry_nodash = expiry[2][-2:] + expiry[0] + expiry[1]    
    strikestr = "{:.3f}".format(strike)
    while len(strikestr) <= 8:
        strikestr = "0" + strikestr
    strikestr = strikestr.replace(".", "")
    option_name = f"{ticker}{expiry_nodash}C{strikestr}"
    return option_name