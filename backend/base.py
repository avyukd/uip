"""
UIP asset base classes.
"""

from abc import ABC, abstractmethod
from external import get_curve
from enum import Enum
from enums import Commodity, Forex
from collections import defaultdict
import datetime
from math import log, sqrt, pi, exp
from scipy.stats import norm
import numpy as np

# class IdeaSource():
#     """
#     Base class for idea sources.
#     """
#     def __init__(self, name, link):
#         self.name = name
#         self.link = link

class Stock(ABC):
    """
    Stock base class. Inherited by each company in /stocks/*.py.
    """
    def __init__(self, ticker: str, company_name: str, sector: str, industry: str, exchange: str):
        """
        Initializes Stock object.
        """
        self.ticker = ticker
        self.sector = sector
        self.industry = industry
        self.exchange = exchange
        self.company_name = company_name
        # self.idea_source = idea_source

    @abstractmethod
    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        """
        pass

class Fund(ABC):
    """
    Fund base class. 
    """
    pass

class PhysicalFund(Fund):
    """
    Physical fund.
    """
    pass

class ETF(Fund):
    """
    ETF.
    """
    pass

# class Option(ABC):
#     """
#     Option base class.
#     """
#     def __init__(self, ticker: str, strike: float, expiry: str):
#         """
#         Initializes Option object.
#         """
#         self.ticker = ticker
#         self.strike = strike
#         self.expiry = datetime.strptime(expiry, "%m-%d-%Y")
    

# #helper functions
# def d1(S,K,T,r,sigma):
#     return(log(S/K)+(r+sigma**2/2.)*T)/(sigma*sqrt(T))

# def d2(S,K,T,r,sigma):
#     return d1(S,K,T,r,sigma)-sigma*sqrt(T)

# def bs_call(S,K,T,r,sigma):
#     return S*norm.cdf(d1(S,K,T,r,sigma))-K*exp(-r*T)*norm.cdf(d2(S,K,T,r,sigma))

# #get fair price of option
# def get_option_price(underlying, strike, interest_rate, time_to_expiration, volatility):
#     return bs_call(underlying, strike, time_to_expiration, interest_rate, volatility)


class FuturesCurve():
    """
    Futures curve.
    """
    def __init__(self, symbol: Enum):
        self.name = str(symbol).split(".")[1]
        self.symbol = symbol.value
        self.curve = get_curve(symbol)
        self.annual_prices = self.get_annual_prices()

    def get_annual_prices(self):
        """
        Returns annual prices of commodity.
        """
        average_prices_by_year = defaultdict(lambda: [0, 0.0])
        for pair in self.curve:
            year = int("20"+pair[0].split(".")[1])
            price = pair[1]
            average_prices_by_year[year][0] += price
            average_prices_by_year[year][1] += 1
        
        annual_prices = []
        for year in average_prices_by_year:
            annual_prices.append([year, average_prices_by_year[year][0]/average_prices_by_year[year][1]])
        
        return annual_prices

    @abstractmethod
    def get_most_recent_futures_price(self):
        """
        Returns price of most recent futures contract. 
        This is not necessarily the current spot price. 
        """
        return self.curve[0][1]

class CommodityCurve(FuturesCurve):
    """
    CommodityCurve class.
    """
    def __init__(self, commodity: Commodity):
        """
        Initializes CommodityCurve object.
        """
        super().__init__(commodity)

class ForexCurve(FuturesCurve):
    """
    ForexCurve class.
    """
    def __init__(self, forex: Forex):
        """
        Initializes ForexCurve object.
        """
        super().__init__(forex)

class SpotPrice(ABC):
    """
    SpotPrice class.
    """
    def __init__(self, symbol: Enum, price: float):
        """
        Initializes SpotPrice object.
        """
        self.symbol = symbol.value
        self.price = self.get_price()
    
    @abstractmethod
    def get_price():
        pass

# class CommodityPrice(SpotPrice):
#     """
#     CommodityPrice class.
#     """
#     def __init__(self, commodity: Commodity, price: float):
#         """
#         Initializes CommodityPrice object.
#         """
#         super().__init__(commodity, price)
    
#     def get_price(self):
#         """
#         Returns price of commodity.
#         """
#         return get_commodity_price(self.commodity)
        