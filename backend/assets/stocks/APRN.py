import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import exit_TV, discount

class APRN(Stock):
    """
    APRN stock.
    """
    def __init__(self):
        """
        Initializes APRN stock object.
        """
        super().__init__("APRN", "Blue Apron Holdings", "Consumer Cyclical", "Internet Retail", "NYSE")

    def get_intrinsic_value(self):
        """
        Returns APRN's intrinsic value.
        """
        net_cash = 55e6 - 30e6
        nj_facility = 75e6 # conservative estimate of new jersey facility, 495000 sq ft
        # note that liquidation value of fairfield center, other property not included here

        # value rest of business
        num_customers = 400e3
        avg_num_orders_per_customer = 5 * 4 # 5 = quarterly num
        avg_order_cost = 10
        long_term_ebitda_margin = 1 - (0.40 + 0.20 + 0.15) # 40% variable margin, 20% ptga, 15% added for risk

        # slap a low multiple on long term ebidta, discount back 5-6 years, call it a day lol
        long_term_ebitda = num_customers * avg_num_orders_per_customer * avg_order_cost * long_term_ebitda_margin
        multiple = 3
        tv = discount(exit_TV(multiple, long_term_ebitda), 0.10, 5)

        # discount it back and add everything up
        mcap = tv + net_cash + nj_facility
        shs = 34.37e6 * (1 + 0.5) # 50% dilution

        return mcap / shs