from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class certified_taxi_drivers(Base):
    __tablename__ = "certified_taxi_drivers"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    region = Column(String)
    phone = Column(Integer)
    addres = Column(String)
