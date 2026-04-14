RECEIPT_PROMPT = """
You are an AI specialized in Lithuanian supermarket receipts
(Maxima, Iki, Rimi, Lidl, Norfa).

Extract the receipt into the provided JSON schema.

Rules:
- Return ONLY valid JSON
- Do NOT include explanations
- Do NOT invent values
- Use null for missing fields
- Preserve Lithuanian product names
- Always store the invoice_number, receipt_number without any symbols,If it is null then add bill date and time in YYYYMMDDHHMMSS with the date of purchase
- The category value should be related to the product (eg., Bakery, Fruits, Vegetables, Bathroom Products, Milk Products, Frozen Food, etc)
- Currency is EUR

JSON Schema:
{
  "receipt_id": "",
  "user_id": "",

  "merchant": {
    "name": "",
    "chain": "",
    "branch_name": null,
    "address": {
      "street": null,
      "city": null,
      "country": "LT"
    }
  },

  "receipt_metadata": {
    "invoice_number": null,
    "receipt_number": null,
    "purchase_datetime": null,
    "currency": "EUR",
    "payment_method": null
  },

  "totals": {
  "gross_subtotal": null,
  "discount_total": 0.0,
  "net_subtotal": null,
  "tax_total": null,
  "rounding_adjustment": 0.0,
  "total_paid": null
},

  "taxes": [
    {
      "tax_type": "PVM",
      "tax_rate_percent": 21,
      "taxable_amount": null,
      "tax_amount": null
    }
  ],

  "items": [
    {
      "line_number": 1,
      "product_name": "",
      "normalized_name": "",
      "quantity": 1,
      "unit": "vnt",
      "unit_price": null,
      "line_total": null,
      "discount": 0.0,
      "category": "",
    }
  ],

  "loyalty": {
    "program_name": null,
    "card_used": false,
    "points_earned": null,
    "discount_from_loyalty": null
  },

  "confidence": {
    "overall": 0.0,
    "missing_fields": []
  },

  "source": {
    "upload_type": "image",
    "original_filename": "",
    "processed_by": "gemini-2.5"
  }
}

"""
