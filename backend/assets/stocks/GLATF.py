import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV, discount

class GLATF(Stock):
    """
    GLATF stock.
    """
    def __init__(self, uranium_price: float, exit_multiple: float, debt_mix: float):
        """
        Initializes GLATF object.
        """
        self.uranium_price = uranium_price
        self.exit_multiple = exit_multiple
        super().__init__("GLATF", "Global Atomic", "Uranium", "Developer", "OTC")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10

        # build out to 2040
        num_yrs = 19

        uranium_prices = [self.uranium_price] * 19
        dasa_phase_1_production = [0] * 3 + [4.79e6] * 7 + [2.30e6] * 4 + [0] * 5
        dasa_phase_2_production = [0] * 11 + [1e6] * 1 + [3e6] * 2 + [5e6] * 5

        cash_costs = [0] * 3 + [12.36] * 7 + [24.20] * 4 + [30] * 5 

        company_overhead = [10e6] * 3 + [5e6] * 16

        op_profit = [
            (uranium_prices[i] - cash_costs[i]) * 
            (dasa_phase_1_production[i] + dasa_phase_2_production[i]) - company_overhead[i] 
            for i in range(num_yrs)
        ]

        royalties = [0.12] * 19
        for i in range(num_yrs):
            if cash_costs[i] / uranium_prices[i] > 0.5:
                royalties[i] = 0.09
        
        expansion_capex = [0] * 1 + [103.8e6] * 2 + [0] * 7 + [50e6] * 2 + [0] * 7
        sustaining_capex = [0] * 3 + [10e6] * 16

        tax_rate = [0] * 5 + 14 # 3 yrs during dev - negative operating profit + 2 yrs of carry over no tax (?)

        fcfs = []
        for i in range(num_yrs):
            if op_profit[i] > 0:
                fcfs.append(
                    op_profit[i] * (1 - tax_rate[i] - royalties[i]) - expansion_capex[i] - sustaining_capex[i]
                )
        
        Dasa = NPV(WACC, fcfs) + discount(exit_TV(self.exit_multiple, op_profit[-1]), WACC, num_yrs)
        Dasa *= 0.9 # global owns 90%

        zinc_plant_ebitda = 15e6
        zinc_plant_multiple = 5
        zinc_plant_value = zinc_plant_ebitda * zinc_plant_multiple

        # how much will it take to finance DASA
        capex = 200e6 
        cash = 25e6 

        debt = (capex - cash) * self.debt_mix    
        equity_financing = (capex - cash) * (1 - self.debt_mix)

        shares_sold = equity_financing / 3.0 # assume 3 dollar share price

        total_shares = 177e6 + shares_sold

        exploration_assets_value = 15e6 # just for geeks, $0.25/lb in the ground

        return (Dasa + zinc_plant_value - debt) / total_shares