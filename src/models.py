from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base


Base = declarative_base()

#class certified_taxi_drivers(Base):
#    __tablename__ = "certified_taxi_drivers"
#
#    id = Column(Integer, primary_key=True)
#    region = Column(String)
#    name = Column(String)
#    phone = Column(Integer)
#    addres = Column(String)

metadata_obj = MetaData()

cert_taxi_drivers = Table(
        "certified_taxi_drivers",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("region", String(20)),
        Column("name", String(20)),
        Column("phone", String(12)),
        Column("addres", String(50)),
        )
