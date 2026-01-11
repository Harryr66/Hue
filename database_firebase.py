#!/usr/bin/env python3
"""
Firebase Firestore database for conversation storage
Production-ready with real-time capabilities
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Optional, Dict
from datetime import datetime
import os
from pathlib import Path

class ConversationDB:
    """Firebase Firestore database manager for conversations"""
    
    def __init__(self, service_account_path: Optional[str] = None):
        self.MAX_CONVERSATIONS = 10
        
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            if service_account_path and os.path.exists(service_account_path):
                # Use service account file
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
            elif os.getenv('FIREBASE_SERVICE_ACCOUNT'):
                # Use service account JSON from environment variable
                import json
                service_account_json = json.loads(os.getenv('FIREBASE_SERVICE_ACCOUNT'))
                cred = credentials.Certificate(service_account_json)
                firebase_admin.initialize_app(cred)
            else:
                # Try default credentials (useful for Firebase Emulator or default app)
                try:
                    firebase_admin.initialize_app()
                except Exception as e:
                    raise ValueError(
                        "Firebase not initialized. Provide FIREBASE_SERVICE_ACCOUNT env var, "
                        "service_account_path, or set GOOGLE_APPLICATION_CREDENTIALS. Error: " + str(e)
                    )
        
        self.db = firestore.client()
        self.conversations_ref = self.db.collection('conversations')
        self.messages_ref = self.db.collection('messages')
    
    def create_conversation(self, conversation_id: str, title: str) -> Dict:
        """Create a new conversation"""
        conversation_data = {
            'id': conversation_id,
            'title': title,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        self.conversations_ref.document(conversation_id).set(conversation_data)
        return conversation_data
    
    def get_conversations(self, limit: Optional[int] = None) -> List[Dict]:
        """Get all conversations, ordered by most recent first"""
        query = self.conversations_ref.order_by('updated_at', direction=firestore.Query.DESCENDING)
        
        if limit:
            query = query.limit(limit)
        
        conversations = []
        for doc in query.stream():
            conv_data = doc.to_dict()
            if conv_data:
                # Convert Firestore timestamps to ISO strings
                if 'created_at' in conv_data and hasattr(conv_data['created_at'], 'isoformat'):
                    conv_data['created_at'] = conv_data['created_at'].isoformat()
                if 'updated_at' in conv_data and hasattr(conv_data['updated_at'], 'isoformat'):
                    conv_data['updated_at'] = conv_data['updated_at'].isoformat()
                conversations.append(conv_data)
        
        return conversations
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a single conversation"""
        doc = self.conversations_ref.document(conversation_id).get()
        if doc.exists:
            conv_data = doc.to_dict()
            if conv_data:
                # Convert Firestore timestamps to ISO strings
                if 'created_at' in conv_data and hasattr(conv_data['created_at'], 'isoformat'):
                    conv_data['created_at'] = conv_data['created_at'].isoformat()
                if 'updated_at' in conv_data and hasattr(conv_data['updated_at'], 'isoformat'):
                    conv_data['updated_at'] = conv_data['updated_at'].isoformat()
            return conv_data
        return None
    
    def update_conversation_title(self, conversation_id: str, title: str):
        """Update conversation title"""
        self.conversations_ref.document(conversation_id).update({
            'title': title,
            'updated_at': datetime.utcnow(),
        })
    
    def delete_conversation(self, conversation_id: str):
        """Delete a conversation and all its messages"""
        # Delete all messages for this conversation
        messages_query = self.messages_ref.where('conversation_id', '==', conversation_id).stream()
        for msg_doc in messages_query:
            msg_doc.reference.delete()
        
        # Delete conversation
        self.conversations_ref.document(conversation_id).delete()
    
    def add_message(self, message_id: str, conversation_id: str, role: str, content: str):
        """Add a message to a conversation"""
        message_data = {
            'id': message_id,
            'conversation_id': conversation_id,
            'role': role,
            'content': content,
            'created_at': datetime.utcnow(),
        }
        self.messages_ref.document(message_id).set(message_data)
        
        # Update conversation's updated_at
        self.conversations_ref.document(conversation_id).update({
            'updated_at': datetime.utcnow(),
        })
    
    def get_messages(self, conversation_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        messages = []
        # Query by conversation_id, then sort in Python (avoids index requirement)
        query = self.messages_ref.where('conversation_id', '==', conversation_id)
        
        for doc in query.stream():
            msg_data = doc.to_dict()
            if msg_data:
                # Convert Firestore timestamps to ISO strings
                if 'created_at' in msg_data and hasattr(msg_data['created_at'], 'isoformat'):
                    msg_data['created_at'] = msg_data['created_at'].isoformat()
                messages.append(msg_data)
        
        # Sort by created_at in Python
        messages.sort(key=lambda x: x.get('created_at', ''))
        return messages
    
    def cleanup_old_conversations(self):
        """Keep only the last MAX_CONVERSATIONS conversations"""
        # Get more than we need to ensure we can delete extras
        all_conversations = self.get_conversations(limit=self.MAX_CONVERSATIONS + 5)
        
        # Keep only the most recent ones
        if len(all_conversations) > self.MAX_CONVERSATIONS:
            to_delete = all_conversations[self.MAX_CONVERSATIONS:]
            for conv in to_delete:
                self.delete_conversation(conv['id'])

