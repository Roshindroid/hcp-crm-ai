import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agent import app as graph_app
from db import init_db, save_interaction, list_interactions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


class ChatRequest(BaseModel):
    message: str
    current: Optional[Dict[str, Any]] = None


@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/chat")
def chat(request: ChatRequest):
    initial_state: Dict[str, Any] = {"input": request.message}
    if request.current:
        # Seed the graph with whatever is currently on the form so that
        # the "edit" tool only changes the fields the user mentions.
        for key in (
            "hcp_name", "date", "interaction_type", "attendees",
            "topics", "sentiment", "materials_shared",
        ):
            if request.current.get(key) not in (None, "", False):
                initial_state[key] = request.current[key]
        if request.current.get("materials_shared") is True:
            initial_state["materials_shared"] = True

    result = graph_app.invoke(initial_state)

    saved_id = None
    if result.get("validation", {}).get("is_valid"):
        try:
            saved_id = save_interaction(result)
        except Exception as e:
            print(f"DB save failed: {e}")

    return {
        "hcp_name": result.get("hcp_name"),
        "date": result.get("date"),
        "interaction_type": result.get("interaction_type"),
        "attendees": result.get("attendees"),
        "topics": result.get("topics"),
        "sentiment": result.get("sentiment"),
        "materials_shared": result.get("materials_shared"),
        "summary": result.get("summary"),
        "validation": result.get("validation"),
        "saved_id": saved_id,
    }


@app.get("/interactions")
def get_interactions(limit: int = 50):
    return {"interactions": list_interactions(limit=limit)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
