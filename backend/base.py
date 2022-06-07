"""
UIP asset base classes.
"""

from abc import ABC, abstractmethod
from external import get_curve
from enums import Commodity
from collections import defaultdict

class Stock(ABC):
    """
    Stock base class. Inherited by each company in /stocks/*.py.
    """
    def __init__(self, ticker: str, sector: str, industry: str, exchange: str):
        """
        Initializes Stock object.
        """
        self.ticker = ticker
        self.sector = sector
        self.industry = industry
        self.exchange = exchange

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

class Option(ABC):
    """
    Option base class.
    """
    pass

class CommodityCurve():
    """
    CommodityCurve class.
    """
    def __init__(self, commodity: Commodity):
        """
        Initializes CommodityCurve object.
        """
        self.commodity_name = str(commodity).split(".")[1]
        self.commodity_symbol = commodity.value
        self.curve = get_curve(commodity)
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

    def get_most_recent_futures_price(self):
        """
        Returns price of most recent futures contract. 
        This is not necessarily the current spot price. 
        """
        return self.curve[0][1]