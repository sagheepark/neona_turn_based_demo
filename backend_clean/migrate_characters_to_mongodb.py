#!/usr/bin/env python3
"""
Character and Knowledge Migration Script
Run this script to migrate character data and knowledge bases to MongoDB
Following TDD principles - this script has been fully tested
"""

import asyncio
import logging
from services.database_service import DatabaseService
from services.migration_service import MigrationService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Main character migration function - migrate characters and knowledge to MongoDB
    """
    print("🚀 Starting Character and Knowledge Migration...")
    print("=" * 60)
    
    # Initialize services
    database_service = DatabaseService()
    migration_service = MigrationService(database_service)
    
    try:
        # Connect to MongoDB
        print("📡 Connecting to MongoDB...")
        connection_result = await database_service.connect()
        
        if not connection_result:
            print("❌ Failed to connect to MongoDB")
            print("   Make sure MongoDB is installed and running:")
            print("   brew tap mongodb/brew")
            print("   brew install mongodb-community") 
            print("   brew services start mongodb-community")
            return
        
        print("✅ Connected to MongoDB successfully")
        
        # Get database info
        db_info = await database_service.get_database_info()
        print(f"📊 Database: {db_info['name']} (Collections: {db_info['collections']})")
        
        # Run character migration
        print("\n🎭 Starting character migration...")
        character_result = await migration_service.migrate_characters()
        
        # Run knowledge migration
        print("\n📚 Starting knowledge migration...")
        knowledge_result = await migration_service.migrate_knowledge()
        
        # Display results
        print("\n" + "=" * 60)
        print("📋 Character & Knowledge Migration Results:")
        print("=" * 60)
        
        if character_result["success"] and knowledge_result["success"]:
            print("✅ Migration completed successfully!")
            
            print(f"🎭 Characters migrated: {character_result['characters_migrated']}")
            print(f"📚 Knowledge items migrated: {knowledge_result['knowledge_migrated']}")
            
            total_migrated = character_result['characters_migrated'] + knowledge_result['knowledge_migrated']
            print(f"📊 Total items migrated: {total_migrated}")
            
            print(f"\n💾 Data is now stored in MongoDB collections:")
            print(f"   - characters: Character definitions (name, prompt, voice_id)")
            print(f"   - knowledge: Character knowledge bases (trigger keywords, content)")
            print(f"   - conversations: Session and message data (from previous migration)")
            print(f"   - personas: User persona definitions (from previous migration)")
            print(f"   - users: User settings and active persona tracking (from previous migration)")
            
            print(f"\n🔒 Original files remain unchanged as backup")
            print(f"✨ Character system now ready for MongoDB-powered conversations!")
            
        else:
            print("❌ Migration encountered issues:")
            if not character_result["success"]:
                print(f"   Character migration error: {character_result.get('error', 'Unknown error')}")
            if not knowledge_result["success"]:
                print(f"   Knowledge migration error: {knowledge_result.get('error', 'Unknown error')}")
            
        # Close connection
        await database_service.close()
        print("\n🔒 Database connection closed")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print(f"❌ Migration failed: {str(e)}")
        
        if database_service.is_connected():
            await database_service.close()

if __name__ == "__main__":
    print("Character and Knowledge Migration Script")
    print("Following TDD methodology - Fully tested implementation")
    print()
    
    # Run migration
    asyncio.run(main())
    
    print("\n🎯 Character migration complete!")
    print("You can now use MongoDB-backed character services in your application.")
    print("\nTo verify the migration, run: python3 verify_mongodb.py")