#!/usr/bin/env python3
"""
FastAPI server for WrappedGrok backend
Run with: uvicorn api_server:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env', override=True)

# Add current directory to path so we can import wrapped_grok
sys.path.insert(0, str(Path(__file__).parent))

from wrapped_grok import WrappedGrok

app = FastAPI(title="Hue API Server")

# CORS middleware to allow Next.js to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:9002", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Hue instance
hue_instance: Optional[WrappedGrok] = None

# Initialize database (Firebase or SQLite fallback)
db = None
try:
    # Try Firebase first
    from database_firebase import ConversationDB
    service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH')
    db = ConversationDB(service_account_path=service_account_path)
    print("✅ Using Firebase Firestore")
except Exception as e:
    # Fallback to SQLite
    try:
        from database import ConversationDB as SQLiteDB
        db = SQLiteDB('hue_conversations.db')
        print(f"⚠️  Firebase not configured, using SQLite database")
        print(f"   Error: {str(e)[:100]}")
    except Exception as sqlite_error:
        print(f"❌ Failed to initialize both Firebase and SQLite: {sqlite_error}")
        raise

def get_hue_instance() -> WrappedGrok:
    global hue_instance
    if hue_instance is None:
        grok_api_key = os.getenv('GROK_API_KEY')
        serpapi_key = os.getenv('SERPAPI_KEY')
        elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        
        if not grok_api_key or 'your-grok' in grok_api_key.lower():
            raise ValueError('GROK_API_KEY not set in .env file')
        
        if not serpapi_key or 'your-serpapi' in serpapi_key.lower():
            raise ValueError('SERPAPI_KEY not set in .env file')
        
        hue_instance = WrappedGrok(
            grok_api_key=grok_api_key,
            serpapi_key=serpapi_key,
            silence_timeout=2.0,
            max_response_words=20,
            explain_keyword='explain',
            elevenlabs_api_key=elevenlabs_api_key,
            elevenlabs_voice_id="21m00Tcm4TlvDq8ikWAM",
            use_elevenlabs=elevenlabs_api_key is not None and 'your-elevenlabs' not in elevenlabs_api_key.lower()
        )
    return hue_instance

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    message_id: str

class ConversationModel(BaseModel):
    id: str
    title: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class MessageModel(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: Optional[str] = None

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        import time
        hue = get_hue_instance()
        response_text = hue.process_input(request.message)
        
        # Get or create conversation
        conversation_id = request.conversation_id
        conversation_title = None
        
        if not conversation_id:
            # Create new conversation
            conversation_id = f"conv-{int(time.time() * 1000)}"
            conversation_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
            db.create_conversation(conversation_id, conversation_title)
        else:
            # Verify conversation exists
            existing_conv = db.get_conversation(conversation_id)
            if not existing_conv:
                # Conversation doesn't exist, create it
                conversation_title = request.message[:30] + "..." if len(request.message) > 30 else request.message
                db.create_conversation(conversation_id, conversation_title)
            else:
                conversation_title = existing_conv.get('title')
        
        # Generate message IDs
        timestamp = int(time.time() * 1000)
        user_message_id = request.message_id or f"msg-{timestamp}"
        assistant_message_id = f"msg-{timestamp + 1}"
        
        # Save messages to database
        db.add_message(user_message_id, conversation_id, 'user', request.message)
        db.add_message(assistant_message_id, conversation_id, 'assistant', response_text)
        
        # Cleanup old conversations (keep only last 10)
        db.cleanup_old_conversations()
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            message_id=assistant_message_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations", response_model=List[ConversationModel])
async def get_conversations():
    """Get all conversations (last 10)"""
    try:
        conversations = db.get_conversations(limit=10)
        return [ConversationModel(**conv) for conv in conversations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/conversations/{conversation_id}/messages", response_model=List[MessageModel])
async def get_messages(conversation_id: str):
    """Get all messages for a conversation"""
    try:
        messages = db.get_messages(conversation_id)
        return [MessageModel(**msg) for msg in messages]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        db.delete_conversation(conversation_id)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/conversations/{conversation_id}/title")
async def update_conversation_title(conversation_id: str, title: str):
    """Update conversation title"""
    try:
        db.update_conversation_title(conversation_id, title)
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    print("════════════════════════════════════════")
    print("🚀 Starting Hue API Server")
    print("════════════════════════════════════════")
    print("📍 Server: http://localhost:8000")
    print("📍 Health: http://localhost:8000/health")
    print("📍 API: http://localhost:8000/api/chat")
    print("════════════════════════════════════════")
    print("Press Ctrl+C to stop")
    print("════════════════════════════════════════")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)

