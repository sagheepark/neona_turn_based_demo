# 📚 API Documentation

## Base URL
```
http://localhost:8000
```

---

## 🔐 Session Management

### Start Session
Check for existing sessions or start new one.

**Endpoint:** `POST /api/sessions/start`

**Request:**
```json
{
  "user_id": "user_123",
  "character_id": "dr_python",
  "persona_id": "persona_abc123"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "previous_sessions": [
      {
        "session_id": "sess_20250118_001",
        "message_count": 5,
        "last_message_pair": {
          "user_message": "변수가 뭔가요?",
          "assistant_message": "변수는 데이터를 저장하는..."
        },
        "last_updated": "2025-01-18T10:30:00Z"
      }
    ],
    "can_continue": true,
    "active_persona_id": "persona_abc123",
    "character_id": "dr_python",
    "user_id": "user_123"
  }
}
```

---

### Create New Session
Create a fresh conversation session.

**Endpoint:** `POST /api/sessions/create`

**Request:**
```json
{
  "user_id": "user_123",
  "character_id": "dr_python",
  "persona_id": "persona_abc123"  // optional
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session": {
      "session_id": "sess_20250118_002",
      "user_id": "user_123",
      "character_id": "dr_python",
      "persona_id": "persona_abc123",
      "created_at": "2025-01-18T11:00:00Z",
      "messages": [],
      "message_count": 0
    },
    "persona_context": "사용자는 '초보 개발자' 페르소나로..."
  }
}
```

---

### Continue Session
Resume an existing conversation.

**Endpoint:** `POST /api/sessions/continue`

**Request:**
```json
{
  "session_id": "sess_20250118_001",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session": {
      "session_id": "sess_20250118_001",
      "messages": [
        {
          "id": "msg_001",
          "role": "user",
          "content": "안녕하세요",
          "timestamp": "2025-01-18T10:00:00Z"
        },
        {
          "id": "msg_002",
          "role": "assistant",
          "content": "안녕하세요! 무엇을 도와드릴까요?",
          "timestamp": "2025-01-18T10:00:05Z"
        }
      ],
      "message_count": 2
    },
    "persona_context": "사용자는 '초보 개발자' 페르소나로...",
    "last_qa": {
      "user_message": "변수가 뭔가요?",
      "assistant_message": "변수는 데이터를 저장하는..."
    }
  }
}
```

---

### Process Message
Send a message and get knowledge-augmented response data.

**Endpoint:** `POST /api/sessions/message`

**Request:**
```json
{
  "session_id": "sess_20250118_001",
  "user_id": "user_123",
  "message": "Python 변수가 뭔가요?",
  "character_id": "dr_python"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_message": "Python 변수가 뭔가요?",
    "relevant_knowledge": [
      {
        "id": "py_001",
        "title": "Python 기본 문법 - 변수와 데이터 타입",
        "content": "Python에서는 변수를 선언할 때...",
        "tags": ["변수", "기초문법"]
      }
    ],
    "persona_context": "사용자는 '초보 개발자' 페르소나로...",
    "knowledge_ids": ["py_001"],
    "session_id": "sess_20250118_001"
  }
}
```

**Note:** This endpoint prepares data for AI response generation. You'll need to:
1. Use this data to generate AI response (via existing `/api/chat` endpoint)
2. Save the AI response back using the session_id

---

### Get Sessions
Retrieve all sessions for a user-character pair.

