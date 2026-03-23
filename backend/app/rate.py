"""
Rate Model
Represents pricing for a load (shipper rate + carrier cost)
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Rate(Base):
    """
    Rate Model
    Stores pricing information for loads
    Each load has one rate: what we charge shipper vs what we pay carrier
    """
    __tablename__ = "rates"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Keys
    load_id = Column(Integer, ForeignKey("loads.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Pricing
    shipper_rate = Column(Float, nullable=False)  # Total amount customer pays
    carri