import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV, discount

class DO(Stock):
    """
    DO Stock
    """
    def __init__(self, floater_rate: float, exit_multiple: float):
        """
        Initializes DO object.
        """
        self.floater_rate = floater_rate
        self.exit_multiple = exit_multiple
        super().__init__("DO", "Diamond Offshore", "Oil", "Offshore Drilling", "NYSE")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10
        net_debt = 222e6

        # 5 yr build -- starts from 2022
        drillships = [4] * 5
        semisubs = [6] * 5
        
        # Diamond's semisubs may actually be worth more...
        # Could possibly be closer to 1 as multipler than 0.75 -- look at later
        rates = {
            "drillship" : 1,
            "semisub" : 0.75
        }

        revenues = []
        
        # on balance, contracts locked up until end of 2023...
        # this analysis could be improved as well by going through fleet one by one
        floater_rates = [200e3] * 2 + [self.floater_rate] * 3

        for i in range(5):
            revenue = 0
            revenue += drillships[i] * rates["drillship"] * floater_rates[i] * 365
            revenue += semisubs[i] * rates["semisub"] * floater_rates[i] * 365
            revenues.append(revenue)
        
        # assume 175k opex per drillship/semisub, 15k/day cold stacking cost for semisubs (3 cold stacked)
        contract_drilling_costs = []
        for i in range(5):
            contract_drilling_costs.append(175e3 * (drillships[i] + semisubs[i]) * 365 + 15e3 * 365 * 3)
        
        sga = 50e6

        ebitdas = []
        for i in range(5):
            ebitda = revenues[i] - contract_drilling_costs[i] - sga
            ebitdas.append(ebitda)

        # tax + capex
        fcfs = [ebitda * (1 - 0.21) - 60e6 for ebitda in ebitdas]
        
        fcfs[0] = -80e6 # 2022 guidance
        
        mcap = NPV(WACC, fcfs) + discount(exit_TV(self.exit_multiple, ebitdas[-1]), WACC, 5)
        shs = 105e6

        return mcap / shs