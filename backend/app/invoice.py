"""
Invoice Model
Represents billing records for loads
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Invoice(Base):
    """
    Invoice Model
    Stores invoicing information for completed loads
    Tracks what we charge customers and what we owe carriers
    """
    __tablename__ = "invoices"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Foreign Key
    load_id = Column(Integer, ForeignKey("loads.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Shipper/Customer Invoice
    shipper_invoice_number = Column(String(100), unique=True, nullable=True, index=True)
    shipper_invoice_amount = Column(Float, nullable=False)  # What we charge customer
    shipper_invoice_status = Column(String(50), default="draft")  # draft, sent, paid, overdue
    shipper_invoice_date = Column(DateTime, nullable=True)
    shipper_payment_received_date = Column(DateTime, nullable=True)

    # Carrier Invoice
    carrier_invoice_number = Column(String(100), unique=True, nullable=True, index=True)
    carrier_invoice_amount = Column(Float, nullable=False)  # What we owe carrier
    carrier_invoice_status = Column(String(50), default="draft")  # draft, sent, approved, paid
    carrier_invoice_date = Column(DateTime, nullable=True)
    carrier_payment_made_date = Column(DateTime, nullable=True)

    # Financial Summary
    total_revenue = Column(Float, nullable=False)  # shipper_invoice_amount
    total_cost = Column(Float, nullable=False)  # carrier_invoice_amount
    gross_profit = Column(Float, nullable=False)  # total_revenue - total_cost
    profit_margin_percentage = Column(Float, nullable=False)  # (gross_profit / total_revenue) * 100

    # Invoice Dates
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Status
    is_finalized = Column(Boolean, default=False)  # True once both invoices are set
    notes = Column(Text, nullable=True)
    
    # External IDs (for importing from old TMS)
    legacy_id = Column(String(50), unique=True, nullable=True, index=True)

    # Relationships
    load = relationship("Load", back_populates="invoice")

    # Indexes for common queries
    __table_args__ = (
        Index('idx_invoice_shipper_status', 'shipper_invoice_status'),
        Index('idx_invoice_carrier_status', 'carrier_invoice_status'),
        Index('idx_invoice_created', 'created_at'),
    )

    def __repr__(self):
        return f"<Invoice(id={self.id}, load_id={self.load_id}, profit={self.gross_profit})>"