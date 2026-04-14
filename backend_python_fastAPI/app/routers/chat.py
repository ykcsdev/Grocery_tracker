from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag.gemini_provider import GeminiProvider
from app.services.rag.vector_db import VectorDB
from app.services.rag.sql_tool import SQLTool
from app.services.rag.llm_orchestrator import LLMOrchestrator

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
def chat_with_ai(request: ChatRequest):
    # The orchestrator handles sanitization, intents, contexts, and generation.
    response = orchestrator.chat_flow(request.message)
    return {"reply": response}
