import logging
import re

import bleach

from ..gemini_client import is_gemini_transient_error
from .interfaces import LLMProvider
from .sql_tool import SQLTool
from .vector_db import VectorDB

logger = logging.getLogger(__name__)


class LLMOrchestrator:
    def __init__(self, llm_provider: LLMProvider, vector_db: VectorDB, sql_tool: SQLTool):
        self.llm = llm_provider
        self.vector_db = vector_db
        self.sql_tool = sql_tool

    def sanitize_input(self, user_input: str) -> str:
        if len(user_input) > 1000:
            user_input = user_input[:1000]

        clean_text = bleach.clean(user_input, tags=[], attributes={}, strip=True)
        return " ".join(clean_text.split())

    def mask_sensitive_context(self, value: str) -> str:
        masked = re.sub(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
            "[uuid]",
            value,
            flags=re.IGNORECASE,
        )
        masked = re.sub(
            r"(?i)(invoice_number|receipt_number|file_path|user_id)\s*[:=]\s*['\"]?[^,'\"\n]+",
            r"\1=[masked]",
            masked,
        )
        return masked

    def _build_memory_metadata(self, user_query: str, sql_query: str, row_count: int) -> dict:
        return {
            "source_type": "financial_insight",
            "user_query": self.mask_sensitive_context(user_query)[:500],
            "sql_query": sql_query[:1000],
            "row_count": row_count,
        }

    def normalize_response(self, response: str) -> str:
        normalized = (response or "").replace("\r\n", "\n").replace("\u2014", "-")
        normalized = normalized.replace("**", "")

        cleaned_lines = []
        for raw_line in normalized.split("\n"):
            line = raw_line.strip()
            if not line:
                continue
            line = re.sub(r"^\*\s*", "- ", line)
            line = re.sub(r"^-\s*\*\s*", "- ", line)
            line = re.sub(r"\$\s*(\d+(?:\.\d+)?)", r"EUR \1", line)
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    def chat_flow(self, user_query: str) -> str:
        try:
            sanitized_query = self.sanitize_input(user_query)
            guardrail = self.sql_tool.validate_user_query(sanitized_query)
            if not guardrail["allowed"]:
                logger.warning(f"Rejected query before LLM processing: {guardrail['reason']}")
                return (
                    "I can only answer receipt and spending questions that map to the current database schema. "
                    f"Request rejected: {guardrail['reason']}"
                )

            plan = self.llm.plan_query(self.sql_tool.schema, sanitized_query)
            logger.info(f"Execution Plan: {plan}")

            sql_context = ""
            vector_context = ""
            validation_context = ""

            if plan.get("needs_sql", False):
                sql_query = self.llm.generate_sql(self.sql_tool.schema, sanitized_query)
                logger.info(f"Generated SQL: {sql_query}")
                sql_result = self.sql_tool.execute_query_with_metadata(sql_query)
                masked_sql_data = self.mask_sensitive_context(sql_result["rendered"])
                sql_context = f"SQL Aggregation Result:\n{masked_sql_data}\n"

                if plan.get("requires_financial_validation", False):
                    validation_context = self.sql_tool.validate_financial_rows(sql_result["rows"])

                if sql_result["ok"] and plan.get("should_store_memory", False) and sql_result["row_count"] > 0:
                    insight_payload = self.llm.summarize_sql_result(
                        sanitized_query,
                        sql_query,
                        masked_sql_data,
                    )
                    insights = insight_payload.get("insights", [])
                    summary = insight_payload.get("summary")
                    if summary:
                        insights = [summary, *insights]
                    stored_count = self.vector_db.store_financial_insights(
                        insights=insights[:5],
                        metadata=self._build_memory_metadata(sanitized_query, sql_query, sql_result["row_count"]),
                    )
                    logger.info(f"Stored {stored_count} financial insights in ChromaDB.")

            if plan.get("needs_vector", False):
                vector_data = self.vector_db.search(sanitized_query, n_results=int(plan.get("vector_k", 5)))
                vector_context = f"Relevant Semantic Information:\n{vector_data}\n"

            combined_context = "\n".join(
                part
                for part in [
                    f"Plan Steps: {', '.join(plan.get('analysis_steps', []))}" if plan.get("analysis_steps") else "",
                    sql_context,
                    validation_context,
                    vector_context,
                ]
                if part
            ).strip()
            if not combined_context:
                return (
                    "The request is within scope, but I could not build enough grounded context from the database "
                    "or memory store to answer safely."
                )

            response = self.llm.generate_response(
                (
                    "You are a helpful grocery and financial tracking assistant. "
                    "Use SQL results as the source of truth for exact numbers. "
                    "Use semantic memory only as supporting context. "
                    "If the data is missing or incomplete, say so clearly. "
                    "Write in plain, concise English. "
                    "Do not use emojis. "
                    "Do not use em dashes. "
                    "Do not use markdown emphasis such as **bold**. "
                    "Use short paragraphs or simple hyphen bullets only when listing values. "
                    "Respect the currency in the SQL data. If the data is in EUR or euro, never use the dollar symbol."
                ),
                sanitized_query,
                context=combined_context,
            )
            return self.normalize_response(response)

        except Exception as exc:
            logger.error(f"Error in chat_flow: {exc}")
            if is_gemini_transient_error(exc):
                return (
                    "Our AI accountants are buried in receipts right now. "
                    "Please try again in a little bit."
                )
            return "I'm sorry, I encountered an internal error while processing your request."
