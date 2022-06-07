"""
Indicators/Signals/Values derived from base classes or other input streams.
Could be things like ratios, crack spreads, etc.
"""
from base import CommodityCurve
from enums import Commodity

def get_312_crack_spread():
    """
    Returns 312 crack spread.
    """
    diesel_prices = CommodityCurve(Commodity.DIESEL).annual_prices
    gasoline_prices = CommodityCurve(Commodity.GASOLINE).annual_prices
    wti_prices = CommodityCurve(Commodity.WTI).annual_prices

    crack_spread = []
    for i in range(min(len(diesel_prices), len(gasoline_prices), len(wti_prices))):
        spread = (1 * gasoline_prices[i][1] * 42 + 2 * diesel_prices[i][1] * 42 - 3 * wti_prices[i][1]) / 3
        crack_spread.append([diesel_prices[i][0], spread])
    
    return crack_spread
