#!/usr/bin/env python3
"""
Database models and operations for conversation storage
Uses SQLite for production-ready conversation memory
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import List, Optional, Dict
import json
from pathlib import Path

Base = declarative_base()

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'role': self.role,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

class ConversationDB:
    """Database manager for conversations"""
    
    def __init__(self, db_path: str = 'hue_conversations.db'):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        self.MAX_CONVERSATIONS = 10
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def create_conversation(self, conversation_id: str, title: str) -> Conversation:
        """Create a new conversation"""
        session = self.get_session()
        try:
            conversation = Conversation(
                id=conversation_id,
                title=title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
        finally:
            session.close()
    
    def get_conversations(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all conversations, ordered by most recent first"""
        session = self.get_session()
        try:
            query = session.query(Conversation).order_by(Conversation.updated_at.desc())
            if limit:
                query = query.limit(limit)
            conversations = query.all()
            return [conv.to_dict() for conv in conversations]
        finally:
            session.close()
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a single conversation"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            return conversation.to_dict() if conversation else None
        finally:
            session.close()
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """Update conversation title"""
        session = self.get_session()
        try:
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation and all its messages"""
        session = self.get_session()
        try:
            # Delete messages first
            session.query(Message).filter_by(conversation_id=conversation_id).delete()
            # Delete conversation
            session.query(Conversation).filter_by(id=conversation_id).delete()
            session.commit()
        finally:
            session.close()
    
    def add_message(self, message_id: str, conversation_id: str, role: str, content: str):
        """Add a message to a conversation"""
        session = self.get_session()
        try:
            message = Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )
            session.add(message)
            # Update conversation's updated_at
            conversation = session.query(Conversation).filter_by(id=conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            session.commit()
        finally:
            session.close()
    
    def get_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        session = self.get_session()
        try:
            messages = session.query(Message).filter_by(
                conversation_id=conversation_id
            ).order_by(Message.created_at.asc()).all()
            return [msg.to_dict() for msg in messages]
        finally:
            session.close()
    
    def cleanup_old_conversations(self):
        """Keep only the last MAX_CONVERSATIONS conversations"""
        session = self.get_session()
        try:
            # Get all conversations ordered by updated_at
            all_conversations = session.query(Conversation).order_by(
                Conversation.updated_at.desc()
            ).all()
            
            # Keep only the most recent ones
            if len(all_conversations) > self.MAX_CONVERSATIONS:
                to_delete = all_conversations[self.MAX_CONVERSATIONS:]
                for conv in to_delete:
                    # Delete messages first
                    session.query(Message).filter_by(conversation_id=conv.id).delete()
                    # Delete conversation
                    session.delete(conv)
                session.commit()
        finally:
            session.close()


