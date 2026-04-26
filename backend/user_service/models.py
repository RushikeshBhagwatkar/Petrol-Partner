from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    uid = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    photo_url = Column(String)
    
    gender = Column(String)
    phone = Column(String)
    
    # Trust & Verification
    trust_score = Column(Float, default=50.0) # 0-100 scale
    verification_level = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    
    # Feature specific
    upi_id = Column(String)
    wallet_balance = Column(Float, default=0.0)
    
    # Metadata
    emergency_contacts = Column(JSON, default=[])
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class TrustEvent(Base):
    __tablename__ = "trust_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uid = Column(String, index=True)
    event_type = Column(String) # ride_completed, cancellation, complaint, verified
    score_delta = Column(Float)
    description = Column(String)
    created_at = Column(DateTime, server_default=func.now())
