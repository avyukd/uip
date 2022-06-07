import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV
from indicators import get_312_crack_spread
class VTNR(Stock):
    """
    VTNR class.
    """
    def __init__(self, discount_to_crack_spread: float, utilization_rate: float, exit_multiple: float):
        """
        Initializes VTNR object.
        """
        self.discount_to_crack_spread = discount_to_crack_spread
        self.utilization_rate = utilization_rate
        self.exit_multiple = exit_multiple
        super().__init__("VTNR", "Oil", "Downstream", "NASDAQ")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10
        cash, debt, exmobile_value = 24e6, 1e6, 200e6 # current portion of long-term debt, value of business - mobile refinery
        
        # $13 is 5-yr trailing average 
        crack_spreads = [x[1] for x in get_312_crack_spread()] + [13]
        capacity = 75000
        fcf_margins = [0.35, 0.40] + [0.45] * (len(crack_spreads) - 2) # based on 2022 + 2023 guidance
        utilization_rates = [0.90] + [self.utilization_rate] * (len(crack_spreads) - 1)

        fcfs = []

        operating_days_2022 = 274
        hedge_price = 13 * 1.25 # hedged 50% of production for 2H22
        fcfs.append((hedge_price + crack_spreads[0]) * (capacity / 2) * (utilization_rates[0]) * operating_days_2022 * fcf_margins[0])

        for i in range(1, len(crack_spreads)):
            fcfs.append(crack_spreads[i] * (1 - self.discount_to_crack_spread) * capacity * 365 * utilization_rates[i] * fcf_margins[i])
        
        last_yr_EBITDA = fcfs[-1] * (1 / fcf_margins[-1]) * 0.70 # using 0.70 as EBITDA margin

        mcap = NPV(WACC, fcfs) + exit_TV(self.exit_multiple, last_yr_EBITDA) + cash + exmobile_value - debt

        shs = 94e6 # fully diluted

        return mcap / shs
