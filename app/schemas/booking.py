from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, Literal, List
from app.models.booking import BookingStatus

# Base fields
class BookingBase(BaseModel):
    vehicle_id: int
    status: BookingStatus
    pickup_time: datetime
    dropoff_time: Optional[datetime]
    origin: str
    destination: str
    price: int

class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    id: int
    driver_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Listing filters
class BookingFilter(BaseModel):
    status: Optional[BookingStatus] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

# Reporting
TimeframeLiteral = Literal['daily','weekly','monthly','yearly']

class EarningsReport(BaseModel):
    period: str
    total: float

class CountReport(BaseModel):
    period: str
    count: int

class ReportParams(BaseModel):
    timeframe: Optional[TimeframeLiteral] = None
    year: Optional[int] = None
    month: Optional[int] = None
    day: Optional[date] = None

UpdateStatusLiteral = Literal["upcoming","in_progress","completed"]  
class StatusUpdate(BaseModel):
    status: UpdateStatusLiteral
