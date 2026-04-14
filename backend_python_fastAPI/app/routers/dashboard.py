from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract
from ..database import SessionLocal
from ..models import Receipt, ReceiptItem
from datetime import datetime
import calendar

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 1. Total monthly spend (Current month)
    current_date = datetime.utcnow()
    year = current_date.year
    month = current_date.month

    monthly_spend = db.query(func.sum(Receipt.total_paid)).filter(
        extract('year', Receipt.purchase_datetime) == year,
        extract('month', Receipt.purchase_datetime) == month,
        Receipt.status == 'processed'
    ).scalar() or 0.0

    # 2. Average daily spend
    days_in_month = calendar.monthrange(year, month)[1]
    average_daily_spend = float(monthly_spend) / days_in_month

    # 3. Highest expense day (in the current month)
    daily_spends = db.query(
        func.date(Receipt.purchase_datetime).label('date'),
        func.sum(Receipt.total_paid).label('total')
    ).filter(
        extract('year', Receipt.purchase_datetime) == year,
        extract('month', Receipt.purchase_datetime) == month,
        Receipt.status == 'processed'
    ).group_by(func.date(Receipt.purchase_datetime)).all()

    highest_expense_day = None
    highest_expense_amount = 0.0
    if daily_spends:
        highest = max(daily_spends, key=lambda x: x.total)
        highest_expense_day = highest.date.strftime("%Y-%m-%d") if highest.date else None
        highest_expense_amount = float(highest.total)

    # 4. Top category (overall or monthly, let's do monthly)
    top_cat = db.query(
        ReceiptItem.category,
        func.sum(ReceiptItem.line_total).label('total')
    ).join(Receipt).filter(
        extract('year', Receipt.purchase_datetime) == year,
        extract('month', Receipt.purchase_datetime) == month
    ).group_by(ReceiptItem.category).order_by(desc('total')).first()

    top_category = top_cat.category if top_cat and top_cat.category else "N/A"

    return {
        "total_monthly_spend": float(monthly_spend),
        "average_daily_spend": average_daily_spend,
        "highest_expense_day": highest_expense_day,
        "highest_expense_amount": highest_expense_amount,
        "top_category": top_category
    }

@router.get("/daily-spending")
def get_daily_spending(db: Session = Depends(get_db)):
    current_date = datetime.utcnow()
    year = current_date.year
    month = current_date.month

    daily_spends = db.query(
        func.date(Receipt.purchase_datetime).label('date'),
        func.sum(Receipt.total_paid).label('total')
    ).filter(
        extract('year', Receipt.purchase_datetime) == year,
        extract('month', Receipt.purchase_datetime) == month,
        Receipt.status == 'processed'
    ).group_by(func.date(Receipt.purchase_datetime)).order_by(func.date(Receipt.purchase_datetime)).all()

    result = []
    for spend in daily_spends:
        if spend.date:
            result.append({
                "date": spend.date.strftime("%b %d"),
                "amount": float(spend.total)
            })
    return result

@router.get("/money-leaks")
def get_money_leaks(db: Session = Depends(get_db)):
    # Find items bought frequently (e.g., count >= 3 in a month)
    current_date = datetime.utcnow()
    year = current_date.year
    month = current_date.month

    frequent_items = db.query(
        ReceiptItem.product_name,
        func.count(ReceiptItem.id).label('frequency'),
        func.avg(ReceiptItem.unit_price).label('avg_price'),
        func.sum(ReceiptItem.line_total).label('total_spent')
    ).join(Receipt).filter(
        extract('year', Receipt.purchase_datetime) == year,
        extract('month', Receipt.purchase_datetime) == month
    ).group_by(ReceiptItem.product_name).having(func.count(ReceiptItem.id) >= 3).order_by(desc('frequency')).limit(5).all()

    leaks = []
    for item in frequent_items:
        leaks.append({
            "name": item.product_name,
            "frequency": item.frequency,
            "avg_price": float(item.avg_price or 0.0),
            "total_spent": float(item.total_spent or 0.0)
        })
    return leaks
