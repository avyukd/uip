import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, TV

class PLTR(Stock):
    """
    PLTR class.
    """
    def __init__(self, gov_growth_rate: float, comm_growth_rate: float, tech_terminal_growth_rate: float,
                dilution: float):
        """
        Initializes PLTR object.
        """
        self.gov_growth_rate = gov_growth_rate
        self.comm_growth_rate = comm_growth_rate
        self.terminal_growth_rate = tech_terminal_growth_rate
        self.dilution = dilution
        super().__init__("PLTR", "Palantir", "Technology", "Software", "NYSE")

    def get_intrinsic_value(self):
        """
        Returns company's intrinsic value based on DCF valuation.
        All numbers are up to date as of 6/5/2022
        """
        num_gov_customers, num_comm_customers, num_big_accounts = 137, 100, 20
        big_account_pct = num_big_accounts / (num_gov_customers + num_comm_customers)
        avg_num_users, pricing_per_user = 500, 11666.67

        # 10 yr build
        revenues = []
        acq_revenue = 0
        big_account_rev = 40000000
        curr_gov_customers, curr_comm_customers = num_gov_customers, num_comm_customers
        new_customers = 0
        for _ in range(10):
            revenue = 0
            revenue += big_account_rev * (big_account_pct * (curr_gov_customers + curr_comm_customers))
            revenue += avg_num_users * pricing_per_user * ((curr_gov_customers + curr_comm_customers) * (1 - big_account_pct) - new_customers)
            revenues.append(revenue)

            new_customers = curr_gov_customers * self.gov_growth_rate + curr_comm_customers * self.comm_growth_rate
            curr_gov_customers *= (1 + self.gov_growth_rate)
            curr_comm_customers *= (1 + self.comm_growth_rate)

        ebits = []
        sga = 1000000000
        stock_comp = 1000000000
        # large assumption - unclear if correct
        stock_comp_change = [-0.2, -0.05] + [0] * 3 + [0.05, 0.2, 0, 0, 0]
        for i in range(10):
            ebit = revenues[i] - sga - stock_comp
            ebits.append(ebit)

            stock_comp += stock_comp_change[i] * stock_comp
        
        taxes = [0] * 3 + [0.21] * 7
        capex = [300000000] * 10

        fcfs = [ebit * taxes[i] - capex[i] for i in range(len(ebits))]

        wacc, cash, debt = 0.1050, 2.269e9, 500e6

        mcap = NPV(wacc, fcfs) + TV(self.terminal_growth_rate, fcfs[-1], wacc) + cash - debt

        shs = 2e9 * (1 + self.dilution)

        return mcap / shs
