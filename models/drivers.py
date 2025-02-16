from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class Driver(Base):
    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    driver_uuid = Column(String(255), unique=True, nullable=False)
    partner_uuid = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(255))
    state = Column(String(255))
    has_cash_payment = Column(Boolean)
    inactivity_reason = Column(String(255))