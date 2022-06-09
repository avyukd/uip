import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from enums import Forex
from exceptions import MustSpecifyValuationTechnique
from base import CommodityCurve, Stock
from enums import Commodity
from typing import Union
from utils import NPV, TV, exit_TV

class WHITF(Stock):
    """
    WHITF class.
    """
    def __init__(self, newc_coal_price: Union[float, str], thermal_coal_terminal_growth_rate: Union[float, str], exit_multiple: Union[float, str]):
        """
        Initializes WHITF object.
        - coal_price is user input or NULL for commodity curve
        - Null for growth rate or multiple means just use one valuation technique
        """
        if newc_coal_price != "NULL":
            self.coal_curve = [[yr, newc_coal_price] for yr in range(2022, 2027, 1)]
        else:
            self.coal_curve = CommodityCurve(Commodity.NEWC_COAL).get_annual_prices()

        self.AUD_curve = CommodityCurve(Forex.AUD).get_annual_prices()
        
        if thermal_coal_terminal_growth_rate == "NULL":
            self.terminal_growth_rate = None
        else:
            self.terminal_growth_rate = thermal_coal_terminal_growth_rate

        if exit_multiple == "NULL":
            self.exit_multiple = None
        else:
            self.exit_multiple = exit_multiple
        
        if self.exit_multiple is None and self.terminal_growth_rate is None:
            raise MustSpecifyValuationTechnique("Must provide either exit multiple or terminal growth rate.")
        
        super().__init__("WHITF", "Whitehaven Coal", "Coal", "Producer", "OTC")    

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        """
        
        WACC = 0.10

        num_yrs = min(len(self.coal_curve), len(self.AUD_curve))

        coal_mt_pa, pct_thermal, discount_to_spot, royalty, cash_cost = \
            [20e6] * num_yrs, [0.8] * num_yrs, [0.15] * num_yrs, [0.08] * num_yrs, [84] * num_yrs

        ebitdas = []
        for i in range(num_yrs):
            thermal_coal_mt = coal_mt_pa[i] * pct_thermal[i]
            coal_price_AUD = self.coal_curve[i][1] / self.AUD_curve[i][1]
            realised_per_ton = coal_price_AUD * (1 - discount_to_spot[i]) * (1 - royalty[i])
            margin_per_ton = realised_per_ton - cash_cost[i]
            ebitdas.append(thermal_coal_mt * margin_per_ton)
        
        tax_rate, capex = 0.30, [100e6] * num_yrs
        fcfs = [ebitdas[i] * (1 - tax_rate) - capex[i] for i in range(num_yrs)]

        npv = NPV(WACC, fcfs)
        
        tv_estimates = []
        if self.terminal_growth_rate is not None:
            tv_estimates.append(TV(self.terminal_growth_rate, fcfs[-1], WACC))
        
        if self.exit_multiple is not None:
            tv_estimates.append(exit_TV(self.exit_multiple, ebitdas[-1]))

        tv = sum(tv_estimates) / len(tv_estimates)

        mcap = npv + tv

        # TODO: not entirely sure how to convert WHC to WHITF price
        # needs to be converted back to usd
        mcap_usd = mcap * self.AUD_curve[-1][1]
        shs = 990e6

        return mcap_usd / shs

