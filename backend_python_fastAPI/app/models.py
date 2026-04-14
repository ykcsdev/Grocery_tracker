from sqlalchemy import (
    Column, String, Numeric, Boolean, Integer,
    DateTime, ForeignKey, Text
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import uuid
class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    #user_id = Column(UUID(as_uuid=True), nullable=True)
    user_id = Column(Numeric)

    merchant_name = Column(Text, nullable=False)
    merchant_chain = Column(Text, nullable=False)
    branch_name = Column(Text)

    street = Column(Text)
    city = Column(Text)
    country = Column(String(2), default="LT")

    invoice_number = Column(Text)
    receipt_number = Column(Text)
    file_path = Column(Text)

    purchase_datetime = Column(DateTime)
    currency = Column(String(3), default="EUR")
    payment_method = Column(Text)

    gross_subtotal = Column(Numeric(10, 2))
    discount_total = Column(Numeric(10, 2), default=0)
    net_subtotal = Column(Numeric(10, 2))
    tax_total = Column(Numeric(10, 2))
    rounding_adjustment = Column(Numeric(10, 2), default=0)
    total_paid = Column(Numeric(10, 2))

    status = Column(Text, default="not_processed")
    confidence_score = Column(Numeric(4, 2))

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    items = relationship("ReceiptItem", back_populates="receipt", cascade="all, delete")
    taxes = relationship("ReceiptTax", back_populates="receipt", cascade="all, delete")
    loyalty = relationship("ReceiptLoyalty", uselist=False, back_populates="receipt", cascade="all, delete")
    confidence = relationship("ReceiptConfidence", uselist=False, back_populates="receipt", cascade="all, delete")
    source = relationship("ReceiptSource", uselist=False, back_populates="receipt", cascade="all, delete")
    def update_totals(self):
        self.discount_total = sum(item.discount for item in self.items)
        self.net_subtotal = sum(item.line_total for item in self.items)
        self.total_paid = self.net_subtotal - self.discount_total


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)

    line_number = Column(Integer)

    product_name = Column(Text, nullable=False)
    normalized_name = Column(Text)
    category = Column(Text)

    quantity = Column(Numeric(10, 3), nullable=False)
    unit = Column(Text, nullable=False)

    unit_price = Column(Numeric(10, 2))
    line_total = Column(Numeric(10, 2))
    discount = Column(Numeric(10, 2), default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    receipt = relationship("Receipt", back_populates="items")

class ReceiptTax(Base):
    __tablename__ = "receipt_taxes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), nullable=False)

    tax_type = Column(Text, nullable=False)
    tax_rate_percent = Column(Numeric(5, 2))
    taxable_amount = Column(Numeric(10, 2))
    tax_amount = Column(Numeric(10, 2))

    receipt = relationship("Receipt", back_populates="taxes")


class ReceiptLoyalty(Base):
    __tablename__ = "receipt_loyalty"

    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), primary_key=True)

    program_name = Column(Text)
    card_used = Column(Boolean, default=False)
    points_earned = Column(Integer)
    discount_from_loyalty = Column(Numeric(10, 2))

    receipt = relationship("Receipt", back_populates="loyalty")

class ReceiptConfidence(Base):
    __tablename__ = "receipt_confidence"

    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), primary_key=True)

    overall = Column(Numeric(4, 2))
    missing_fields = Column(ARRAY(Text))

    receipt = relationship("Receipt", back_populates="confidence")

class ReceiptSource(Base):
    __tablename__ = "receipt_source"

    receipt_id = Column(UUID(as_uuid=True), ForeignKey("receipts.id"), primary_key=True)

    upload_type = Column(Text)
    original_filename = Column(Text)
    processed_by = Column(Text)

    receipt = relationship("Receipt", back_populates="source")
