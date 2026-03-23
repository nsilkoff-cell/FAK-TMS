"""
Customer/Shipper Model
Represents freight shippers and customers
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Customer(Base):
    """
    Customer/Shipper Model
    Stores information about companies that ship freight
    """
    __tablename__ = "customers"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Basic Information
    company_name = Column(String(255), nullable=False, index=True)
    contact_name = Column(String(255), nullable=True)
    
    # Contact Information
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Billing Address
    billing_address = Column(String(255), nullable=True)
    billing_city = Column(String(100), nullable=True)
    billing_state = Column(String(2), nullable=True)
    billing_zip = Column(String(10), nullable=True)
    
    # Shipping Address (can differ from billing)
    shipping_address = Column(String(255), nullable=True)
    shipping_city = Column(String(100), nullable=True)
    shipping_state = Column(String(2), nullable=True)
    shipping_zip = Column(String(10), nullable=True)