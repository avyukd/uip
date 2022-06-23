from enum import Enum

class Commodity(Enum):
    DIESEL = "23%3D1"
    GASOLINE = "27%3D2"
    WTI = "CL"
    COPPER = "HG"
    NEWC_COAL = "NCF-ICE"
    TIN = "tin"
    URANIUM = "uranium-futures"

class Forex(Enum):
    AUD = "QAD"

class Direction(Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NA = "NA"