from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc,func,extract
from ..database import SessionLocal
from ..models import Receipt
from datetime import datetime
from ..schemas import InvoiceListItem, InvoiceDetailResponse, InvoiceItemDetail,MonthlySpendingResponse

router = APIRouter(prefix="/invoices", tags=["Invoices"])
from decimal import Decimal

def format_quantity(q: Decimal) -> str:
    if q % 1 == 0:
        return str(q.quantize(Decimal("1")))
    return str(q.normalize())


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/recentExp", response_model=list[InvoiceListItem])
def get_recent_invoices(db: Session = Depends(get_db)):
    receipts = (
        db.query(Receipt)
        .filter(Receipt.status == "processed")
        .order_by(desc(Receipt.purchase_datetime))
        .all()
    )

    return [
        InvoiceListItem(
            receipt_id = r.id,
            merchant_name=r.merchant_name,
            payment_method = r.payment_method,
            total_paid=r.total_paid,
            invoice_number=r.invoice_number,
            purchase_datetime = r.purchase_datetime.strftime("%b %d, %Y").lstrip("0") if r.purchase_datetime else None,
            status=r.status,
            ready=True if r.status=='processed' else False
        )
        for r in receipts
    ]

@router.get("/", response_model=list[InvoiceListItem])
def get_invoices(db: Session = Depends(get_db)):
    receipts = (
        db.query(Receipt)
        # .filter(Receipt.status == "processed")
        .order_by(desc(Receipt.purchase_datetime))
        .all()
    )

    return [
        InvoiceListItem(
            receipt_id = r.id,
            merchant_name=r.merchant_name,
            payment_method = r.payment_method,
            total_paid=r.total_paid,
            invoice_number=r.invoice_number,
            purchase_datetime = r.purchase_datetime.strftime("%b %d, %Y").lstrip("0") if r.purchase_datetime else None,
            status=r.status,
            ready=True if r.status=='processed' else False
        )
        for r in receipts
    ]


@router.get("/receipts/{receipt_id}", response_model=InvoiceDetailResponse)
def get_invoice_detail(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(
        Receipt.id == receipt_id
    ).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    sorted_items = sorted(receipt.items, key=lambda i: i.product_name)

    items = [
        InvoiceItemDetail(
            product_id=i.id,
            product_name=i.product_name,
            unit_price=i.unit_price,
            quantity=(
            int(i.quantity)
            if i.quantity == i.quantity.to_integral_value()
            else round(i.quantity, 3)),
            unit= i.unit,
            line_total=i.line_total,
            discount=i.discount,
            isDiscount=True if i.discount>0.0 else False
        )
        for i in sorted_items
    ]

    return InvoiceDetailResponse(
        invoice_number=receipt.invoice_number,
        merchant_name=receipt.merchant_name,
        merchant_address=f'{receipt.street}, {receipt.city}',
        payment_method = receipt.payment_method,
        total_paid=receipt.total_paid,
        discount_total = receipt.discount_total,
        purchase_datetime = receipt.purchase_datetime.strftime("%B %d, %Y %H:%M")if receipt.purchase_datetime else None,
        items=items
    )

@router.get("/monthlySpending", response_model=list[MonthlySpendingResponse])
def get_monthly_spending(db: Session = Depends(get_db)):
    # Get the current date to fallback on
    current_date = datetime.utcnow()

    # Query the database to get total_paid and discount_total by month and year
    monthly_data = db.query(
        func.extract('year', Receipt.purchase_datetime).label('year'),
        func.extract('month', Receipt.purchase_datetime).label('month'),
        func.sum(Receipt.total_paid).label('total_paid_in_month'),
        func.sum(Receipt.discount_total).label('discount_in_month')
    ).group_by(
        func.extract('year', Receipt.purchase_datetime),
        func.extract('month', Receipt.purchase_datetime)
    ).order_by(
        func.extract('year', Receipt.purchase_datetime).desc(),
        func.extract('month', Receipt.purchase_datetime).desc()
    ).all()

    result = []
    previous_month_total = 0

    for data in monthly_data:
        # Handle case where year or month is None
        if data.year is None or data.month is None:
            continue

        # Default to current date values if year or month are None
        year = int(data.year) if data.year is not None else current_date.year
        month = int(data.month) if data.month is not None else current_date.month
        
        # Safely handle None for total_paid and discount_total
        total_paid = data.total_paid_in_month if data.total_paid_in_month is not None else 0
        discount_total = data.discount_in_month if data.discount_in_month is not None else 0
        
        # Get the month name using the year and month (validating month range)
        try:
            month_name = datetime(year, month, 1).strftime('%B')
        except ValueError:
            continue
        
        # Calculate the difference with the previous month in percentage
        if previous_month_total == 0:
            difference = 0  # No previous month, so no difference, logic breaks if there is something exists
        else:
            difference = ((total_paid - previous_month_total) / previous_month_total) * 100
        
        # Prepare the result list
        result.append({
            "month": month_name,
            "total_paid_in_month": total_paid,
            "difference_with_previous_month": round(difference, 2),
            "discount_in_month": discount_total
        })
        
        # Update the previous month total for the next iteration
        previous_month_total = total_paid

    return result