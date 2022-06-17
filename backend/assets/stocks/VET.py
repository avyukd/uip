import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import NPV, discount

class VET(Stock):
    """
    VET stock.
    """
    def __init__(self, fcf_multiple: float):
        """
        Initializes VET object.
        """
        self.fcf_multiple = fcf_multiple
        super().__init__("VET", "Vermilion Energy", "Oil", "Producer", "NYSE")

    def get_intrinsic_value(self):
        """
        Not a complete model.
        Use FCF estimates out to 2024.
        """
        fcfs = [1.8e9, 1.0e9, 1.0e9]
        mcap = NPV(0.10, fcfs) + discount(fcfs[-1] * self.fcf_multiple) - 1.6e9
        shs = 170e6
        cadusd = 0.77
        return (mcap * cadusd) / shs