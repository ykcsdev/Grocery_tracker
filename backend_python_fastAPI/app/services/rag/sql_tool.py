import re
from typing import Dict, List, Set

from sqlalchemy import text

from app.database import engine


class SQLTool:
    def __init__(self):
        self.schema = """
        PostgreSQL schema for financial receipt analytics.

        Base tables:
        - receipts:
          id, user_id, merchant_name, merchant_chain, branch_name, street, city, country,
          invoice_number, receipt_number, purchase_datetime, currency, payment_method,
          gross_subtotal, discount_total, net_subtotal, tax_total, rounding_adjustment,
          total_paid, status, confidence_score, created_at, file_path, user_id_numeric
        - receipt_items:
          id, receipt_id, line_number, product_name, normalized_name, category,
          quantity, unit, unit_price, line_total, discount, created_at
        - receipt_confidence:
          receipt_id, overall, missing_fields
        - receipt_loyalty:
          receipt_id, program_name, card_used, points_earned, discount_from_loyalty
        - receipt_source:
          receipt_id, upload_type, original_filename, processed_by
        - receipt_taxes:
          id, receipt_id, tax_type, tax_rate_percent, taxable_amount, tax_amount

        Recommended analytics views:
        - vw_receipt_financials:
          receipt_id, user_id, user_id_numeric, merchant_name, merchant_chain,
          purchase_datetime, currency, payment_method, gross_subtotal, discount_total,
          net_subtotal, receipt_tax_total, computed_tax_total, total_paid,
          tax_lines_count, loyalty_discount
        - vw_monthly_receipt_summary:
          purchase_month, user_id, user_id_numeric, currency, total_receipts,
          gross_subtotal_sum, discount_total_sum, net_subtotal_sum, tax_total_sum,
          total_paid_sum, average_receipt_value
        """
        self.known_columns: Set[str] = {
            "id", "user_id", "merchant_name", "merchant_chain", "branch_name", "street", "city", "country",
            "invoice_number", "receipt_number", "purchase_datetime", "currency", "payment_method",
            "gross_subtotal", "discount_total", "net_subtotal", "tax_total", "rounding_adjustment",
            "total_paid", "status", "confidence_score", "created_at", "file_path", "user_id_numeric",
            "receipt_id", "line_number", "product_name", "normalized_name", "category", "quantity", "unit",
            "unit_price", "line_total", "discount", "overall", "missing_fields", "program_name", "card_used",
            "points_earned", "discount_from_loyalty", "upload_type", "original_filename", "processed_by",
            "tax_type", "tax_rate_percent", "taxable_amount", "tax_amount", "receipt_tax_total",
            "computed_tax_total", "tax_lines_count", "loyalty_discount", "purchase_month", "total_receipts",
            "gross_subtotal_sum", "discount_total_sum", "net_subtotal_sum", "tax_total_sum",
            "total_paid_sum", "average_receipt_value"
        }
        self.domain_keywords: Dict[str, Set[str]] = {
            "receipts": {"receipt", "receipts", "invoice", "invoices", "purchase", "purchases", "merchant", "store", "branch"},
            "items": {"item", "items", "product", "products", "category", "categories", "quantity", "price", "unit"},
            "finance": {"spend", "spent", "spending", "cost", "amount", "total", "subtotal", "discount", "discounts", "tax", "vat", "loyalty", "currency", "payment"},
            "time": {"day", "week", "month", "monthly", "year", "yearly", "trend", "growth", "compare", "comparison", "previous"},
        }
        self.blocked_patterns = [
            r"\b(ignore|bypass|override)\b.{0,40}\b(instruction|system|guardrail|policy)\b",
            r"\b(prompt injection|system prompt|developer message|hidden prompt)\b",
            r"\b(drop|delete|truncate|alter|update|insert|grant|revoke)\b",
            r"\b(api[_ ]?key|token|password|secret)\b",
            r"\b(shell|terminal|powershell|bash|os command)\b",
        ]

    def validate_user_query(self, user_query: str) -> Dict[str, object]:
        normalized = (user_query or "").strip().lower()
        if not normalized:
            return {"allowed": False, "reason": "Empty questions cannot be processed."}

        for pattern in self.blocked_patterns:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                return {
                    "allowed": False,
                    "reason": "This request looks malicious or attempts to bypass backend safety rules.",
                }

        explicit_identifiers = {
            token
            for token in re.findall(r"\b[a-z_][a-z0-9_]{2,}\b", normalized)
            if "_" in token
        }
        unknown_identifiers = sorted(token for token in explicit_identifiers if token not in self.known_columns)
        if unknown_identifiers:
            return {
                "allowed": False,
                "reason": f"Unknown schema fields requested: {', '.join(unknown_identifiers[:6])}.",
            }

        matched_keywords: Set[str] = set()
        for values in self.domain_keywords.values():
            matched_keywords.update(keyword for keyword in values if keyword in normalized)

        mentioned_columns = {column for column in self.known_columns if column in normalized}
        if not matched_keywords and not mentioned_columns:
            return {
                "allowed": False,
                "reason": "The question is outside the supported receipt and financial analytics domain.",
            }

        unsupported_business_terms = {
            "profit", "margin", "revenue", "supplier", "warehouse", "salary", "balance sheet", "forecast"
        }
        unsupported_hits = sorted(term for term in unsupported_business_terms if term in normalized)
        if unsupported_hits and not mentioned_columns:
            return {
                "allowed": False,
                "reason": f"The question references concepts not present in the current schema: {', '.join(unsupported_hits)}.",
            }

        return {
            "allowed": True,
            "reason": "Query maps to the supported financial receipts schema.",
            "matched_columns": sorted(mentioned_columns),
            "matched_keywords": sorted(matched_keywords),
        }

    def is_safe_query(self, query: str) -> bool:
        upper_query = query.upper()
        stripped = upper_query.strip()
        if not (stripped.startswith("SELECT") or stripped.startswith("WITH")):
            return False
        if "--" in query or "/*" in query or "*/" in query:
            return False
        if stripped.count(";") > 1:
            return False

        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "REPLACE", "CREATE", "GRANT", "REVOKE"]
        for keyword in dangerous_keywords:
            if re.search(rf"\b{keyword}\b", upper_query):
                return False
        return True

    def execute_query_with_metadata(self, sql: str) -> dict:
        if not self.is_safe_query(sql):
            return {
                "ok": False,
                "error": "Unsafe execution attempt blocked. Only SELECT queries are permitted.",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "rendered": "Error: Unsafe execution attempt blocked. Only SELECT queries are permitted.",
            }

        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                columns = list(result.keys())
                if not rows:
                    return {
                        "ok": True,
                        "error": None,
                        "columns": columns,
                        "rows": [],
                        "row_count": 0,
                        "rendered": "No data found.",
                    }

                rendered_rows = [dict(zip(columns, row)) for row in rows]
                rendered = f"Columns: {', '.join(columns)}\nRows:\n"
                for row in rendered_rows:
                    rendered += f"- {row}\n"
                return {
                    "ok": True,
                    "error": None,
                    "columns": columns,
                    "rows": rendered_rows,
                    "row_count": len(rendered_rows),
                    "rendered": rendered.strip(),
                }
        except Exception as exc:
            return {
                "ok": False,
                "error": f"Database Error: {str(exc)}",
                "columns": [],
                "rows": [],
                "row_count": 0,
                "rendered": f"Database Error: {str(exc)}",
            }

    def execute_query(self, sql: str) -> str:
        return self.execute_query_with_metadata(sql)["rendered"]

    def validate_financial_rows(self, rows: List[dict]) -> str:
        if not rows:
            return "Validation: no rows available to validate."

        validation_messages = []
        for row in rows[:20]:
            gross = row.get("gross_subtotal")
            discount = row.get("discount_total")
            net = row.get("net_subtotal")
            tax = row.get("receipt_tax_total", row.get("tax_total"))
            total = row.get("total_paid")

            checks = []
            if gross is not None and discount is not None and net is not None:
                expected_net = float(gross) - float(discount)
                checks.append(abs(expected_net - float(net)) <= 0.05)
            if net is not None and tax is not None and total is not None:
                expected_total = float(net) + float(tax)
                checks.append(abs(expected_total - float(total)) <= 0.05)

            if checks and not all(checks):
                receipt_id = row.get("receipt_id", "unknown")
                validation_messages.append(f"Potential mismatch detected for receipt_id={receipt_id}.")

        if not validation_messages:
            return "Validation: sampled financial rows are internally consistent."
        return "Validation: " + " ".join(validation_messages)
