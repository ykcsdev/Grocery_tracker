from sqlalchemy.orm import Session
from app.models import (
    Receipt, ReceiptItem, ReceiptTax,
    ReceiptLoyalty, ReceiptConfidence, ReceiptSource
)


def save_receipt_to_db(db: Session, receipt: Receipt, data: dict):
    # Merchant
    receipt.merchant_name = data["merchant"]["name"]
    receipt.merchant_chain = data["merchant"]["chain"]
    receipt.branch_name = data["merchant"]["branch_name"]

    addr = data["merchant"]["address"]
    receipt.street = addr["street"]
    receipt.city = addr["city"]
    receipt.country = addr["country"]

    # Metadata
    meta = data["receipt_metadata"]
    receipt.invoice_number = meta["invoice_number"]
    receipt.receipt_number = meta["receipt_number"]
    receipt.purchase_datetime = meta["purchase_datetime"]
    receipt.payment_method = meta["payment_method"]

    # Totals
    totals = data["totals"]
    receipt.gross_subtotal = totals["gross_subtotal"]
    receipt.discount_total = totals["discount_total"]
    receipt.net_subtotal = totals["net_subtotal"]
    receipt.tax_total = totals["tax_total"]
    receipt.rounding_adjustment = totals["rounding_adjustment"]
    receipt.total_paid = totals["total_paid"]

    receipt.confidence_score = data["confidence"]["overall"]
    receipt.status = "processed"

    # Items
    for item in data["items"]:
        db.add(ReceiptItem(
            receipt_id=receipt.id,
            line_number=item["line_number"],
            product_name=item["product_name"],
            normalized_name=item["normalized_name"],
            category=item["category"],
            quantity=item["quantity"],
            unit=item["unit"],
            unit_price=item["unit_price"],
            line_total=item["line_total"],
            discount=item["discount"]
        ))

    # Taxes
    for tax in data["taxes"]:
        db.add(ReceiptTax(
            receipt_id=receipt.id,
            tax_type=tax["tax_type"],
            tax_rate_percent=tax["tax_rate_percent"],
            taxable_amount=tax["taxable_amount"],
            tax_amount=tax["tax_amount"]
        ))

    # Loyalty
    if data["loyalty"]:
        db.add(ReceiptLoyalty(
            receipt_id=receipt.id,
            program_name=data["loyalty"]["program_name"],
            card_used=data["loyalty"]["card_used"],
            points_earned=data["loyalty"]["points_earned"],
            discount_from_loyalty=data["loyalty"]["discount_from_loyalty"]
        ))

    # Confidence
    db.add(ReceiptConfidence(
        receipt_id=receipt.id,
        overall=data["confidence"]["overall"],
        missing_fields=data["confidence"]["missing_fields"]
    ))

    # Source
    db.add(ReceiptSource(
        receipt_id=receipt.id,
        upload_type=data["source"]["upload_type"],
        original_filename=data["source"]["original_filename"],
        processed_by=data["source"]["processed_by"]
    ))
