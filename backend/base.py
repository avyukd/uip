"""
UIP asset base classes.
"""

from abc import ABC, abstractmethod
from external import get_curve, get_stock_prices
from enum import Enum
from enums import Commodity, Forex, Direction
from collections import defaultdict
import datetime
from exceptions import InvalidParameterException
from utils import bs_call, get_option_name
from pydantic import BaseModel
from typing import Optional, Dict, List

class Asset(ABC):
    """
    Asset base class. All assets have an intrinisic value.
    """
    @abstractmethod
    def get_intrinsic_value(self):
        """
        Return intrinsic value of the asset
        """
        pass
    
    @abstractmethod
    def get_asset_name(self):
        """
        Return name of the asset
        """
        pass
    
    def __repr__(self) -> str:
        return self.get_asset_name()

class DummyAsset(Asset):
    """
    Dummy asset. 
    """
    def __init__(self, asset_name: str):
        self.asset_name = asset_name
    
    def get_asset_name(self):
        return self.asset_name
    
    def get_intrinsic_value(self):
        return 0.0

class Cash(Asset):
    """
    Cash.
    """
    def get_intrinsic_value(self):
        return 1.0
    
    def get_asset_name(self):
        return "Cash"

class Stock(Asset):
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
        self.detail = Detail().dict()

    # @abstractmethod
    # def get_intrinsic_value(self):
    #     """
    #     Returns company's intrinsic value based on DCF valuation.
    #     """
    #     pass

    def get_asset_name(self):
        return self.ticker

class Detail(BaseModel):
    fcf_ps: Optional[float] = None
    div_ps: Optional[float] = None
    net_cash: Optional[float] = None
    ebitda: Optional[float] = None
    shs: Optional[float] = None

class Option(Asset):
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
    
    def get_asset_name(self):
        return get_option_name(self.underlying_ticker, self.strike, self.expiry)

class Fund(Asset):
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

class Position():
    # everything here is on a per share basis
    def __init__(self, direction: Direction, asset: Asset, cost_basis: float, price: float, num_shares: float):
        self.direction = direction
        self.asset = asset
        self.price = price
        self.intrinsic_value = max(asset.get_intrinsic_value(), 0)
        self.cost_basis = cost_basis
        self.num_shares = num_shares
        self.change = (self.price - self.cost_basis) / self.cost_basis
        self.unrealized = self.change * num_shares
        # upside vs cost basis
        # discount vs cost basis

class Portfolio():
    def __init__(self, positions: List[Position]):
        self.positions = positions
        self.cash = 0.0
        for position in positions:
            if str(position.asset) == "Cash":
                self.cash = position.num_shares * position.price
    
    def get_current_value(self):
        return sum([p.price * p.num_shares for p in self.positions])
    
    def get_intrinsic_value(self): 
        return sum([p.intrinsic_value * p.num_shares for p in self.positions])
    
    def get_cost_basis_value(self):
        return sum([p.cost_basis * p.num_shares for p in self.positions])

    def pct_cost_basis(self):
        total_value = self.get_cost_basis_value()
        return {str(p.asset): (p.cost_basis * p.num_shares) / total_value for p in self.positions}
    
    def pct_current(self):
        total_value = self.get_current_value()
        return {str(p.asset): (p.price * p.num_shares) / total_value for p in self.positions}

    def get_pct_cash(self):
        return self.cash / self.get_current_value()
        
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
        