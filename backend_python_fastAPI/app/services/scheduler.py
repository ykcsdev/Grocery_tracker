import time
from app.database import SessionLocal
from app.models import Receipt
from app.services.receipt_processor import process_receipt_file
from app.services.db_writer import save_receipt_to_db


def receipt_scheduler():
    while True:
        db = SessionLocal()
        try:
            # Fetch the next unprocessed receipt (one at a time)
            receipt = db.query(Receipt).filter(
                Receipt.status == "not_processed"
            ).order_by(Receipt.id).first()

            if receipt is None:
                time.sleep(10)
                continue

            # Mark as in_process
            receipt.status = "in_process"
            db.commit()

            try:
                data = process_receipt_file(receipt.file_path)
                print('Received JSON DATA ->', data)
                save_receipt_to_db(db, receipt, data)
                receipt.status = "processed"
                db.commit()

            except Exception as e:
                receipt.status = "failed"
                db.commit()
                print(f"Processing failed for {receipt.id}: {e}")

        finally:
            db.close()
        time.sleep(1)
