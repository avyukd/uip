import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV, discount

class UAN(Stock):
    """
    UAN stock.
    """
    def __init__(self, exit_multiple: float):
        """
        Initializes UAN object.
        """
        self.exit_multiple = exit_multiple
        super().__init__("UAN", "CVR Partners", "Agriculture", "Producer", "NYSE")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/14/2022
        This isn't a complete model, numbers are sourced from Excel Spreadsheet. See there for details.
        """
        WACC = 0.10

        # 2022 through 2025

        fcfs = [482e6 + 2.26 * 10.7e6, 267e6, 183e6, 116e6]
        
        value = NPV(WACC, fcfs) + discount(exit_TV(self.exit_multiple, 250e6), WACC, 4)

        net_debt = 550e6 - 1.25e6
        units = 10.7e6

        return (value - net_debt) / units