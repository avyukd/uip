import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV

class BNNLF(Stock):
    """
    BNNLF stock.
    """
    def __init__(self, uranium_price: float, debt_mix: float):
        """
        Initializes BNNLF object.
        """
        self.uranium_price = uranium_price
        self.debt_mix = debt_mix
        super().__init__("BNNLF", "Bannerman Energy", "Uranium", "Developer", "OTC")
    
    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10

        # build out to 2040
        num_yrs = 19
        uranium_prices = [self.uranium_price] * 19
        etango_production = [0] * 4 + [1.75e6] * 1 + [3.5e6] * 13 + [1.75e6] * 1
        opex = [39.5] * 19 # includes royalties
        overhead = [1e6] * 19
        capex = [0] * 2 + [125e6] * 2 + [2e6] * 15
        tax_rate = [0.375] * 19
        tax_flag = [0] * 7 + [1] * 12 # 4 yrs at loss + 3 more years no taxes (?)

        fcfs = [0] * 19
        for i in range(num_yrs):
            ebit = etango_production[i] * (uranium_prices[i] - opex[i]) - overhead[i]
            if tax_flag[i]:
                fcfs[i] = ebit * (1 - tax_rate[i]) - capex[i]
            else:
                fcfs[i] = ebit - capex[i]
        
        bannerman_etango = (NPV(WACC, fcfs) + 150e6 * 0.5) * 0.95 # remaining pounds valued at $0.5/lb
        cash_raise_amt = 254e6 - 7e6 # 254 is capex + overhead pre-production, 7 is current amt of cash

        debt = cash_raise_amt * self.debt_mix
        equity_value = cash_raise_amt * (1 - self.debt_mix)
        shares_raised = equity_value / 0.15 # assuming 0.15 per share raise price
        total_shs = 1.5e9 + shares_raised

        return (bannerman_etango - debt) / total_shs