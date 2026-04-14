import os
from uuid import uuid4

UPLOAD_DIR = "uploads/receipts"


def save_receipt_file(file):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid4()}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path
