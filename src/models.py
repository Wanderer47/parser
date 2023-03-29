from typing import Optional
from dataclasses import dataclass


@dataclass
class certified_taxi_drivers():
    name: str
    phone: str
    addres: str

    def to_list(self) -> list[str]:
        return [self.name, self.phone, self.addres]

@dataclass
class city_partners_organizatons():
    name: Optional[str]
    full_name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]

    def to_list(self) -> list[Optional[str]]:
        return [self.name, self.full_name, self.ogrn, self.inn]

