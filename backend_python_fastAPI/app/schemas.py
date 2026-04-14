from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid


class ReceiptUploadResponse(BaseModel):
    receipt_id: uuid.UUID
    status: str


class ProcessingStatusResponse(BaseModel):
    receipt_id: uuid.UUID
    status: str


class InvoiceListItem(BaseModel):
    receipt_id: uuid.UUID
    invoice_number: Optional[str]
    status: str
    ready:Optional[bool]
    merchant_name: Optional[str] = None
    payment_method: Optional[str] = None
    total_paid: Optional[float] = None
    purchase_datetime: Optional[str] = None


class InvoiceItemDetail(BaseModel):
    product_id : Optional[uuid.UUID] = None
    product_name: str
    unit_price: float
    quantity: float
    unit: str
    line_total: float
    discount: float
    isDiscount:bool


class InvoiceDetailResponse(BaseModel):
    invoice_number: Optional[str]
    merchant_name: Optional[str] = None
    merchant_address: str
    discount_total: float
    payment_method: str
    total_paid: Optional[float] = None
    purchase_datetime: Optional[str] = None
    items: List[InvoiceItemDetail]

class ReceiptItemUpdateRequest(BaseModel):
    product_id : Optional[uuid.UUID] = None
    receipt_id : uuid.UUID
    product_name: Optional[str] = None
    unit_price: float
    quantity: float
    unit: str
    line_total: float
    discount: Optional[float] = 0


class CategorySummaryResponse(BaseModel):
    category: str
    total_items_in_category: int
    total_amount_spent_in_category: float

class MonthlySpendingResponse(BaseModel):
    month: str
    total_paid_in_month: float
    difference_with_previous_month: float
    discount_in_month: float
