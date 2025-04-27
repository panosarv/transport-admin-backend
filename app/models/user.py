# app/models/user.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String,  unique=True, index=True, nullable=False)
    email           = Column(String,  unique=True, index=True, nullable=False)
    hashed_password = Column(String,                nullable=False)
    role_id         = Column(Integer, ForeignKey("roles.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # relationships
    role      = relationship("Role",    back_populates="users")
    vehicles  = relationship("Vehicle", back_populates="driver")
    company   = relationship("Company", back_populates="users")
    bookings  = relationship("Booking", back_populates="driver")