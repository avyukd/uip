"""
UIP asset base classes.
"""

from abc import ABC, abstractmethod
from external import get_curve
from enum import Enum
from enums import Commodity, Forex
from collections import defaultdict
import datetime
from exceptions import InvalidParameterException
from utils import bs_call

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

    @abstractmethod
    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        """
        pass

class Option():
    """
    Option class.
    """
    
    def __init__(self, underlying_ticker: str, underlying_price: float, strike: float, expiry: str, intrinsic_value_lookback: str, iv: float):
        """
        Initializes Option object.
        """
        self.underlying_ticker = underlying_ticker
        self.underlying_price = underlying_price
        self.strike = strike
        self.expiry = datetime.datetime.strptime(expiry, "%m-%d-%Y")
        
        if intrinsic_value_lookback[-1] == 'd':
            delta = datetime.timedelta(days=int(intrinsic_value_lookback[:-1]))
        elif intrinsic_value_lookback[-1] == 'm':
            delta = datetime.timedelta(days=30 * int(intrinsic_value_lookback[:-1]))
        elif intrinsic_value_lookback[-1] == 'y':
            delta = datetime.timedelta(days=365 * int(intrinsic_value_lookback[:-1]))
        else:
            raise InvalidParameterException("Invalid intrinsic value lookback.")
        
        self.intrinsic_value_date = self.expiry - delta
        self.iv = iv
        self.dte = (self.expiry - datetime.datetime.now()).days


    def get_intrinsic_value(self):
        """
        Returns option's intrinsic value based on BS model.
        Not conventional use of "intrinsic value" for an option. 
        """
        # 1 percent interest rate
        return bs_call(self.underlying_price, self.strike, (self.intrinsic_value_date - datetime.datetime.now()).days / 365, 0.01, self.iv)

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
        