# app/models/vehicle.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id                  = Column(Integer, primary_key=True, index=True)
    make                = Column(String,  index=True, nullable=False)
    model               = Column(String,  index=True, nullable=False)
    driver_id           = Column(Integer, ForeignKey("users.id"), nullable=False)
    registration_number = Column(String, unique=True, index=True, nullable=False)
    company_id          = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # relationships
    driver  = relationship("User",    back_populates="vehicles")
    company = relationship("Company", back_populates="vehicles")
    bookings = relationship("Booking", back_populates="vehicle")