"""
UIP Base Classes
"""
from abc import ABC, abstractmethod

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