-- PostgreSQL Initialization Script
-- Use this script to create the necessary tables in sequential order.
-- Ensures that tables with foreign keys are created AFTER the parent tables.

-- Enable UUID extension as used by the application
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Create Parent Table: receipts
CREATE TABLE IF NOT EXISTS receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id NUMERIC,
    merchant_name TEXT NOT NULL,
    merchant_chain TEXT NOT NULL,
    branch_name TEXT,
    street TEXT,
    city TEXT,
    country VARCHAR(2) DEFAULT 'LT',
    invoice_number TEXT,
    receipt_number TEXT,
    file_path TEXT,
    purchase_datetime TIMESTAMP,
    currency VARCHAR(3) DEFAULT 'EUR',
    payment_method TEXT,
    gross_subtotal NUMERIC(10, 2),
    discount_total NUMERIC(10, 2) DEFAULT 0,
    net_subtotal NUMERIC(10, 2),
    tax_total NUMERIC(10, 2),
    rounding_adjustment NUMERIC(10, 2) DEFAULT 0,
    total_paid NUMERIC(10, 2),
    status TEXT DEFAULT 'not_processed',
    confidence_score NUMERIC(4, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Child Table: receipt_items
CREATE TABLE IF NOT EXISTS receipt_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL,
    line_number INTEGER,
    product_name TEXT NOT NULL,
    normalized_name TEXT,
    category TEXT,
    quantity NUMERIC(10, 3) NOT NULL,
    unit TEXT NOT NULL,
    unit_price NUMERIC(10, 2),
    line_total NUMERIC(10, 2),
    discount NUMERIC(10, 2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_receipt_items_receipt FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);

-- 3. Create Child Table: receipt_taxes
CREATE TABLE IF NOT EXISTS receipt_taxes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID NOT NULL,
    tax_type TEXT NOT NULL,
    tax_rate_percent NUMERIC(5, 2),
    taxable_amount NUMERIC(10, 2),
    tax_amount NUMERIC(10, 2),
    CONSTRAINT fk_receipt_taxes_receipt FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);

-- 4. Create Child Table: receipt_loyalty
CREATE TABLE IF NOT EXISTS receipt_loyalty (
    receipt_id UUID PRIMARY KEY,
    program_name TEXT,
    card_used BOOLEAN DEFAULT FALSE,
    points_earned INTEGER,
    discount_from_loyalty NUMERIC(10, 2),
    CONSTRAINT fk_receipt_loyalty_receipt FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);

-- 5. Create Child Table: receipt_confidence
CREATE TABLE IF NOT EXISTS receipt_confidence (
    receipt_id UUID PRIMARY KEY,
    overall NUMERIC(4, 2),
    missing_fields TEXT[],
    CONSTRAINT fk_receipt_confidence_receipt FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);

-- 6. Create Child Table: receipt_source
CREATE TABLE IF NOT EXISTS receipt_source (
    receipt_id UUID PRIMARY KEY,
    upload_type TEXT,
    original_filename TEXT,
    processed_by TEXT,
    CONSTRAINT fk_receipt_source_receipt FOREIGN KEY (receipt_id) REFERENCES receipts(id) ON DELETE CASCADE
);
