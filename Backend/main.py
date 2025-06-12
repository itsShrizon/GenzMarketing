from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import io
import json
from crew import crew_workflow
from speech_openai import record_audio_from_file, transcribe_audio_with_openai
from avatar_utils import create_avatar_video

app = FastAPI(title="GenZ Marketing Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    status: str

class AvatarRequest(BaseModel):
    text: str

class AvatarResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None

# Store chat history (in production, use a database)
chat_history = []

@app.get("/")
async def root():
    return {"message": "GenZ Marketing Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat message and return the AI response
    """
    try:
        # Add user message to history
        chat_history.append({"role": "user", "content": request.message})
        
        # Process the query using the crew workflow
        result = crew_workflow(request.message)
        
        if result.get("status") == "success":
            response_text = result["response"]
            sources = result.get("sources", [])
            
            # Add AI response to history
            chat_history.append({"role": "assistant", "content": response_text})
            
            return ChatResponse(
                response=response_text,
                sources=sources,
                status="success"
            )
        else:
            error_message = f"Error: {result.get('error', 'Unknown error')}"
            chat_history.append({"role": "assistant", "content": error_message})
            
            return ChatResponse(
                response=error_message,
                sources=[],
                status="error"
            )
            
    except Exception as e:
        error_message = f"Internal server error: {str(e)}"
        return ChatResponse(
            response=error_message,
            sources=[],
            status="error"
        )

@app.get("/chat/history")
async def get_chat_history():
    """
    Get the chat history
    """
    return {"history": chat_history}

@app.delete("/chat/history")
async def clear_chat_history():
    """
    Clear the chat history
    """
    global chat_history
    chat_history = []
    return {"message": "Chat history cleared"}

@app.post("/speech-to-text")
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    Convert speech to text using OpenAI Whisper
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process audio and save to temp file
        audio_path = record_audio_from_file(audio_data)
        if not audio_path:
            raise HTTPException(status_code=400, detail="Failed to process audio file")
        
        # Transcribe audio
        transcript = transcribe_audio_with_openai()
        
        if transcript and transcript != "Transcription failed." and not transcript.startswith("Error:"):
            return {"transcript": transcript, "status": "success"}
        else:
            raise HTTPException(status_code=400, detail=f"Transcription failed: {transcript}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@app.post("/create-avatar", response_model=AvatarResponse)
async def create_avatar(request: AvatarRequest):
    """
    Create an avatar video from text
    """
    try:
        result = create_avatar_video(request.text)
        
        if result["status"] == "success":
            return AvatarResponse(
                status="success",
                video_url=result["video_url"]
            )
        elif result["status"] == "processing":
            return AvatarResponse(
                status="processing",
                error=result["error"]
            )
        else:
            return AvatarResponse(
                status="error",
                error=result["error"]
            )
            
    except Exception as e:
        return AvatarResponse(
            status="error",
            error=f"Internal server error: {str(e)}"
        )

@app.get("/avatar-video/{video_url:path}")
async def get_avatar_video(video_url: str):
    """
    Stream avatar video content
    """
    try:
        import requests
        response = requests.get(video_url)
        if response.status_code == 200:
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type="video/mp4",
                headers={"Content-Disposition": "inline; filename=avatar.mp4"}
            )
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error streaming video: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
