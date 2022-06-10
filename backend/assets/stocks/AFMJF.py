import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, exit_TV, discount

class AFMJF(Stock):
    """
    AFMJF Stock
    """
    def __init__(self, tin_price: float, exit_multiple: float):
        """
        Initializes AFMJF object.
        """
        self.tin_price = tin_price
        self.exit_multiple = exit_multiple
        super().__init__("AFMJF", "Alphamin Resources", "Tin", "Miner", "OTC")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        WACC = 0.10

        # 10 yr build to 2032, exit_TV since Mpama South will be around

        fcfs = []
        fcf_2022 = 200e6
        fcfs.append(fcf_2022)

        mpama_north_production = [15, 16, 16, 17, 14, 16, 9, 7, 8, 7, 2]
        mpama_south_production = [0] * 4 + [3] + [7] * 6

        mpama_north_AISC, mpama_south_AISC = 15000, 16000
        tax_rate = 0.35

        capex = [30e6] * 3 + [150e6] + [30e6] * 7

        for i in range(1, 11):
            mpama_north_margin = mpama_north_production[i] * 1000 * (self.tin_price - mpama_north_AISC)
            mpama_south_margin = mpama_south_production[i] * 1000 * (self.tin_price - mpama_south_AISC)
            ebitda = mpama_north_margin + mpama_south_margin
            fcfs.append(ebitda * (1 - tax_rate) - capex[i])
        
        mcap = NPV(WACC, fcfs) + discount(exit_TV(self.exit_multiple, ebitda), WACC, 10)

        shs = 1.27e9

        return mcap / shs