#!/usr/bin/env python3
"""
Populate Sample Data Script
Creates sample data for demonstration purposes
"""

import json
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_sample_data():
    """Create sample MongoDB data for the demo"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/neona_chat')
    client = MongoClient(mongodb_url)
    
    # Get database name from URL
    db_name = mongodb_url.split('/')[-1].split('?')[0]
    db = client[db_name]
    
    print(f"📦 Creating sample data in database: {db_name}")
    print("-" * 50)
    
    # Sample Characters Collection
    characters_data = [
        {
            "_id": ObjectId(),
            "character_id": "seol_min_seok",
            "name": "설민석",
            "description": "역사 교육자이자 방송인",
            "avatar": "/images/설민석.png",
            "voice": "seolminseok_tts",
            "personality": "교육적이고 열정적인 역사 선생님",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "character_id": "park_hyun",
            "name": "박현",
            "description": "친근한 대화 상대",
            "avatar": "/images/박현.png", 
            "voice": "typecast_tts",
            "personality": "친근하고 유머러스한 친구",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "character_id": "yoon_ahri",
            "name": "윤아리",
            "description": "활발하고 긍정적인 캐릭터",
            "avatar": "/images/윤아리.png",
            "voice": "typecast_tts", 
            "personality": "밝고 활발한 성격",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Insert characters
    characters_collection = db['characters']
    characters_collection.delete_many({})  # Clear existing
    characters_collection.insert_many(characters_data)
    print(f"✅ Created characters collection: {len(characters_data)} documents")
    
    # Sample Knowledge Base for 설민석
    knowledge_data = [
        {
            "_id": ObjectId(),
            "character_id": "seol_min_seok",
            "topic": "조선시대",
            "content": "조선시대는 1392년부터 1897년까지 505년간 지속된 한국의 마지막 왕조입니다. 태조 이성계가 개국했으며, 성리학을 통치 이념으로 삼았습니다.",
            "keywords": ["조선", "이성계", "성리학", "왕조"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "character_id": "seol_min_seok", 
            "topic": "임진왜란",
            "content": "임진왜란(1592-1598)은 일본이 조선을 침입한 전쟁입니다. 이순신의 활약과 의병활동, 명군의 지원으로 일본군을 물리쳤습니다.",
            "keywords": ["임진왜란", "이순신", "의병", "일본침입"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "_id": ObjectId(),
            "character_id": "seol_min_seok",
            "topic": "세종대왕",
            "content": "세종대왕(1397-1450)은 조선 제4대 왕으로 한글 창제, 과학기술 발달, 영토 확장 등 많은 업적을 남겼습니다.",
            "keywords": ["세종대왕", "한글", "훈민정음", "과학기술"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Insert knowledge base
    knowledge_collection = db['knowledge_base']
    knowledge_collection.delete_many({})
    knowledge_collection.insert_many(knowledge_data)
    print(f"✅ Created knowledge_base collection: {len(knowledge_data)} documents")
    
    # Sample User Personas
    personas_data = [
        {
            "_id": ObjectId(),
            "user_id": "demo_user",
            "name": "데모 사용자",
            "preferences": {
                "preferred_language": "korean",
                "interaction_style": "casual",
                "topics_of_interest": ["역사", "교육", "문화"]
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    # Insert personas
    personas_collection = db['user_personas']
    personas_collection.delete_many({})
    personas_collection.insert_many(personas_data)
    print(f"✅ Created user_personas collection: {len(personas_data)} documents")
    
    # Sample Conversations (empty for privacy)
    conversations_data = [
        {
            "_id": ObjectId(),
            "session_id": "demo_session_001",
            "user_id": "demo_user",
            "character_id": "seol_min_seok",
            "messages": [
                {
                    "role": "assistant",
                    "content": "안녕하세요! 역사 교육자 설민석입니다. 오늘은 어떤 역사 이야기가 궁금하신가요?",
                    "timestamp": datetime.now(),
                    "audio_data": None
                }
            ],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "status": "active"
        }
    ]
    
    # Insert conversations
    conversations_collection = db['conversations']
    conversations_collection.delete_many({})
    conversations_collection.insert_many(conversations_data)
    print(f"✅ Created conversations collection: {len(conversations_data)} documents")
    
    print("-" * 50)
    print("✅ Sample data creation complete!")
    print("\n📊 Database Statistics:")
    for collection_name in db.list_collection_names():
        count = db[collection_name].count_documents({})
        print(f"  - {collection_name}: {count} documents")
    
    client.close()

def export_sample_data():
    """Export the sample data we just created"""
    print("\n🔄 Now exporting sample data to JSON files...")
    os.system('python3 export_mongodb_data.py')

if __name__ == "__main__":
    print("Sample Data Creator")
    print("==================")
    print("This will create sample data for demo purposes")
    print("⚠️  This will replace existing data in the database")
    
    response = input("\nDo you want to continue? (yes/no): ").lower().strip()
    
    if response == 'yes':
        create_sample_data()
        
        # Ask if they want to export too
        export_response = input("\nDo you want to export this data to JSON files? (yes/no): ").lower().strip()
        if export_response == 'yes':
            export_sample_data()
    else:
        print("❌ Operation cancelled")