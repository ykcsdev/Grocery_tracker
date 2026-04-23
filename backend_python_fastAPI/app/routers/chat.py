from fastapi import APIRouter, Request
from pydantic import BaseModel
from app.services.rag.gemini_provider import GeminiProvider
from app.services.rag.vector_db import VectorDB
from app.services.rag.sql_tool import SQLTool
from app.services.rag.llm_orchestrator import LLMOrchestrator
from app.limiter import limiter

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

# Initialize the RAG dependencies
# Designing this loosely coupled allows us to easily replace `GeminiProvider`
# with `ClaudeProvider` or `OllamaProvider` later.
llm_provider = GeminiProvider()
vector_db = VectorDB(embedding_provider=llm_provider)
sql_tool = SQLTool()

orchestrator = LLMOrchestrator(
    llm_provider=llm_provider,
    vector_db=vector_db,
    sql_tool=sql_tool
)

@router.post("/")
@limiter.limit("15/minute")
def chat_with_ai(request: Request, payload: ChatRequest):
    # The orchestrator handles sanitization, intents, contexts, and generation.
    response = orchestrator.chat_flow(payload.message)
    return {"reply": response}
