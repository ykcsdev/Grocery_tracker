import bleach
import logging
from .interfaces import LLMProvider
from .vector_db import VectorDB
from .sql_tool import SQLTool

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    def __init__(self, llm_provider: LLMProvider, vector_db: VectorDB, sql_tool: SQLTool):
        self.llm = llm_provider
        self.vector_db = vector_db
        self.sql_tool = sql_tool

    def sanitize_input(self, user_input: str) -> str:
        """Sanitizes user input (Step 6A)"""
        # Limit length to 1000 characters
        if len(user_input) > 1000:
            user_input = user_input[:1000]
            
        # Strip HTML tags
        clean_text = bleach.clean(user_input, tags=[], attributes={}, strip=True)
        # Normalize whitespace
        clean_text = " ".join(clean_text.split())
        return clean_text

    def chat_flow(self, user_query: str) -> str:
        try:
            # Step 1: Input Sanitization
            sanitized_query = self.sanitize_input(user_query)
            
            # Step 2: Query Understanding
            intent = self.llm.classify_intent(sanitized_query)
            logger.info(f"Query Intent Classified: {intent}")
            
            sql_context = ""
            vector_context = ""
            
            # Step 3: SQL Execution
            if intent.get("needs_sql", False):
                sql_query = self.llm.generate_sql(self.sql_tool.schema, sanitized_query)
                logger.info(f"Generated SQL: {sql_query}")
                sql_data = self.sql_tool.execute_query(sql_query)
                sql_context = f"SQL Aggregation Result:\n{sql_data}\n"
                
            # Step 4: Vector Retrieval
            if intent.get("needs_vector", False):
                vector_data = self.vector_db.search(sanitized_query)
                vector_context = f"Relevant Semantic Information:\n{vector_data}\n"
                
            # Step 5: Context Builder
            combined_context = f"{sql_context}\n{vector_context}".strip()
            if not combined_context:
                combined_context = None

            # Step 6: LLM Generation
            sys_prompt = "You are a helpful and intelligent grocery and financial tracking assistant."
            response = self.llm.generate_response(sys_prompt, sanitized_query, context=combined_context)
            
            return response
            
        except Exception as e:
            logger.error(f"Error in chat_flow: {e}")
            return "I'm sorry, I encountered an internal error while processing your request."
