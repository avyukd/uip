# generated by datamodel-codegen:
#   filename:  defaults.json
#   timestamp: 2022-06-10T19:39:16+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Generics(BaseModel):
    tech_terminal_growth_rate: Optional[float] = None
    thermal_coal_terminal_growth_rate: Optional[float] = None
    floater_rate: Optional[float] = None
    jackup_rate: Optional[float] = None
    tin_price: Optional[float] = None
    newc_coal_price: Optional[float] = None
    margin_of_safety: Optional[float] = None


class PLTR(BaseModel):
    gov_growth_rate: Optional[float] = None
    comm_growth_rate: Optional[float] = None
    dilution: Optional[float] = None


class VTNR(BaseModel):
    discount_to_crack_spread: Optional[float] = None
    utilization_rate: Optional[float] = None
    exit_multiple: Optional[float] = None


class WHITF(BaseModel):
    exit_multiple: Optional[float] = None


class VAL(BaseModel):
    exit_multiple: Optional[float] = None


class AFMJF(BaseModel):
    exit_multiple: Optional[float] = None


class DO(BaseModel):
    exit_multiple: Optional[float] = None


class Model(BaseModel):
    generics: Optional[Generics] = None
    PLTR: Optional[PLTR] = None
    VTNR: Optional[VTNR] = None
    WHITF: Optional[WHITF] = None
    VAL: Optional[VAL] = None
    AFMJF: Optional[AFMJF] = None
    DO: Optional[DO] = None
