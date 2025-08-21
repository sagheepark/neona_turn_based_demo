# MongoDB Migration Plan

## Overview
This document outlines the migration from file-based storage to MongoDB for the Neona Turn-Based Demo application.

## Current State Analysis

### Existing File-Based Storage
- **Conversations**: Stored in `backend_clean/conversations/` as JSON files
- **Knowledge**: Stored in `backend_clean/knowledge/` as JSON files  
- **Personas**: Stored in `backend_clean/personas/` as JSON files
- **File naming**: `{user_id}.json` or `{character_id}_{user_id}.json`

### Data Structure Analysis
1. **Conversations**: Session-based conversation history with character interactions
2. **Knowledge**: RAG knowledge base with embeddings and context
3. **Personas**: User-defined personality profiles with attributes

## Migration Strategy

### Phase 1: MongoDB Setup & Infrastructure
1. **Install MongoDB locally on macOS**
   ```bash
   # Install via Homebrew (recommended)
   brew tap mongodb/brew
   brew install mongodb-community
   brew services start mongodb-community
   ```

2. **Install Python Dependencies**
   ```bash
   # Using PyMongo Async API (2025 recommended approach - Motor is deprecated)
   pip install pymongo[srv]
   # Alternative: pip install motor[srv]  # If using legacy Motor
   ```

3. **Create MongoDB Configuration**
   - Default database: `neona_chat_db`
   - Collections: `conversations`, `knowledge`, `personas`, `users`
   - Connection string: `mongodb://localhost:27017/neona_chat_db`

### Phase 2: Database Schema Design

#### Collections Structure

```javascript
// conversations collection
{
  _id: ObjectId,
  session_id: "string",
  user_id: "string", 
  character_id: "string",
  messages: [
    {
      role: "user|assistant",
      content: "string",
      timestamp: ISODate,
      emotion?: "string",
      speed?: number
    }
  ],
  persona_context: "string",
  knowledge_used: ["string"],
  created_at: ISODate,
  updated_at: ISODate,
  is_active: boolean
}

// knowledge collection  
{
  _id: ObjectId,
  user_id: "string",
  title: "string",
  content: "string", 
  embedding: [number],
  metadata: {
    source: "string",
    type: "string",
    tags: ["string"]
  },
  created_at: ISODate,
  updated_at: ISODate
}

// personas collection
{
  _id: ObjectId,
  persona_id: "string", // Keep existing UUID format
  user_id: "string",
  name: "string",
  description: "string",
  attributes: {
    age: "string",
    occupation: "string", 
    personality: "string",
    interests: ["string"],
    speaking_style: "string",
    background: "string"
  },
  is_active: boolean,
  created_at: ISODate,
  updated_at: ISODate
}

// users collection (new)
{
  _id: ObjectId,
  user_id: "string",
  active_persona_id: "string",
  settings: {
    voice_enabled: boolean,
    language: "string"
  },
  created_at: ISODate,
  updated_at: ISODate
}
```

### Phase 3: Service Layer Refactoring

#### 1. Database Connection Service
```python
# services/database_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
import os

class DatabaseService:
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_URI", "mongodb://localhost:27017/neona_chat_db")
        self.client = None
        self.db = None
    
    async def connect(self):
        self.client = AsyncIOMotorClient(self.connection_string)
        self.db = self.client.neona_chat_db
        
    async def close(self):
        if self.client:
            self.client.close()
```

#### 2. Update Existing Services

**ConversationService Migration:**
- Replace JSON file operations with MongoDB operations
- Implement session-based conversation storage
- Add indexing for efficient queries

**KnowledgeService Migration:** 
- Store knowledge entries with embeddings in MongoDB
- Implement vector similarity search capabilities
- Maintain RAG functionality with database backing

**PersonaService Migration:**
- Convert file-based persona storage to MongoDB
- Maintain existing persona management features
- Add user-persona relationship management

### Phase 4: Data Migration Script

```python
# scripts/migrate_to_mongodb.py
import asyncio
import json
from pathlib import Path
from services.database_service import DatabaseService

async def migrate_existing_data():
    """Migrate existing JSON files to MongoDB"""
    
    db_service = DatabaseService()
    await db_service.connect()
    
    # Migrate conversations
    await migrate_conversations(db_service)
    
    # Migrate knowledge 
    await migrate_knowledge(db_service)
    
    # Migrate personas
    await migrate_personas(db_service)
    
    await db_service.close()

async def migrate_conversations(db_service):
    conversations_path = Path("backend_clean/conversations")
    if conversations_path.exists():
        for file in conversations_path.glob("*.json"):
            # Load and transform existing conversation data
            # Insert into MongoDB conversations collection
            pass

# Similar functions for knowledge and personas
```

### Phase 5: Testing & Validation

1. **Data Integrity Tests**
   - Verify all existing data migrated correctly
   - Test CRUD operations for all collections
   - Validate relationships between collections

2. **Performance Testing**
   - Compare query performance vs file-based approach
   - Test concurrent access scenarios
   - Monitor memory and CPU usage

3. **Functional Testing**
   - Test all existing API endpoints
   - Verify conversation flows work correctly
   - Test persona management features

## Implementation Steps (Outside Terminal)

### Step 1: MongoDB Installation (User Action Required)
```bash
# Open Terminal and run:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Verify installation
mongosh
# If successful, you'll see the MongoDB shell
```

### Step 2: MongoDB Compass (Optional GUI)
- Download from: https://www.mongodb.com/try/download/compass
- Install and connect to `mongodb://localhost:27017`

### Step 3: Environment Configuration
```bash
# Add to .env file:
MONGODB_URI=mongodb://localhost:27017/neona_chat_db
```

## Risk Assessment & Mitigation

### Risks:
1. **Data Loss**: Migration script failures could corrupt data
2. **Performance**: MongoDB overhead vs simple file operations
3. **Complexity**: Additional infrastructure dependency
4. **Development**: Learning curve for team members

### Mitigation:
1. **Backup Strategy**: Full backup before migration, gradual rollout
2. **Performance Monitoring**: Benchmark before/after, indexing optimization
3. **Documentation**: Comprehensive setup guides, troubleshooting docs
4. **Training**: Team education on MongoDB best practices

## Timeline Estimate

- **Phase 1 (Setup)**: 1-2 days
- **Phase 2 (Schema Design)**: 1 day  
- **Phase 3 (Service Refactoring)**: 3-5 days
- **Phase 4 (Data Migration)**: 2-3 days
- **Phase 5 (Testing)**: 2-3 days

**Total Estimated Time**: 9-14 days

## Success Criteria

- [ ] All existing functionality works with MongoDB backend
- [ ] Data migration completed without loss
- [ ] Performance meets or exceeds file-based approach
- [ ] Easy local development setup
- [ ] Comprehensive test coverage
- [ ] Documentation complete

## Next Steps

1. Get approval for MongoDB installation and setup
2. Install MongoDB locally following Step 1 above
3. Begin implementation of DatabaseService
4. Create migration scripts for existing data
5. Update service layers incrementally
6. Test thoroughly before production deployment

---

*This plan provides a comprehensive roadmap for migrating to MongoDB while maintaining all existing functionality and ensuring data integrity.*