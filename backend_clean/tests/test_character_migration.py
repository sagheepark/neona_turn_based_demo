"""
TDD Tests for Character and Knowledge Base Migration to MongoDB
RED PHASE: Write failing tests for character migration
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import asyncio
from services.database_service import DatabaseService

class TestCharacterMigration:
    def setup_method(self):
        self.database_service = DatabaseService()
        
    def test_should_migrate_characters_to_mongodb(self):
        """
        Test 15.1: Should migrate character definitions from demo-characters.ts to MongoDB
        
        RED PHASE: This test fails because character migration doesn't exist yet
        Character data should be extracted from frontend and stored in MongoDB collections
        """
        async def test_character_migration():
            try:
                from services.migration_service import MigrationService
                
                # Given: Character definitions in frontend/src/data/demo-characters.ts
                migration_service = MigrationService(self.database_service)
                await self.database_service.connect()
                
                # When: Character migration script runs
                migration_result = await migration_service.migrate_characters()
                
                # Then: Should create documents in characters collection  
                assert migration_result["success"] is True, "Migration should succeed"
                assert migration_result["characters_migrated"] >= 4, "Should migrate at least 4 demo characters"
                
                # And: Should maintain all character data structure
                characters = await self.database_service.characters.find({}).to_list(length=None)
                if characters:
                    character = characters[0]
                    assert "character_id" in character, "Should have character_id field"
                    assert "name" in character, "Should have name field" 
                    assert "description" in character, "Should have description field"
                    assert "prompt" in character, "Should have prompt field"
                    assert "voice_id" in character, "Should have voice_id field"
                    
                await self.database_service.close()
                
                print("✅ GREEN PHASE: Character migration working correctly")
                return True
                
            except ImportError as e:
                print(f"🔴 RED PHASE: Character migration not implemented - {str(e)}")
                return False
            except Exception as e:
                print(f"🔴 RED PHASE: Character migration failed - {str(e)}")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(test_character_migration())
            if result:
                return  # Test passes
        except Exception as e:
            print(f"🔴 RED PHASE: Migration functionality not implemented - {str(e)}")
        finally:
            loop.close()
        
        # EXPECTED FAILURE: Character migration doesn't exist yet
        # This test documents the requirement for character migration
        assert False, "Should provide character migration from frontend data to MongoDB"
        
    def test_should_migrate_knowledge_bases_to_mongodb(self):
        """
        Test 15.2: Should migrate character knowledge bases to MongoDB
        
        RED PHASE: This test fails because knowledge migration doesn't exist yet
        Knowledge data should be extracted from backend/knowledge/ and stored in MongoDB
        """
        async def test_knowledge_migration():
            try:
                from services.migration_service import MigrationService
                
                # Given: Knowledge files in backend_clean/knowledge/characters/
                migration_service = MigrationService(self.database_service)
                await self.database_service.connect()
                
                # When: Knowledge migration script runs
                migration_result = await migration_service.migrate_knowledge()
                
                # Then: Should create documents in knowledge collection
                assert migration_result["success"] is True, "Migration should succeed"
                assert migration_result["knowledge_migrated"] >= 13, "Should migrate Dr Python's 13 knowledge items"
                
                # And: Should preserve all knowledge structure
                knowledge_items = await self.database_service.knowledge.find({}).to_list(length=None)
                if knowledge_items:
                    knowledge = knowledge_items[0]
                    assert "character_id" in knowledge, "Should have character_id field"
                    assert "knowledge_id" in knowledge, "Should have knowledge_id field"
                    assert "title" in knowledge, "Should have title field"
                    assert "content" in knowledge, "Should have content field"
                    assert "tags" in knowledge, "Should have tags field"
                    assert "trigger_keywords" in knowledge, "Should have trigger_keywords field"
                    
                await self.database_service.close()
                
                print("✅ GREEN PHASE: Knowledge migration working correctly")
                return True
                
            except ImportError as e:
                print(f"🔴 RED PHASE: Knowledge migration not implemented - {str(e)}")
                return False
            except Exception as e:
                print(f"🔴 RED PHASE: Knowledge migration failed - {str(e)}")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(test_knowledge_migration())
            if result:
                return  # Test passes
        except Exception as e:
            print(f"🔴 RED PHASE: Migration functionality not implemented - {str(e)}")
        finally:
            loop.close()
        
        # EXPECTED FAILURE: Knowledge migration doesn't exist yet
        # This test documents the requirement for knowledge migration
        assert False, "Should provide knowledge migration from JSON files to MongoDB"
        
    def test_should_link_characters_with_knowledge_bases(self):
        """
        Test 15.3: Should properly link characters with their knowledge bases
        
        RED PHASE: This test fails because character-knowledge linking doesn't exist yet
        Characters should be associated with their specific knowledge bases
        """
        async def test_character_knowledge_linking():
            try:
                from services.character_service import CharacterService
                
                # Given: Characters and knowledge migrated to MongoDB
                character_service = CharacterService(self.database_service)
                await self.database_service.connect()
                
                # When: Get character with knowledge base
                character_with_knowledge = await character_service.get_character_with_knowledge("dr_python")
                
                # Then: Should return character with linked knowledge
                assert character_with_knowledge is not None, "Should find character"
                assert "character" in character_with_knowledge, "Should have character data"
                assert "knowledge_items" in character_with_knowledge, "Should have knowledge items"
                
                character = character_with_knowledge["character"]
                knowledge_items = character_with_knowledge["knowledge_items"]
                
                assert character["character_id"] == "dr_python", "Should be correct character"
                assert len(knowledge_items) >= 13, "Should have Dr Python's knowledge items"
                assert knowledge_items[0]["character_id"] == "dr_python", "Knowledge should be linked to character"
                
                await self.database_service.close()
                
                print("✅ GREEN PHASE: Character-knowledge linking working correctly")
                return True
                
            except ImportError as e:
                print(f"🔴 RED PHASE: CharacterService not implemented - {str(e)}")
                return False
            except Exception as e:
                print(f"🔴 RED PHASE: Character-knowledge linking failed - {str(e)}")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(test_character_knowledge_linking())
            if result:
                return  # Test passes
        except Exception as e:
            print(f"🔴 RED PHASE: Character service not implemented - {str(e)}")
        finally:
            loop.close()
        
        # EXPECTED FAILURE: CharacterService doesn't exist yet
        # This test documents the requirement for character-knowledge linking
        assert False, "Should provide CharacterService with character-knowledge linking functionality"
        
    def test_should_maintain_character_knowledge_integrity(self):
        """
        Test 15.4: Should maintain data integrity between characters and knowledge
        
        RED PHASE: This test fails because data integrity validation doesn't exist yet
        Migration should preserve all relationships and data consistency
        """
        async def test_data_integrity():
            try:
                # Given: Characters and knowledge migrated to MongoDB
                await self.database_service.connect()
                
                # When: Check data integrity
                characters = await self.database_service.characters.find({}).to_list(length=None)
                knowledge_items = await self.database_service.knowledge.find({}).to_list(length=None)
                
                # Then: Every character should exist
                expected_characters = {"dr_python", "yoon_ahri", "taepung", "park_hyun"}
                actual_characters = {char["character_id"] for char in characters}
                assert expected_characters.issubset(actual_characters), f"Missing characters: {expected_characters - actual_characters}"
                
                # And: Knowledge should be properly linked
                dr_python_knowledge = [k for k in knowledge_items if k["character_id"] == "dr_python"]
                assert len(dr_python_knowledge) >= 13, f"Dr Python should have at least 13 knowledge items, found {len(dr_python_knowledge)}"
                
                # And: Knowledge items should have all required fields
                for knowledge in dr_python_knowledge[:3]:  # Check first 3 items
                    required_fields = ["knowledge_id", "character_id", "title", "content", "tags", "trigger_keywords"]
                    for field in required_fields:
                        assert field in knowledge, f"Knowledge item missing {field} field"
                
                await self.database_service.close()
                
                print("✅ GREEN PHASE: Data integrity validation working correctly")
                return True
                
            except Exception as e:
                print(f"🔴 RED PHASE: Data integrity check failed - {str(e)}")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(test_data_integrity())
            if result:
                return  # Test passes
        except Exception as e:
            print(f"🔴 RED PHASE: Data integrity functionality not implemented - {str(e)}")
        finally:
            loop.close()
        
        # EXPECTED FAILURE: Complete migration functionality doesn't exist yet
        # This test documents the requirement for data integrity validation
        assert False, "Should maintain data integrity between characters and knowledge after migration"