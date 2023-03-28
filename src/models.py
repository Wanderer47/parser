from typing import Optional
from dataclasses import dataclass


@dataclass
class certified_taxi_drivers():
    name: str
    phone: str
    addres: str

    def to_dict(self) -> dict[str, str]:
        return{
                'name': self.name,
                'phone': self.phone,
                'addres': self.addres
                }

@dataclass
class city_partners_organizatons():
    name: Optional[str]
    full_name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]

    def to_dict(self) -> dict[Optional[str], Optional[str]]:
        return{
                'name': self.name,
                'full_name': self.full_name,
                'ogrn': self.ogrn,
                'inn': self.inn
                }

