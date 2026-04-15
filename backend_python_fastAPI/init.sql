-- Enable UUID generation used by gen_random_uuid().
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS public.receipts (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	user_id uuid NULL,
	merchant_name text NULL,
	merchant_chain text NULL,
	branch_name text NULL,
	street text NULL,
	city text NULL,
	country bpchar(2) DEFAULT 'LT'::bpchar NULL,
	invoice_number text NULL,
	receipt_number text NULL,
	purchase_datetime timestamp NULL,
	currency bpchar(3) DEFAULT 'EUR'::bpchar NULL,
	payment_method text NULL,
	gross_subtotal numeric(10, 2) NULL,
	discount_total numeric(10, 2) DEFAULT 0 NULL,
	net_subtotal numeric(10, 2) NULL,
	tax_total numeric(10, 2) NULL,
	rounding_adjustment numeric(10, 2) DEFAULT 0 NULL,
	total_paid numeric(10, 2) NULL,
	status text DEFAULT 'not_processed'::text NULL,
	confidence_score numeric(4, 2) NULL,
	created_at timestamp DEFAULT now() NULL,
	file_path text NOT NULL,
	user_id_numeric int8 NULL,
	CONSTRAINT receipts_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_receipts_chain ON public.receipts USING btree (merchant_chain);
CREATE INDEX idx_receipts_purchase_time ON public.receipts USING btree (purchase_datetime DESC);
CREATE INDEX idx_receipts_status ON public.receipts USING btree (status);
CREATE INDEX idx_receipts_user ON public.receipts USING btree (user_id);



CREATE TABLE IF NOT EXISTS public.receipt_items (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	receipt_id uuid NOT NULL,
	line_number int4 NULL,
	product_name text NOT NULL,
	normalized_name text NULL,
	category text NULL,
	quantity numeric(10, 3) NOT NULL,
	unit text NOT NULL,
	unit_price numeric(10, 2) NULL,
	line_total numeric(10, 2) NULL,
	discount numeric(10, 2) DEFAULT 0 NULL,
	created_at timestamp DEFAULT now() NULL,
	CONSTRAINT receipt_items_pkey PRIMARY KEY (id),
	CONSTRAINT receipt_items_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(id) ON DELETE CASCADE
);
CREATE INDEX idx_items_category ON public.receipt_items USING btree (category);
CREATE INDEX idx_items_normalized ON public.receipt_items USING btree (normalized_name);
CREATE INDEX idx_items_product ON public.receipt_items USING btree (product_name);
CREATE INDEX idx_items_receipt ON public.receipt_items USING btree (receipt_id);

CREATE TABLE IF NOT EXISTS public.receipt_confidence (
	receipt_id uuid NOT NULL,
	overall numeric(4, 2) NULL,
	missing_fields _text NULL,
	CONSTRAINT receipt_confidence_pkey PRIMARY KEY (receipt_id),
	CONSTRAINT receipt_confidence_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(id) ON DELETE CASCADE
);



CREATE TABLE IF NOT EXISTS public.receipt_loyalty (
	receipt_id uuid NOT NULL,
	program_name text NULL,
	card_used bool DEFAULT false NULL,
	points_earned int4 NULL,
	discount_from_loyalty numeric(10, 2) NULL,
	CONSTRAINT receipt_loyalty_pkey PRIMARY KEY (receipt_id),
	CONSTRAINT receipt_loyalty_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS public.receipt_source (
	receipt_id uuid NOT NULL,
	upload_type text NULL,
	original_filename text NULL,
	processed_by text NULL,
	CONSTRAINT receipt_source_pkey PRIMARY KEY (receipt_id),
	CONSTRAINT receipt_source_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS public.receipt_taxes (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	receipt_id uuid NOT NULL,
	tax_type text NOT NULL,
	tax_rate_percent numeric(5, 2) NULL,
	taxable_amount numeric(10, 2) NULL,
	tax_amount numeric(10, 2) NULL,
	CONSTRAINT receipt_taxes_pkey PRIMARY KEY (id),
	CONSTRAINT receipt_taxes_receipt_id_fkey FOREIGN KEY (receipt_id) REFERENCES public.receipts(id) ON DELETE CASCADE
);
