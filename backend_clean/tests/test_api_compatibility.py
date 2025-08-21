"""
TDD Test for API Compatibility Layer - MongoDB Migration
RED PHASE: Write failing test for API compatibility after MongoDB migration
Following TDD methodology: Red → Green → Refactor
"""

import pytest
import asyncio
from services.database_service import DatabaseService
from services.conversation_service import ConversationService
from services.persona_service import PersonaService

class TestAPICompatibility:
    def setup_method(self):
        self.database_service = DatabaseService()
        
    def test_should_maintain_api_compatibility_after_migration(self):
        """
        Test 14.4: Should maintain API compatibility after MongoDB migration
        
        RED PHASE: This test fails because services still use file-based storage
        API endpoints should work identically with MongoDB backend
        """
        async def test_mongodb_api_compatibility():
            try:
                # Given: MongoDB is connected and has migrated data
                await self.database_service.connect()
                
                # When: Using services that should work with MongoDB
                conversation_service = ConversationService(storage_type="mongodb", database_service=self.database_service)
                persona_service = PersonaService(storage_type="mongodb", database_service=self.database_service)
                
                # Then: Services should initialize without errors
                assert conversation_service is not None, "ConversationService should initialize with MongoDB"
                assert persona_service is not None, "PersonaService should initialize with MongoDB"
                
                # And: Basic operations should work the same way
                user_id = "test_api_user"
                character_id = "dr_python"
                
                # Test conversation creation (should work identically to file-based)
                session_data = await conversation_service.create_session_async(user_id, character_id)
                assert session_data["success"] is True, "Session creation should work with MongoDB"
                assert "session_id" in session_data, "Should return session_id like file-based version"
                
                # Test persona operations (should work identically to file-based)
                personas = await persona_service.get_user_personas_async(user_id)
                assert isinstance(personas, list), "Should return persona list like file-based version"
                
                await self.database_service.close()
                
                print("✅ GREEN PHASE: MongoDB API compatibility working correctly")
                return True
                
            except Exception as e:
                print(f"🔴 RED PHASE: API compatibility not implemented - {str(e)}")
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(test_mongodb_api_compatibility())
            if result:
                return  # Test passes
        except Exception as e:
            print(f"🔴 RED PHASE: MongoDB API compatibility not implemented - {str(e)}")
        finally:
            loop.close()
        
        # EXPECTED FAILURE: Services don't support MongoDB yet
        # This test documents the requirement for MongoDB API compatibility
        assert False, "Services should support MongoDB storage while maintaining API compatibility"