#!/usr/bin/env python3
"""
Migration script to add temperature settings to existing characters
Following the recommendations from plan.md
"""

import asyncio
from services.database_service import DatabaseService
from services.character_service import CharacterService

# Recommended temperatures for demo characters
CHARACTER_TEMPERATURES = {
    'yoon_ahri': 0.5,      # ASMR 상담사 - Consistent, supportive
    'taepung': 0.9,        # 논쟁꾼 - Creative, unpredictable  
    'park_hyun': 0.8,      # 분노 대행 - Emotional, varied
    'kim_python': 0.6,     # 프로그래머 - Logical, accurate
    'seol_min_seok': 0.7,  # 역사 교육자 - Balanced
    'game_master': 0.85    # 게임 마스터 - Creative storytelling
}

async def migrate_character_temperatures():
    """Add temperature field to existing characters"""
    
    # Initialize services
    database_service = DatabaseService()
    character_service = CharacterService(database_service)
    
    try:
        # Connect to database
        await database_service.connect()
        print("✅ Connected to database")
        
        # Get all characters
        characters = await character_service.get_all_characters()
        print(f"📊 Found {len(characters)} characters")
        
        updated_count = 0
        
        for character in characters:
            character_id = character.get('character_id')
            
            # Skip if already has temperature
            if 'temperature' in character:
                print(f"⏭️  {character_id}: Already has temperature ({character['temperature']})")
                continue
            
            # Get recommended temperature or use default
            recommended_temp = CHARACTER_TEMPERATURES.get(character_id, 0.7)
            
            # Update character with temperature
            await character_service.update_character(character_id, {
                'temperature': recommended_temp
            })
            
            updated_count += 1
            print(f"✅ {character_id}: Added temperature = {recommended_temp}")
        
        print(f"\n🎯 Migration completed: Updated {updated_count} characters")
        
        # Verify the updates
        print("\n🔍 Verification:")
        for character_id, expected_temp in CHARACTER_TEMPERATURES.items():
            character = await character_service.get_character(character_id)
            if character:
                actual_temp = character.get('temperature', 'MISSING')
                status = "✅" if actual_temp == expected_temp else "❌"
                print(f"{status} {character_id}: {actual_temp}")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        await database_service.disconnect()
        print("🔌 Disconnected from database")

if __name__ == "__main__":
    print("🌡️ Starting character temperature migration...")
    print("-" * 50)
    
    asyncio.run(migrate_character_temperatures())
    
    print("\n✨ Migration completed!")
    print("Characters now have temperature settings for personalized creativity levels.")