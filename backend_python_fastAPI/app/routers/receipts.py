from fastapi import APIRouter, UploadFile, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from datetime import datetime
from ..models import Receipt,ReceiptItem
from ..schemas import ReceiptUploadResponse, ProcessingStatusResponse, ReceiptItemUpdateRequest,CategorySummaryResponse
from ..utils.file_storage import save_receipt_file

router = APIRouter(prefix="/receipts", tags=["Receipts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload", response_model=ReceiptUploadResponse)
def upload_receipt(file: UploadFile, db: Session = Depends(get_db)):
    file_path = save_receipt_file(file)
    original_filename = file.filename

    receipt = Receipt(
        file_path=file_path,
        status="not_processed",
        merchant_name=original_filename
    )
    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    return ReceiptUploadResponse(
        receipt_id=receipt.id,
        status=receipt.status
    )


@router.get("/{receipt_id}/status", response_model=ProcessingStatusResponse)
def get_processing_status(receipt_id: str, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()

    return ProcessingStatusResponse(
        receipt_id=receipt.id,
        status=receipt.status
    )


@router.put("/updateItems", response_model=dict)
def update_or_add_receipt_item(
    payload: ReceiptItemUpdateRequest,
    db: Session = Depends(get_db),
):
    # Check if the item exists by product_id (receipt_item id)
    if payload.product_id:
        item = db.query(ReceiptItem).filter(ReceiptItem.id == payload.product_id).first()
        if not item:
                raise HTTPException(status_code=404, detail="Receipt item not found")
        item.product_name = payload.product_name
        item.unit_price = payload.unit_price
        item.quantity = payload.quantity
        item.unit = payload.unit
        item.line_total = payload.line_total
        item.discount = payload.discount
        item.created_at = datetime.utcnow()

        db.commit()
        db.refresh(item)

        receipt = db.query(Receipt).filter(Receipt.id == item.receipt_id).first()
        if receipt:
            receipt.update_totals()
            db.commit()
            db.refresh(receipt)

        return {
            "item_id": item.id,
            "message": "Receipt item updated successfully"
        }

    else:
        new_item = ReceiptItem(
            product_name=payload.product_name,
            unit_price=payload.unit_price,
            quantity=payload.quantity,
            unit=payload.unit,
            line_total=payload.line_total,
            discount=payload.discount,
            receipt_id=payload.receipt_id,  
            created_at=datetime.utcnow()
        )

        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        receipt = db.query(Receipt).filter(Receipt.id == new_item.receipt_id).first()
        if receipt:
            receipt.update_totals()
            db.commit()
            db.refresh(receipt)

        return {
            "item_id": new_item.id,
            "message": "New receipt item added successfully"
        }

@router.get("/topItemsByCategory", response_model=list[CategorySummaryResponse])
def get_top_5_items_by_category(db: Session = Depends(get_db)):
    results = db.query(
        ReceiptItem.category,
        func.count(ReceiptItem.id).label("total_items_in_category"),
        func.sum(ReceiptItem.line_total).label("total_amount_spent_in_category")
    ).group_by(ReceiptItem.category).order_by(func.sum(ReceiptItem.line_total).desc()).limit(5).all()

    if not results:
        raise HTTPException(status_code=404, detail="No items found")

    return [
        CategorySummaryResponse(
            category=row.category,
            total_items_in_category=row.total_items_in_category,
            total_amount_spent_in_category=row.total_amount_spent_in_category
        )
        for row in results
    ]