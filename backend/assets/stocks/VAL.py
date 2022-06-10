import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV, discount

class VAL(Stock):
    """
    VAL Stock
    """
    def __init__(self, floater_rate: float, jackup_rate: float, exit_multiple: float):
        """
        Initializes PLTR object.
        """
        self.floater_rate = floater_rate
        self.jackup_rate = jackup_rate
        self.exit_multiple = exit_multiple
        super().__init__("VAL", "Valaris", "Oil", "Offshore Drilling", "NYSE")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10

        # 5 yr build -- starts from 2022
        drillships = [7, 7, 8, 9, 9]
        hdh_jackups = [4] * 5
        hdm_jackups = [8] * 4 + [9]
        hduh_jackups = [7] * 5
        sdl_jackups = [2] * 2 + [0] * 4
        sdm_jackups = [8] * 5
        semisubs = [3] * 4 + [4]
        
        rates = {
            "drillship" : 1,
            "hdh_jackup" : 0.9,
            "hdm_jackup" : 0.7,
            "hduh_jackup" : 1,
            "sdl_jackup" : 0.6,
            "sdm_jackup" : 0.7,
            "semisub" : 0.75
        }

        revenues = []
        floater_rates = [300e3] + [self.floater_rate] * 4
        jackup_rates = [100e3] + [self.jackup_rate] * 4
        for i in range(5):
            revenue = 0
            revenue += drillships[i] * rates["drillship"] * floater_rates[i] * 365
            revenue += hdh_jackups[i] * rates["hdh_jackup"] * jackup_rates[i] * 365
            revenue += hdm_jackups[i] * rates["hdm_jackup"] * jackup_rates[i] * 365
            revenue += hduh_jackups[i] * rates["hduh_jackup"] * jackup_rates[i] * 365
            revenue += sdl_jackups[i] * rates["sdl_jackup"] * jackup_rates[i] * 365
            revenue += sdm_jackups[i] * rates["sdm_jackup"] * jackup_rates[i] * 365
            revenue += semisubs[i] * rates["semisub"] * floater_rates[i] * 365
            revenues.append(revenue)
        
        contract_drilling_costs = []
        base = 750e6 * (12 / 8) * 1.05
        for i in range(5):
            contract_drilling_costs.append(base * (1.03) ** i)
        
        sga = 100e6

        aro_ebits = [80e6] + [102.857e6] * 4

        ebits = []
        for i in range(5):
            ebit = revenues[i] - contract_drilling_costs[i] - sga + aro_ebits[i]
            ebits.append(ebit)

        # tax + capex
        fcfs = [ebit * (1 - 0.21) - 225e6 for ebit in ebits]

        mcap = NPV(WACC, fcfs) + discount(exit_TV(self.exit_multiple, ebits[-1]), WACC, 5)
        shs = 75e6

        return mcap / shs