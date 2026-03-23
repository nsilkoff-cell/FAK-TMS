"""
Stop Location Model
Represents pickup and delivery locations
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StopLocation(Base):
    """
    Stop Location Model
    Represents warehouses, distribution centers, and other shipping locations
    Can be associated with customers
    """
    __tablename__ = "stop_locations"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Location Information
    location_name = Column(String(255), nullable=False, index=True)
    location_type = Column(String(50), nullable=True)  # warehouse, distribution_center, retail, factory, etc.
    
    # Address Information
    address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False)
    zip_code = Column(String(10), nullable=True)
    country = Column(String(2), default="US", nullable=False)

    # GPS Coordinates (for mapping/routing)
    latitude = Column