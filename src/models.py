from typing import Optional
from dataclasses import dataclass


@dataclass
class certified_taxi_drivers():
    name: Optional[str]
    phone: Optional[str]
    addres: Optional[str]

    def to_list(self) -> list[Optional[str]]:
        return [self.name, self.phone, self.addres]


@dataclass
class city_partners_organizatons():
    id: Optional[str]
    name: Optional[str]
    full_name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]

    def to_list(self) -> list[Optional[str]]:
        return [self.id, self.name, self.full_name, self.ogrn, self.inn]
