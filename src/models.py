from typing import Optional
from dataclasses import dataclass


@dataclass
class Certified_taxi_drivers():
    region: Optional[str]
    name: Optional[str]
    phone: Optional[str]
    addres: Optional[str]

    def to_dict(self) -> dict[Optional[str], Optional[str]]:
        return {
                'REGION': self.region,
                'NAME': self.name,
                'PHONE': self.phone,
                'ADDRESS': self.addres
                }


@dataclass
class City_partners_organizatons():
    id: Optional[str]
    name: Optional[str]
    full_name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]

    def to_dict(self) -> dict[Optional[str], Optional[str]]:
        return {
                'PARK_ID': self.id,
                'NAME': self.name,
                'FULL_NAME': self.full_name,
                'OGRN': self.ogrn,
                'INN': self.inn
                }
