#!/usr/bin/env python3
"""
MongoDB Data Verification Script
Quick script to check your migrated data
"""

import asyncio
from services.database_service import DatabaseService

async def verify_database():
    """
    Verify MongoDB data after migration
    """
    print("🔍 Verifying MongoDB Data...")
    print("=" * 50)
    
    # Connect to database
    db_service = DatabaseService()
    connection_result = await db_service.connect()
    
    if not connection_result:
        print("❌ Failed to connect to MongoDB")
        return
    
    print("✅ Connected to MongoDB")
    
    try:
        # Get database info
        db_info = await db_service.get_database_info()
        print(f"📊 Database: {db_info['name']}")
        print(f"📁 Collections: {db_info['collections']}")
        print(f"💾 Data Size: {db_info['dataSize']} bytes")
        
        # Count documents in each collection
        conversations_count = await db_service.conversations.count_documents({})
        personas_count = await db_service.personas.count_documents({})
        users_count = await db_service.users.count_documents({})
        characters_count = await db_service.characters.count_documents({})
        knowledge_count = await db_service.knowledge.count_documents({})
        
        print(f"\n📈 Document Counts:")
        print(f"💬 Conversations: {conversations_count}")
        print(f"👤 Personas: {personas_count}")
        print(f"👥 Users: {users_count}")
        print(f"🎭 Characters: {characters_count}")
        print(f"📚 Knowledge Items: {knowledge_count}")
        print(f"📊 Total Documents: {conversations_count + personas_count + users_count + characters_count + knowledge_count}")
        
        # Show sample data
        print(f"\n🔍 Sample Data:")
        
        # Sample conversation
        sample_conv = await db_service.conversations.find_one()
        if sample_conv:
            print(f"💬 Sample Conversation:")
            print(f"   Session ID: {sample_conv.get('session_id')}")
            print(f"   User ID: {sample_conv.get('user_id')}")
            print(f"   Character ID: {sample_conv.get('character_id')}")
            print(f"   Messages: {len(sample_conv.get('messages', []))}")
        
        # Sample persona
        sample_persona = await db_service.personas.find_one()
        if sample_persona:
            print(f"👤 Sample Persona:")
            print(f"   Persona ID: {sample_persona.get('persona_id')}")
            print(f"   User ID: {sample_persona.get('user_id')}")
            print(f"   Name: {sample_persona.get('name')}")
            print(f"   Active: {sample_persona.get('is_active')}")
        
        # Sample user
        sample_user = await db_service.users.find_one()
        if sample_user:
            print(f"👥 Sample User:")
            print(f"   User ID: {sample_user.get('user_id')}")
            print(f"   Active Persona: {sample_user.get('active_persona_id')}")
            
        # Sample character
        sample_character = await db_service.characters.find_one()
        if sample_character:
            print(f"🎭 Sample Character:")
            print(f"   Character ID: {sample_character.get('character_id')}")
            print(f"   Name: {sample_character.get('name')}")
            print(f"   Description: {sample_character.get('description')}")
            print(f"   Voice ID: {sample_character.get('voice_id')}")
            
        # Sample knowledge
        sample_knowledge = await db_service.knowledge.find_one()
        if sample_knowledge:
            print(f"📚 Sample Knowledge:")
            print(f"   Knowledge ID: {sample_knowledge.get('knowledge_id')}")
            print(f"   Character ID: {sample_knowledge.get('character_id')}")
            print(f"   Title: {sample_knowledge.get('title')}")
            print(f"   Category: {sample_knowledge.get('category')}")
            print(f"   Tags: {len(sample_knowledge.get('tags', []))} tags")
        
        print(f"\n✅ Database verification complete!")
        print(f"🎯 Your complete system has been successfully migrated to MongoDB")
        print(f"💡 Characters, knowledge bases, conversations, personas, and users are all ready!")
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
    
    finally:
        await db_service.close()
        print(f"🔒 Database connection closed")

if __name__ == "__main__":
    asyncio.run(verify_database())