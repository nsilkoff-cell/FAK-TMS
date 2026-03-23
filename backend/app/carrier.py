"""
Carrier Model
Represents freight carriers/trucking companies
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Carrier(Base):
    """
    Carrier/Trucking Company Model
    Stores information about carriers that can haul loads
    """
    __tablename__ = "carriers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    name = Column(String(255), nullable=False, index=True)
    dot_number = Column(String(20), unique=True, nullable=True, index=True)
    mc_number = Column(String(20), unique=True, nullable=True)
    
    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address Information
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)
    zip_code = Column(String(10), nullable=True)
    country = Column(String(2), default="US", nullable=False)

    # Performance Metrics
    on_time_percentage = Column(Float, default=0.0)  # 0-100
    cost_per_mile = Column(Float, nullable=True)
    average_rating = Column(Float, default=0.0)  # 0-5 stars

    # Capacity Information
    available_trucks = Column(Integer, default=0)
    max_weight_capacity = Column(Float, nullable=True)  # in lbs
    
    # Equipment & Requirements
    equipment_type = Column(String(100), nullable=True)  # e.g., "Dry Van", "Flatbed", "Tanker"
    team_required = Column(Boolean, default=False)  # Whether load requires team driving
    hazmat_certified = Column(Boolean, default=False)
    special_certifications = Column(Text, nullable=True)  # JSON or comma-separated list

    # Driver Information
    primary_driver_name = Column(String(255), nullable=True)
    primary_driver_phone = Column(String(20), nullable=True)
    primary_driver_license = Column(String(50), nullable=True)
    
    # Compliance & Insurance
    insurance_status = Column(String(50), default="unknown")  # active, expired, pending
    insurance_expiry = Column(DateTime, nullable=True)
    safety_score = Column(Float, nullable=True)  # From Highway.com
    compliance_status = Column(String(50), default="unknown")  # compliant, warning, non-compliant
    
    # Status & Metadata
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # External IDs (for importing from old TMS)
    legacy_id = Column(String(50), unique=True, nullable=True, index=True)

    # Relationships
    rates = relationship("Rate", back_populates="carrier")
    loads = relationship("Load", back_populates="carrier")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_carrier_name_active', 'name', 'is_active'),
        Index('idx_carrier_dot', 'dot_number'),
        Index('idx_carrier_legacy', 'legacy_id'),
    )

    def __repr__(self):
        return f"<Carrier(id={self.id}, name='{self.name}', dot='{self.dot_number}')>"