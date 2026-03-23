"""
Load Model
Represents freight loads/shipments
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Load(Base):
    """
    Load Model
    Represents a single freight shipment from pickup to delivery
    """
    __tablename__ = "loads"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Shipper/Customer Information
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Pickup Location
    pickup_location_id = Column(Integer, ForeignKey("stop_locations.id", ondelete="RESTRICT"), nullable=False)
    
    # Delivery Location
    delivery_location_id = Column(Integer, ForeignKey("stop_locations.id", ondelete="RESTRICT"), nullable=False)

    # Carrier Assignment
    carrier_id = Column(Integer, ForeignKey("carriers.id", ondelete="SET NULL"), nullable=True, index=True)

    # Load Details
    load_type = Column(String(50), nullable=True)  # dry_van, flatbed, tanker, etc.
    weight = Column(Float, nullable=True)  # in lbs
    dimensions = Column(String(100), nullable=True)  # e.g., "48x40x45"
    description = Column(Text, nullable=True)
    
    # Special Requirements
    team_required = Column(Boolean, default=False)
    hazmat = Column(Boolean, default=False)
    refrigerated = Column(Boolean, default=False)
    special_instructions = Column(Text, nullable=True)

    # Dates & Times
    pickup_date = Column(DateTime, nullable=True)
    delivery_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Rate Information
    shipper_rate = Column(Float, nullable=True)  # What customer is paying
    carrier_cost = Column(Float, nullable=True)  # What we pay the carrier
    margin_percentage = Column(Float, nullable=True)  # Calculated: (shipper_rate - carrier_cost) / shipper_rate * 100

    # Load Status
    status = Column(String(50), default="created", index=True)  # created, confirmed, assigned, in_transit, delivered, invoiced, archived
    
    # Performance Tracking
    actual_pickup_time = Column(DateTime, nullable=True)
    actual_delivery_time = Column(DateTime, nullable=True)
    on_time = Column(Boolean, default=None)  # null=not yet delivered, true=on time, false=late

    # Metadata
    reference_number = Column(String(100), unique=True, nullable=True, index=True)
    notes = Column(Text, nullable=True)
    
    # External IDs (for importing from old TMS)
    legacy_id = Column(String(50), unique=True, nullable=True, index=True)

    # Relationships
    customer = relationship("Customer", back_populates="loads")
    carrier = relationship("Carrier", back_populates="loads")
    pickup_location = relationship("StopLocation", foreign_keys=[pickup_location_id], back_populates="loads_pickup")
    delivery_location = relationship("StopLocation", foreign_keys=[delivery_location_id], back_populates="loads_delivery")
    rate = relationship("Rate", back_populates="load", uselist=False, cascade="all, delete-orphan")
    invoice = relationship("Invoice", back_populates="load", uselist=False, cascade="all, delete-orphan")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_load_status_created', 'status', 'created_at'),
        Index('idx_load_customer', 'customer_id'),
        Index('idx_load_carrier', 'carrier_id'),
        Index('idx_load_legacy', 'legacy_id'),
        Index('idx_load_reference', 'reference_number'),
    )

    def __repr__(self):
        return f"<Load(id={self.id}, customer_id={self.customer_id}, status='{self.status}')>"