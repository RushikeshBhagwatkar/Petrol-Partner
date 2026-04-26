from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Ride(Base):
    __tablename__ = "rides"

    id = Column(String, primary_key=True)
    driver_id = Column(String, index=True)
    driver_name = Column(String)
    
    from_city = Column(String, index=True)
    to_city = Column(String, index=True)
    
    # In production with PostGIS, use:
    # origin_point = Column(Geometry('POINT'))
    # destination_point = Column(Geometry('POINT'))
    
    # Standard fields for mock/fallback
    origin_lat = Column(Float)
    origin_lng = Column(Float)
    dest_lat = Column(Float)
    dest_lng = Column(Float)
    
    date = Column(String)
    time = Column(String)
    
    total_seats = Column(Integer)
    seats_left = Column(Integer)
    
    price_per_seat = Column(Float)
    fuel_type = Column(String)
    status = Column(String, default="scheduled")  # scheduled, arrived, started, completed, cancelled
    
    is_pink_mode = Column(Boolean, default=False)
    meeting_hub = Column(String)
    dropoff_hub = Column(String)
    
    created_at = Column(DateTime, server_default=func.now())
