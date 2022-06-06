
from typing import List


def NPV(discount_rate: float, fcfs: List[float]) -> float:
    """
    Returns net present value of a cash flow series.
    """
    return sum([fcfs[i] / (1 + discount_rate) ** i for i in range(len(fcfs))])

def TV(terminal_growth_rate: float, last_yr_fcf: float, discount_rate: float) -> float:
    """
    Returns terminal value of a cash flow series.
    """
    return last_yr_fcf * (1 + terminal_growth_rate) / (discount_rate - terminal_growth_rate)