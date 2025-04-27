# app/models/company.py

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=True)

    # back-populate both sides
    vehicles = relationship("Vehicle", back_populates="company")
    users    = relationship("User",    back_populates="company")
