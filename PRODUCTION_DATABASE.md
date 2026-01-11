# Production Database Setup

## Overview

For **production-ready** storage of conversation threads, we use **SQLite** (can be upgraded to PostgreSQL later). The database automatically stores and manages the last 10 conversation threads.

## What's Included

### Database Schema

- **`conversations`** table: Stores conversation metadata
  - `id` (string, primary key)
  - `title` (string)
  - `created_at` (datetime)
  - `updated_at` (datetime)

- **`messages`** table: Stores all messages
  - `id` (string, primary key)
  - `conversation_id` (string, indexed)
  - `role` (string: 'user' or 'assistant')
  - `content` (text)
  - `created_at` (datetime)

### Features

✅ **Automatic cleanup**: Keeps only last 10 conversations  
✅ **Persistent storage**: Survives server restarts  
✅ **API endpoints**: Full CRUD operations  
✅ **Production-ready**: SQLite (can migrate to PostgreSQL)

## Installation

1. **Install dependencies**:
```bash
pip install sqlalchemy aiosqlite
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

2. **Database file**: Created automatically as `hue_conversations.db` in the project root

## API Endpoints

### POST `/api/chat`
Send a message and get AI response. Automatically creates conversation if needed.

**Request**:
```json
{
  "message": "Hello",
  "conversation_id": "conv-123" // optional
}
```

**Response**:
```json
{
  "response": "Hello! How can I help?",
  "conversation_id": "conv-123",
  "message_id": "msg-456"
}
```

### GET `/api/conversations`
Get all conversations (last 10).

**Response**:
```json
[
  {
    "id": "conv-123",
    "title": "Hello",
    "created_at": "2024-01-01T12:00:00",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

### GET `/api/conversations/{conversation_id}/messages`
Get all messages for a conversation.

**Response**:
```json
[
  {
    "id": "msg-1",
    "conversation_id": "conv-123",
    "role": "user",
    "content": "Hello",
    "created_at": "2024-01-01T12:00:00"
  }
]
```

### DELETE `/api/conversations/{conversation_id}`
Delete a conversation and all its messages.

### PUT `/api/conversations/{conversation_id}/title`
Update conversation title.

## Usage

The database is automatically initialized when the API server starts. The Next.js UI uses these endpoints to:
- Load conversations on startup
- Save messages automatically
- Load messages when selecting a conversation
- Create new conversations on first message

## Upgrading to PostgreSQL (Optional)

To use PostgreSQL instead of SQLite for production:

1. **Install PostgreSQL driver**:
```bash
pip install psycopg2-binary
```

2. **Update `database.py`**:
```python
# Change this line:
self.engine = create_engine(f'sqlite:///{db_path}', echo=False)

# To:
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:pass@localhost/hue')
self.engine = create_engine(DATABASE_URL, echo=False)
```

3. **Set environment variable**:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/hue_db"
```

## Backup

To backup the SQLite database:
```bash
cp hue_conversations.db hue_conversations.db.backup
```

Or for PostgreSQL:
```bash
pg_dump -U user hue_db > hue_backup.sql
```

## Notes

- **SQLite is perfect** for single-server deployments
- **PostgreSQL** is better for multi-server/scalable deployments
- Database is created automatically on first run
- Old conversations (beyond 10) are automatically deleted
- All messages are persisted and searchable


