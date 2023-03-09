from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
#from sqlalchemy.orm import declarative_base

class certified_taxi_drivers():
    name: str
    phone: str
    addres: str

    def __init__(self, name:str, phone:str, addres:str):
        self.name = name
        self.phone = phone
        self.addres = addres

    def to_dict(self):
        return{
                'name': self.name,
                'phone': self.phone,
                'addres': self.addres
                }

#Base = declarative_base()
#
#class certified_taxi_drivers(Base):
#    __tablename__ = "certified_taxi_drivers"
#
#    id = Column(Integer, primary_key=True)
#    region = Column(String)
#    name = Column(String)
#    phone = Column(String)
#    addres = Column(String)
#    
#    def to_dict(self):
#        return{
#                'name': self.name,
#                'phone': self.phone,
#                'addres': self.addres
#                }
#
metadata_obj = MetaData()

cert_taxi_drivers_meta_data = Table(
        "certified_taxi_drivers",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("region", String(20)),
        Column("name", String(20)),
        Column("phone", String(12)),
        Column("addres", String(50)),
        )
