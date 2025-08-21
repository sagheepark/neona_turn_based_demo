# Development Plans - Voice Character Chat

## 📅 Current Status & Priorities
*Last Updated: 2025-01-18*

## 🎯 Immediate Priority: Knowledge Base System (Phase 2)

### Implementation Approach: JSON-Based (No External DB)
We can implement the Knowledge Base system **without any external database** using:
- **JSON files** for knowledge storage
- **LocalStorage** for client-side caching
- **File system** for backend storage
- **In-memory search** for knowledge retrieval

This approach is perfect for prototyping and can handle 100s of knowledge items per character easily.

---

## 📋 Development Timeline

### 🚀 NOW: Knowledge Base System
**Timeline**: Start immediately  
**Duration**: 4-5 hours  
**Database Required**: NO ✅

#### Implementation Plan:
1. **Backend Structure** (1 hour)
   ```
   backend_clean/
   ├── knowledge/
   │   ├── yoon_ahri/
   │   │   └── knowledge.json
   │   ├── taepung/
   │   │   └── knowledge.json
   │   └── park_hyun/
   │       └── knowledge.json
   ```

2. **Knowledge JSON Schema**
   ```json
   {
     "character_id": "yoon_ahri",
     "knowledge_items": [
       {
         "id": "k001",
         "type": "text",
         "title": "ASMR 기법",
         "content": "귓속말, 탭핑, 브러싱 등의 ASMR 트리거...",
         "tags": ["ASMR", "릴렉스", "수면"],
         "trigger_keywords": ["잠", "스트레스", "긴장", "피곤"],
         "priority": 1
       },
       {
         "id": "k002",
         "type": "link",
         "title": "추천 명상 음악",
         "content": "https://youtube.com/...",
         "description": "수면에 도움되는 음악 플레이리스트",
         "tags": ["음악", "명상"],
         "trigger_keywords": ["음악", "명상", "릴렉스"]
       }
     ]
   }
   ```

3. **Frontend Components** (2 hours)
   - Knowledge manager UI at `/characters/[id]/knowledge`
   - Add/Edit/Delete knowledge items
   - Tag management
   - Keyword configuration

4. **Search & Retrieval** (1 hour)
   - Keyword matching algorithm
   - Context-aware knowledge injection
   - Relevance scoring

5. **Chat Integration** (1 hour)
   - Auto-detect relevant knowledge from user message
   - Include in AI prompt context
   - Visual indicator when knowledge is used

#### Why This Works Without DB:
- **JSON files** are perfect for <1000 items per character
- **Fast enough** for prototype (millisecond search times)
- **Easy backup** - just copy JSON files
- **Version control friendly** - track changes in git
- **No setup required** - works immediately

---

### 📝 LATER (Priority Order)

#### 1. Character Creation/Edit Pages
**Timeline**: After Knowledge Base  
**Duration**: 3-4 hours  
**Why Later**: Knowledge Base is more unique/differentiating feature

**Tasks**:
- Character creation form with all fields
- Image upload/preview
- Voice selector integration
- Personality builder UI

#### 2. Production Backend Setup
**Timeline**: After Character CRUD  
**Duration**: 2-3 hours  
**Why Later**: Current backend_clean works fine for prototype

**Tasks**:
- Migrate to `/backend` folder
- Proper FastAPI structure
- Environment configuration
- API documentation

#### 3. Fix Voice Recommendation Mapping
**Timeline**: After main features complete  
**Duration**: 2-3 hours  
**Why Later**: Not blocking other features, partial functionality exists

**Tasks**:
- Create mapping between recommendation API and TTS API
- Test end-to-end flow
- Cache mapping results

---

## 💾 Database Recommendations (If Needed Later)

### For When You Need Persistence Beyond JSON:

#### 🏆 **Recommended: Supabase**
- **Free Tier**: 500MB database, 2GB storage
- **Setup Time**: 5 minutes
- **Features**: PostgreSQL, Realtime, Auth, Storage
- **Perfect for**: Moving from JSON to real DB
```javascript
// Super simple setup
import { createClient } from '@supabase/supabase-js'
const supabase = createClient(url, key)
```

#### Alternative Options:

**2. Firebase Firestore**
- Free: 1GB storage, 50K reads/day
- NoSQL, realtime sync
- Great for user data

**3. MongoDB Atlas**
- Free: 512MB storage
- JSON-like documents
- Easy migration from JSON files

**4. SQLite (Local)**
- Zero setup
- File-based
- Perfect for desktop/local testing

---

## 🚀 Today's Implementation Steps

### Knowledge Base System (No DB Required!)

1. **Create knowledge structure** (30 min)
   ```bash
   mkdir -p backend_clean/knowledge/{yoon_ahri,taepung,park_hyun}
   ```

2. **Add sample knowledge** (30 min)
   - Create JSON files with character-specific knowledge
   - Add ASMR tips for 윤아리
   - Add debate techniques for 태풍
   - Add anger management for 박현

3. **Build backend service** (1 hour)
   - Knowledge loader service
   - Search/match algorithm
   - API endpoints

4. **Create frontend UI** (2 hours)
   - Knowledge management page
   - CRUD operations
   - Preview functionality

5. **Integrate with chat** (1 hour)
   - Modify chat endpoint
   - Add knowledge context
   - Test knowledge retrieval

### Why This Approach is Perfect:
- ✅ **No database setup** - Start coding immediately
- ✅ **No costs** - Everything runs locally
- ✅ **Easy to test** - Just edit JSON files
- ✅ **Portable** - Copy folder to deploy anywhere
- ✅ **Upgradeable** - Easy to migrate to DB later

---

## 📊 Success Metrics

### Knowledge Base (This Week)
- [ ] 10+ knowledge items per character
- [ ] <100ms search response time
- [ ] 80% relevance accuracy
- [ ] Visual feedback when knowledge used

### Character Management (Next Week)
- [ ] Full CRUD operations
- [ ] Image upload working
- [ ] Voice preview in creation

### Production Ready (Week 3)
- [ ] All features integrated
- [ ] Error handling complete
- [ ] Performance optimized

---

## 🔄 Quick Start Commands

```bash
# Start development now
cd backend_clean
python main.py

# In another terminal
cd frontend
npm run dev

# Knowledge files location
ls backend_clean/knowledge/
```

Ready to implement the Knowledge Base system? It requires NO database and can be built entirely with JSON files! 🚀