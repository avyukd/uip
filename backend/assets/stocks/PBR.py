import sys

sys.path.append("C:/Users/avyuk/stocks/uip/backend/")

from base import Stock
from utils import detail_factory

class PBR(Stock):
    """
    UAN stock.
    """
    def __init__(self, fcf_multiple: float):
        """
        Initializes UAN object.
        """
        self.fcf_multiple = fcf_multiple
        super().__init__("PBR", "Petrobras", "Oil", "Producer", "NYSE")

    def get_intrinsic_value(self):
        """
        Not a complete model.
        """
        self.fcf = 30e9
        value = self.fcf * self.fcf_multiple
        self.shs = 6.522e9

        detail_factory(self)
        
        return value / self.shs