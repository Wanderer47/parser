from typing import Optional


class certified_taxi_drivers():
    name: str
    phone: str
    addres: str

    def __init__(self, name:str, phone:str, addres:str) -> None:
        self.name = name
        self.phone = phone
        self.addres = addres

    def to_dict(self) -> dict[str, str]:
        return{
                'name': self.name,
                'phone': self.phone,
                'addres': self.addres
                }

class city_partners_organizatons():
    name: Optional[str]
    ogrn: Optional[str]
    inn: Optional[str]

    def __init__(self, name:Optional[str], ogrn:Optional[str], inn:Optional[str]) -> None:
        self.name = name
        self.ogrn = ogrn
        self.inn = inn

    def to_dict(self) -> dict[Optional[str], Optional[str]]:
        return{
                'name': self.name,
                'ogrn': self.ogrn,
                'inn': self.inn
                }

