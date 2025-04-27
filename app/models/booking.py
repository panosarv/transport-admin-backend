from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class BookingStatus(str, enum.Enum):
    upcoming = "upcoming"
    in_progress = "in_progress"
    completed = "completed"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.upcoming)
    pickup_time = Column(DateTime(timezone=True), nullable=False)
    dropoff_time = Column(DateTime(timezone=True), nullable=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    driver = relationship("User", back_populates="bookings")
    vehicle = relationship("Vehicle", back_populates="bookings")