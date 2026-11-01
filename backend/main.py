import os
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sarvamai import SarvamAI

# Try loading .env from current directory or parent directory
for env_candidate in [Path(".env"), Path(__file__).parent / ".env", Path(__file__).parent.parent / ".env"]:
    if env_candidate.is_file():
        with open(env_candidate, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v

app = FastAPI(
    title="Sarvam AI Backend",
    description="Backend API powered by Sarvam AI for chat and Indic language generation",
    version="1.0.0",
)

# Enable CORS for frontend deployment (Vercel, localhost, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_sarvam_client() -> SarvamAI:
    api_key = os.environ.get("SARVAM_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="SARVAM_API_KEY is not configured in the environment.",
        )
    return SarvamAI(api_subscription_key=api_key)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    model: Optional[str] = "sarvam-105b-conversations"

class ChatResponse(BaseModel):
    reply: str
    model: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Sarvam AI Backend",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "docs": "/docs",
        },
    }

@app.get("/api/health")
def health_check():
    has_key = bool(os.environ.get("SARVAM_API_KEY"))
    return {
        "status": "healthy",
        "sarvam_configured": has_key,
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat_completion(request: ChatRequest):
    client = get_sarvam_client()
    messages = []

    # Include prior history if provided
    if request.history:
        for msg in request.history:
            messages.append({"role": msg.role, "content": msg.content})

    # Append current message
    messages.append({"role": "user", "content": request.message})

    try:
        response = client.chat.completions(
            model=request.model or "sarvam-105b-conversations",
            messages=messages,
        )
        reply = response.choices[0].message.content
        return ChatResponse(reply=reply, model=request.model or "sarvam-105b-conversations")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

