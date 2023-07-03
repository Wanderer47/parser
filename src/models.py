from typing import Optional
from dataclasses import dataclass


@dataclass
class Certified_taxi_drivers():
    region: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    address: Optional[str]


@dataclass
class City_partners_organizatons():
    park_id: Optional[str]
    name: Optional[str]
    full_name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]
