from fastapi import APIRouter, Depends
from sqlalchemy import desc, extract, func
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Receipt, ReceiptItem

import calendar

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_latest_processed_period(db: Session):
    latest_receipt = (
        db.query(Receipt)
        .filter(
            Receipt.status == "processed",
            Receipt.purchase_datetime.isnot(None),
        )
        .order_by(desc(Receipt.purchase_datetime))
        .first()
    )

    if not latest_receipt or not latest_receipt.purchase_datetime:
        return None

    purchase_datetime = latest_receipt.purchase_datetime
    return purchase_datetime.year, purchase_datetime.month


def _filter_receipts_for_period(query, year: int, month: int):
    return query.filter(
        Receipt.status == "processed",
        Receipt.purchase_datetime.isnot(None),
        extract("year", Receipt.purchase_datetime) == year,
        extract("month", Receipt.purchase_datetime) == month,
    )


@router.get("/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    latest_period = _get_latest_processed_period(db)
    if latest_period is None:
        return {
            "summary_month": None,
            "total_monthly_spend": 0.0,
            "average_daily_spend": 0.0,
            "highest_expense_day": None,
            "highest_expense_amount": 0.0,
            "top_category": "N/A",
            "comparison_to_previous_month_pct": None,
        }

    year, month = latest_period

    monthly_spend = (
        _filter_receipts_for_period(
            db.query(func.sum(Receipt.total_paid)),
            year,
            month,
        ).scalar()
        or 0.0
    )

    days_in_month = calendar.monthrange(year, month)[1]
    average_daily_spend = float(monthly_spend) / days_in_month if days_in_month else 0.0

    highest_day = (
        _filter_receipts_for_period(
            db.query(
                func.date(Receipt.purchase_datetime).label("date"),
                func.sum(Receipt.total_paid).label("total"),
            ),
            year,
            month,
        )
        .group_by(func.date(Receipt.purchase_datetime))
        .order_by(desc("total"))
        .first()
    )

    highest_expense_day = None
    highest_expense_amount = 0.0
    if highest_day and highest_day.date:
        highest_expense_day = str(highest_day.date)
        highest_expense_amount = float(highest_day.total or 0.0)

    top_category_row = (
        db.query(
            ReceiptItem.category,
            func.sum(ReceiptItem.line_total).label("total"),
        )
        .join(Receipt)
        .filter(
            Receipt.status == "processed",
            Receipt.purchase_datetime.isnot(None),
            extract("year", Receipt.purchase_datetime) == year,
            extract("month", Receipt.purchase_datetime) == month,
        )
        .group_by(ReceiptItem.category)
        .order_by(desc("total"))
        .first()
    )
    top_category = (
        top_category_row.category
        if top_category_row and top_category_row.category
        else "N/A"
    )

    previous_month = month - 1 or 12
    previous_year = year if month > 1 else year - 1
    previous_month_total = (
        _filter_receipts_for_period(
            db.query(func.sum(Receipt.total_paid)),
            previous_year,
            previous_month,
        ).scalar()
        or 0.0
    )

    comparison_to_previous_month_pct = None
    if previous_month_total:
        comparison_to_previous_month_pct = (
            (float(monthly_spend) - float(previous_month_total)) / float(previous_month_total)
        ) * 100

    return {
        "summary_month": f"{calendar.month_abbr[month]}-{str(year)[-2:]}",
        "total_monthly_spend": float(monthly_spend),
        "average_daily_spend": average_daily_spend,
        "highest_expense_day": highest_expense_day,
        "highest_expense_amount": highest_expense_amount,
        "top_category": top_category,
        "comparison_to_previous_month_pct": comparison_to_previous_month_pct,
    }


@router.get("/monthly-trend")
def get_monthly_trend(db: Session = Depends(get_db)):
    monthly_spends = (
        db.query(
            extract("year", Receipt.purchase_datetime).label("year"),
            extract("month", Receipt.purchase_datetime).label("month"),
            func.sum(Receipt.total_paid).label("total"),
        )
        .filter(
            Receipt.status == "processed",
            Receipt.purchase_datetime.isnot(None),
        )
        .group_by(
            extract("year", Receipt.purchase_datetime),
            extract("month", Receipt.purchase_datetime),
        )
        .order_by(
            extract("year", Receipt.purchase_datetime),
            extract("month", Receipt.purchase_datetime),
        )
        .all()
    )

    result = []
    for monthly_spend in monthly_spends:
        if not monthly_spend.year or not monthly_spend.month:
            continue

        year = int(monthly_spend.year)
        month = int(monthly_spend.month)
        days_in_month = calendar.monthrange(year, month)[1]
        total_amount = float(monthly_spend.total or 0.0)

        result.append(
            {
                "month": f"{calendar.month_abbr[month]}-{str(year)[-2:]}",
                "total_monthly_spend": total_amount,
                "average_daily_spend": total_amount / days_in_month if days_in_month else 0.0,
            }
        )
    return result


@router.get("/money-leaks")
def get_money_leaks(db: Session = Depends(get_db)):
    latest_period = _get_latest_processed_period(db)
    if latest_period is None:
        return []

    year, month = latest_period

    frequent_items = (
        db.query(
            ReceiptItem.product_name,
            func.count(ReceiptItem.id).label("frequency"),
            func.avg(ReceiptItem.unit_price).label("avg_price"),
            func.sum(ReceiptItem.line_total).label("total_spent"),
        )
        .join(Receipt)
        .filter(
            Receipt.status == "processed",
            Receipt.purchase_datetime.isnot(None),
            extract("year", Receipt.purchase_datetime) == year,
            extract("month", Receipt.purchase_datetime) == month,
        )
        .group_by(ReceiptItem.product_name)
        .having(func.count(ReceiptItem.id) >= 3)
        .order_by(desc("frequency"), desc("total_spent"))
        .limit(5)
        .all()
    )

    return [
        {
            "name": item.product_name,
            "frequency": item.frequency,
            "avg_price": float(item.avg_price or 0.0),
            "total_spent": float(item.total_spent or 0.0),
        }
        for item in frequent_items
    ]
