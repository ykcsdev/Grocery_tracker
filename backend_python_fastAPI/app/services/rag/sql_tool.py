import re
from sqlalchemy import text
from app.database import engine

class SQLTool:
    def __init__(self):
        # We supply the LLM with a stripped down read-only view of the schema
        self.schema = """
        Tables:
        - receipts: id, merchant_name, merchant_chain, purchase_datetime, total_paid, status
        - receipt_items: id, receipt_id, product_name, category, quantity, unit_price, line_total, discount
        """

    def is_safe_query(self, query: str) -> bool:
        """Application level validation enforcing read-only."""
        upper_query = query.upper()
        if not upper_query.strip().startswith("SELECT"):
            return False
        
        dangerous_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "REPLACE", "CREATE", "GRANT", "REVOKE"]
        for keyword in dangerous_keywords:
            if re.search(rf"\b{keyword}\b", upper_query):
                return False
        return True

    def execute_query(self, sql: str) -> str:
        if not self.is_safe_query(sql):
            return "Error: Unsafe execution attempt blocked. Only SELECT queries are permitted."
        
        try:
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.fetchall()
                if not rows:
                    return "No data found."
                
                columns = result.keys()
                res_str = f"Columns: {', '.join(columns)}\nRows:\n"
                for row in rows:
                    res_str += f"- {row}\n"
                return res_str
        except Exception as e:
            return f"Database Error: {str(e)}"
