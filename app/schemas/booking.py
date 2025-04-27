from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.booking import BookingStatus

class BookingBase(BaseModel):
    vehicle_id: int
    status: BookingStatus
    pickup_time: datetime
    dropoff_time: Optional[datetime]
    origin: str
    destination: str
    driver_id: Optional[int] = None  # ID of the driver assigned to the booking

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    user_id: int  # the driver
    created_at: datetime

    class Config:
        orm_mode = True