**Endpoint:** `GET /api/sessions/{user_id}/{character_id}`

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "sess_20250118_001",
      "created_at": "2025-01-18T10:00:00Z",
      "last_updated": "2025-01-18T10:30:00Z",
      "message_count": 5,
      "last_message_pair": {
        "user_message": "마지막 질문",
        "assistant_message": "마지막 답변"
      }
    }
  ]
}
```

---

## 👤 Persona Management

### Create Persona
Create a new user persona.

**Endpoint:** `POST /api/personas/create`

**Request:**
```json
{
  "user_id": "user_123",
  "name": "초보 개발자",
  "description": "Python을 처음 배우는 대학생",
  "attributes": {
    "age": "22세",
    "occupation": "대학생",
    "personality": "호기심 많음, 꼼꼼함",
    "interests": ["웹개발", "데이터분석"],
    "speaking_style": "존댓말, 조심스러움",
    "background": "컴퓨터공학과 2학년",
    "current_mood": "학습에 대한 열정"
  }
}
```

**Response:**
```json
{
  "success": true,
  "persona": {
    "id": "persona_abc123",
    "name": "초보 개발자",
    "description": "Python을 처음 배우는 대학생",
    "attributes": { ... },
    "created_at": "2025-01-18T11:00:00Z",
    "is_active": false
  }
}
```

---

### Activate Persona
Set a persona as active for the user.

**Endpoint:** `POST /api/personas/activate`

**Query Parameters:**
- `user_id`: User ID
- `persona_id`: Persona ID to activate

**Example:**
```
POST /api/personas/activate?user_id=user_123&persona_id=persona_abc123
```

**Response:**
```json
{
  "success": true,
  "data": {
    "personas": [...],
    "active_persona_id": "persona_abc123"
  }
}
```

---

### Get Active Persona
Get the currently active persona for a user.

**Endpoint:** `GET /api/personas/{user_id}/active`

**Response:**
```json
{
  "success": true,
  "persona": {
    "id": "persona_abc123",
    "name": "초보 개발자",
    "description": "Python을 처음 배우는 대학생",
    "attributes": { ... },
    "is_active": true
  }
}
```

---

## 🔄 Integration Flow

### Starting a Conversation
```mermaid
1. Call /api/sessions/start
2. If can_continue == true:
   - Show previous sessions to user
   - User selects: Call /api/sessions/continue
   - User starts new: Call /api/sessions/create
3. If can_continue == false:
   - Call /api/sessions/create directly
```

### Processing Messages
```mermaid
1. Call /api/sessions/message with user input
2. Get relevant_knowledge and persona_context
3. Use existing /api/chat with knowledge context
4. Save response back to session (future endpoint)
```

### Persona Management
```mermaid
1. Call /api/personas/create to make new persona
2. Call /api/personas/activate to switch
3. Persona context automatically included in sessions
```

---

## 📝 Examples

### Complete Flow Example
```javascript
// 1. Start session
const startResponse = await fetch('/api/sessions/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 'user_123',
    character_id: 'dr_python'
  })
});

const { data } = await startResponse.json();

// 2. Show previous sessions or create new
let session;
if (data.can_continue && userWantsToContinue) {
  // Continue existing session
  const continueResponse = await fetch('/api/sessions/continue', {
    method: 'POST',
    body: JSON.stringify({
      session_id: data.previous_sessions[0].session_id,
      user_id: 'user_123'
    })
  });
  session = await continueResponse.json();
} else {
  // Create new session
  const createResponse = await fetch('/api/sessions/create', {
    method: 'POST',
    body: JSON.stringify({
      user_id: 'user_123',
      character_id: 'dr_python'
    })
  });
  session = await createResponse.json();
}

// 3. Process user message
const messageResponse = await fetch('/api/sessions/message', {
  method: 'POST',
  body: JSON.stringify({
    session_id: session.data.session.session_id,
    user_id: 'user_123',
    message: 'Python 변수가 뭔가요?',
    character_id: 'dr_python'
  })
});

const messageData = await messageResponse.json();
// Use messageData.data.relevant_knowledge for AI response
```

---

## 🚨 Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid parameters)
- `404`: Not Found (session/persona not found)
- `500`: Internal Server Error

---

## 📌 Important Notes

1. **Session IDs** are unique and include timestamps
2. **Persona IDs** are auto-generated with format `persona_[hash]`
3. **File-based storage** means data persists between server restarts
4. **No authentication** currently implemented (add for production)
5. **Knowledge retrieval** is automatic based on message content

---

*Last Updated: 2025-08-18*