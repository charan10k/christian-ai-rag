from fastapi import APIRouter
from pydantic import BaseModel

# NOTE: This loads the chat router.
from app.safety.moderation import moderate_prompt
from app.safety.fake_verse_detector import validate_reference
from app.rag.retriever import retrieve_scriptures
from app.llm.generator import generate_response
from app.memory.session_memory import memory_store

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


class ChatRequest(BaseModel):
    session_id: str
    question: str
    denomination: str = "Protestant"


@router.post("/")
def chat(request: ChatRequest):

    moderation = moderate_prompt(request.question)

    if moderation["blocked"]:
        return {
            "success": False,
            "message": moderation["message"]
        }

    fake_verse = validate_reference(request.question)

    if fake_verse:
        return {
            "success": False,
            "message": fake_verse
        }

    retrieved_verses = retrieve_scriptures(request.question)

    history = memory_store.get(request.session_id, [])

    response = generate_response(
        question=request.question,
        verses=retrieved_verses,
        denomination=request.denomination,
        history=history
    )

    history.append({
        "question": request.question,
        "response": response
    })

    memory_store[request.session_id] = history[-5:]

    return {
        "success": True,
        "response": response,
        "citations": [
            verse["citation"] for verse in retrieved_verses
        ]
    }