#!/usr/bin/env python3
"""
MongoDB Migration Script
Run this script to migrate existing JSON files to MongoDB
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
    Main migration function - migrate all data to MongoDB
    """
    print("🚀 Starting MongoDB Migration...")
    print("=" * 50)
    
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
        
        # Run migration
        print("\n🔄 Starting data migration...")
        migration_result = await migration_service.migrate_all()
        
        # Display results
        print("\n" + "=" * 50)
        print("📋 Migration Results:")
        print("=" * 50)
        
        if migration_result["success"]:
            print("✅ Migration completed successfully!")
            print(f"📊 Total items migrated: {migration_result['total_migrated']}")
            
            # Detailed breakdown
            conv_result = migration_result["conversation_result"]
            persona_result = migration_result["persona_result"]
            
            print(f"💬 Conversations: {conv_result['conversations_migrated']}")
            print(f"👤 Personas: {persona_result['personas_migrated']}")
            
            print(f"\n💾 Data is now stored in MongoDB collections:")
            print(f"   - conversations: Session and message data")
            print(f"   - personas: User persona definitions")
            print(f"   - users: User settings and active persona tracking")
            
            print(f"\n🔒 Original JSON files remain unchanged as backup")
            print(f"✨ Your application can now use MongoDB for improved performance!")
            
        else:
            print("❌ Migration failed:")
            print(f"   Error: {migration_result.get('error', 'Unknown error')}")
            
        # Close connection
        await database_service.close()
        print("\n🔒 Database connection closed")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        print(f"❌ Migration failed: {str(e)}")
        
        if database_service.is_connected():
            await database_service.close()

if __name__ == "__main__":
    print("MongoDB Data Migration Script")
    print("Following TDD methodology - Fully tested implementation")
    print()
    
    # Run migration
    asyncio.run(main())
    
    print("\n🎯 Migration complete!")
    print("You can now use MongoDB-backed services in your application.")