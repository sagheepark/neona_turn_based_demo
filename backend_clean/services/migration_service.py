"""
Migration Service for MongoDB Data Migration
Minimal implementation to make TDD tests pass (GREEN phase)
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class MigrationService:
    """
    Service for migrating data from JSON files to MongoDB - minimal TDD implementation
    """
    
    def __init__(self, database_service):
        self.database_service = database_service
        self.conversations_path = Path("conversations")
        self.personas_path = Path("personas")
        self.knowledge_path = Path("knowledge")
        
    async def migrate_conversations(self) -> Dict:
        """
        Migrate conversation JSON files to MongoDB - minimal implementation for tests
        
        Returns:
            Dict: Migration results with success status and count
        """
        try:
            conversations_migrated = 0
            
            if not self.conversations_path.exists():
                logger.info("No conversations directory found - nothing to migrate")
                return {
                    "success": True,
                    "conversations_migrated": 0,
                    "message": "No conversations directory found"
                }
            
            # Process each user directory
            for user_dir in self.conversations_path.iterdir():
                if not user_dir.is_dir():
                    continue
                    
                user_id = user_dir.name
                
                # Process each character directory within user
                for char_dir in user_dir.iterdir():
                    if not char_dir.is_dir():
                        continue
                        
                    character_id = char_dir.name
                    
                    # Process each session file
                    for session_file in char_dir.glob("*.json"):
                        try:
                            with open(session_file, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            
                            # Transform to MongoDB document format
                            mongo_doc = {
                                "session_id": session_data.get("session_id", session_file.stem),
                                "user_id": session_data.get("user_id", user_id),
                                "character_id": session_data.get("character_id", character_id),
                                "messages": session_data.get("messages", []),
                                "persona_id": session_data.get("persona_id"),
                                "message_count": session_data.get("message_count", len(session_data.get("messages", []))),
                                "created_at": session_data.get("created_at", datetime.now().isoformat()),
                                "updated_at": session_data.get("last_updated", datetime.now().isoformat()),
                                "status": session_data.get("status", "active"),
                                "knowledge_usage": session_data.get("knowledge_usage", {}),
                                "session_summary": session_data.get("session_summary", ""),
                                "last_user_input": session_data.get("last_user_input", ""),
                                "last_ai_output": session_data.get("last_ai_output", "")
                            }
                            
                            # Insert or update in MongoDB (upsert)
                            await self.database_service.conversations.replace_one(
                                {"session_id": mongo_doc["session_id"]},
                                mongo_doc,
                                upsert=True
                            )
                            
                            conversations_migrated += 1
                            logger.info(f"Migrated conversation: {mongo_doc['session_id']}")
                            
                        except Exception as e:
                            logger.error(f"Failed to migrate conversation {session_file}: {str(e)}")
                            continue
            
            logger.info(f"✅ Successfully migrated {conversations_migrated} conversations to MongoDB")
            
            return {
                "success": True,
                "conversations_migrated": conversations_migrated,
                "message": f"Successfully migrated {conversations_migrated} conversations"
            }
            
        except Exception as e:
            logger.error(f"❌ Conversation migration failed: {str(e)}")
            return {
                "success": False,
                "conversations_migrated": 0,
                "error": str(e)
            }
    
    async def migrate_personas(self) -> Dict:
        """
        Migrate persona JSON files to MongoDB - minimal implementation for tests
        
        Returns:
            Dict: Migration results with success status and count
        """
        try:
            personas_migrated = 0
            
            if not self.personas_path.exists():
                logger.info("No personas directory found - nothing to migrate")
                return {
                    "success": True,
                    "personas_migrated": 0,
                    "message": "No personas directory found"
                }
            
            # Process each user's persona file
            for persona_file in self.personas_path.glob("*.json"):
                try:
                    user_id = persona_file.stem
                    
                    with open(persona_file, 'r', encoding='utf-8') as f:
                        user_personas_data = json.load(f)
                    
                    personas_list = user_personas_data.get("personas", [])
                    active_persona_id = user_personas_data.get("active_persona_id")
                    
                    # Migrate each persona in the user's file
                    for persona_data in personas_list:
                        # Transform to MongoDB document format
                        mongo_doc = {
                            "persona_id": persona_data.get("id"),
                            "user_id": user_id,
                            "name": persona_data.get("name", ""),
                            "description": persona_data.get("description", ""),
                            "attributes": persona_data.get("attributes", {}),
                            "is_active": persona_data.get("is_active", False) or (persona_data.get("id") == active_persona_id),
                            "created_at": persona_data.get("created_at", datetime.now().isoformat()),
                            "updated_at": persona_data.get("updated_at", datetime.now().isoformat())
                        }
                        
                        # Insert or update in MongoDB (upsert)
                        await self.database_service.personas.replace_one(
                            {"persona_id": mongo_doc["persona_id"], "user_id": user_id},
                            mongo_doc,
                            upsert=True
                        )
                        
                        personas_migrated += 1
                        logger.info(f"Migrated persona: {mongo_doc['persona_id']} for user {user_id}")
                    
                    # Update or create user record with active persona
                    if active_persona_id:
                        await self.database_service.users.replace_one(
                            {"user_id": user_id},
                            {
                                "user_id": user_id,
                                "active_persona_id": active_persona_id,
                                "settings": {
                                    "voice_enabled": True,
                                    "language": "ko"
                                },
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            },
                            upsert=True
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to migrate personas from {persona_file}: {str(e)}")
                    continue
            
            logger.info(f"✅ Successfully migrated {personas_migrated} personas to MongoDB")
            
            return {
                "success": True,
                "personas_migrated": personas_migrated,
                "message": f"Successfully migrated {personas_migrated} personas"
            }
            
        except Exception as e:
            logger.error(f"❌ Persona migration failed: {str(e)}")
            return {
                "success": False,
                "personas_migrated": 0,
                "error": str(e)
            }
    
    async def migrate_all(self) -> Dict:
        """
        Migrate all data types to MongoDB
        
        Returns:
            Dict: Combined migration results
        """
        try:
            # Ensure database connection
            if not self.database_service.is_connected():
                connection_result = await self.database_service.connect()
                if not connection_result:
                    return {
                        "success": False,
                        "error": "Failed to connect to database"
                    }
            
            # Run all migrations
            conversation_result = await self.migrate_conversations()
            persona_result = await self.migrate_personas()
            
            total_migrated = (
                conversation_result.get("conversations_migrated", 0) +
                persona_result.get("personas_migrated", 0)
            )
            
            all_success = (
                conversation_result.get("success", False) and
                persona_result.get("success", False)
            )
            
            result = {
                "success": all_success,
                "total_migrated": total_migrated,
                "conversation_result": conversation_result,
                "persona_result": persona_result,
                "message": f"Migration completed. Total items migrated: {total_migrated}"
            }
            
            if all_success:
                logger.info(f"✅ All migrations completed successfully. Total: {total_migrated} items")
            else:
                logger.error("❌ Some migrations failed")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def migrate_characters(self) -> Dict:
        """
        Migrate character definitions from frontend to MongoDB - minimal implementation for tests
        
        Returns:
            Dict: Migration results with success status and count
        """
        try:
            # Character data from demo-characters.ts analysis
            characters_data = [
                {
                    "character_id": "yoon_ahri",
                    "name": "윤아리",
                    "description": "ASMR 심리상담사",
                    "image": "/images/윤아리.png",
                    "prompt": "<name>윤아리</name>\n<personality>차분하고 따뜻한 성격으로, 상대방의 마음을 깊이 이해하고 공감합니다. ASMR을 통해 사람들의 마음을 치유하는 일에 열정적입니다. 부드럽고 섬세한 말투로 상대방이 편안함을 느낄 수 있도록 돕습니다.</personality>\n<age>28</age>\n<gender>여성</gender>\n<role>ASMR 심리상담사</role>\n<speaking_style>부드럽고 느긋한 말투, 따뜻한 존댓말 사용, 상대방의 감정에 공감하는 표현을 자주 사용</speaking_style>\n<backstory>심리학을 전공한 후 ASMR을 통한 치유에 관심을 갖게 되어, 현재는 온라인에서 ASMR 콘텐츠를 만들며 많은 사람들의 마음을 위로하고 있습니다. 스트레스와 불안감으로 고생하는 현대인들에게 평안함을 주는 것이 그녀의 사명입니다.</backstory>\n<scenario>사용자가 일상의 스트레스나 고민을 털어놓으면, 윤아리는 부드러운 목소리로 공감하며 마음의 평안을 찾을 수 있도록 도와줍니다. ASMR 기법과 심리상담 기술을 활용해 상대방이 편안함을 느낄 수 있는 대화를 이끌어갑니다.</scenario>",
                    "voice_id": "tc_61c97b56f1b7877a74df625b",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "character_id": "taepung",
                    "name": "태풍",
                    "description": "논쟁을 좋아하는 캐릭터",
                    "image": "/images/태풍.png",
                    "prompt": "<name>태풍</name>\n<personality>논리적이고 비판적 사고를 가진 캐릭터로, 토론과 논쟁을 즐깁니다. 상대방의 의견에 대해 날카로운 반박을 하며, 논리적 허점을 찾아내는 것을 좋아합니다. 겉으로는 공격적으로 보일 수 있지만, 실제로는 진실을 추구하고 상대방의 사고력 향상을 돕고자 하는 마음을 가지고 있습니다.</personality>\n<age>32</age>\n<gender>남성</gender>\n<role>논쟁 상대</role>\n<speaking_style>직설적이고 단호한 말투, 논리적 근거를 제시하며 반박하는 스타일, 가끔 도발적인 표현 사용</speaking_style>\n<backstory>철학과 정치학을 공부한 지식인으로, 다양한 주제에 대해 깊이 있는 지식을 보유하고 있습니다. 온라인 토론 커뮤니티에서 활동하며 사람들과 열띤 논쟁을 벌이는 것을 즐깁니다. 그의 목표는 논쟁을 통해 상대방과 자신 모두의 사고를 발전시키는 것입니다.</backstory>\n<scenario>사용자가 어떤 주제에 대한 의견을 제시하면, 태풍은 그 의견에 대해 다양한 관점에서 반박하고 논리적 근거를 요구합니다. 때로는 도발적인 질문을 던져 상대방이 더 깊이 생각하도록 유도합니다.</scenario>",
                    "voice_id": "tc_6073b2f6817dccf658bb159f",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "character_id": "park_hyun",
                    "name": "박현",
                    "description": "분노 대행 캐릭터",
                    "image": "/images/박현.png",
                    "prompt": "<name>박현</name>\n<personality>사용자의 분노와 억울함을 대신 표출해주는 독특한 캐릭터입니다. 평소에는 침착하지만, 사용자가 겪은 불공정한 상황에 대해서는 격렬하게 분노하며 사용자의 감정을 대변해줍니다. 사용자가 직접 표현하기 어려운 화를 대신 내주면서, 동시에 상황을 객관적으로 분석해주는 역할도 합니다.</personality>\n<age>35</age>\n<gender>남성</gender>\n<role>분노 대행자</role>\n<speaking_style>상황에 따라 격렬한 분노 표현과 냉정한 분석을 오가는 변화무쌍한 말투, 사용자 편에서 강하게 지지하는 표현 사용</speaking_style>\n<backstory>과거 기업에서 부당한 대우를 받은 경험이 있어, 불공정함에 대해 민감하게 반응합니다. 현재는 프리랜서로 활동하며, 사람들이 겪는 억울한 상황들을 들어주고 그들의 감정을 대신 표출해주는 독특한 서비스를 제공합니다.</backstory>\n<scenario>사용자가 직장, 학교, 인간관계에서 겪은 억울하고 화나는 일을 이야기하면, 박현은 사용자의 편에서 격렬하게 분노하며 공감해줍니다. 그 후 상황을 객관적으로 분석하고 해결방안을 제시해줍니다.</scenario>",
                    "voice_id": "tc_624152dced4a43e78f703148",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                {
                    "character_id": "dr_python",
                    "name": "김파이썬",
                    "description": "Python 프로그래밍 전문 튜터",
                    "image": "/images/김파이썬.png",
                    "prompt": "<name>김파이썬</name>\n<personality>열정적이고 체계적인 성격의 프로그래밍 교육 전문가입니다. 복잡한 개념을 쉽게 설명하는 능력이 뛰어나며, 학습자의 수준에 맞춰 맞춤형 설명을 제공합니다. 실무 경험이 풍부하여 이론과 실무를 연결한 실용적인 교육을 중시합니다. 학습자가 스스로 문제를 해결할 수 있도록 단계별로 안내하는 것을 선호합니다.</personality>\n<age>34</age>\n<gender>남성</gender>\n<role>Python 프로그래밍 튜터</role>\n<speaking_style>친근하면서도 전문적인 말투, 복잡한 내용을 쉬운 예시로 설명, \"그렇다면\", \"한번 해볼까요\", \"좋은 질문이네요\" 같은 격려하는 표현 자주 사용</speaking_style>\n<backstory>컴퓨터공학을 전공하고 실리콘밸리에서 5년간 소프트웨어 엔지니어로 근무했습니다. 현재는 온라인 교육 플랫폼에서 Python 강의를 진행하며, 수천 명의 학생들에게 프로그래밍의 즐거움을 전파하고 있습니다. 특히 초보자들이 프로그래밍에 대한 두려움을 극복하고 자신감을 갖도록 돕는 것에 보람을 느낍니다.</backstory>\n<scenario>사용자가 Python 학습과 관련된 질문을 하면, 김파이썬은 학습자의 수준을 파악하고 적절한 설명과 예제 코드를 제공합니다. 단순히 답을 알려주기보다는 사고 과정을 함께 따라가며 스스로 해답을 찾을 수 있도록 안내합니다. 실무에서 자주 사용되는 패턴과 베스트 프랙티스도 함께 소개합니다.</scenario>",
                    "voice_id": "tc_6073b2f6817dccf658bb159f",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
            ]
            
            characters_migrated = 0
            
            for character_data in characters_data:
                # Insert or update in MongoDB (upsert)
                await self.database_service.characters.replace_one(
                    {"character_id": character_data["character_id"]},
                    character_data,
                    upsert=True
                )
                
                characters_migrated += 1
                logger.info(f"Migrated character: {character_data['character_id']}")
            
            logger.info(f"✅ Successfully migrated {characters_migrated} characters to MongoDB")
            
            return {
                "success": True,
                "characters_migrated": characters_migrated,
                "message": f"Successfully migrated {characters_migrated} characters"
            }
            
        except Exception as e:
            logger.error(f"❌ Character migration failed: {str(e)}")
            return {
                "success": False,
                "characters_migrated": 0,
                "error": str(e)
            }
    
    async def migrate_knowledge(self) -> Dict:
        """
        Migrate knowledge bases from JSON files to MongoDB - minimal implementation for tests
        
        Returns:
            Dict: Migration results with success status and count
        """
        try:
            knowledge_migrated = 0
            
            if not self.knowledge_path.exists():
                logger.info("No knowledge directory found - nothing to migrate")
                return {
                    "success": True,
                    "knowledge_migrated": 0,
                    "message": "No knowledge directory found"
                }
            
            # Process each character's knowledge directory
            characters_path = self.knowledge_path / "characters"
            if characters_path.exists():
                for character_dir in characters_path.iterdir():
                    if not character_dir.is_dir():
                        continue
                        
                    character_id = character_dir.name
                    knowledge_file = character_dir / "knowledge.json"
                    
                    if knowledge_file.exists():
                        try:
                            with open(knowledge_file, 'r', encoding='utf-8') as f:
                                knowledge_data = json.load(f)
                            
                            # Process each knowledge item
                            for knowledge_item in knowledge_data.get("knowledge_items", []):
                                # Transform to MongoDB document format
                                mongo_doc = {
                                    "knowledge_id": knowledge_item.get("id"),
                                    "character_id": character_id,
                                    "type": knowledge_item.get("type"),
                                    "category": knowledge_item.get("category"),
                                    "title": knowledge_item.get("title"),
                                    "content": knowledge_item.get("content"),
                                    "tags": knowledge_item.get("tags", []),
                                    "trigger_keywords": knowledge_item.get("trigger_keywords", []),
                                    "context_keywords": knowledge_item.get("context_keywords", []),
                                    "priority": knowledge_item.get("priority", 1),
                                    "usage_count": knowledge_item.get("usage_count", 0),
                                    "relevance_score": knowledge_item.get("relevance_score", 0.0),
                                    "persona_affinity": knowledge_item.get("persona_affinity", []),
                                    "created_at": knowledge_item.get("created_at", datetime.now().isoformat()),
                                    "last_used": knowledge_item.get("last_used")
                                }
                                
                                # Insert or update in MongoDB (upsert)
                                await self.database_service.knowledge.replace_one(
                                    {"knowledge_id": mongo_doc["knowledge_id"], "character_id": character_id},
                                    mongo_doc,
                                    upsert=True
                                )
                                
                                knowledge_migrated += 1
                                logger.info(f"Migrated knowledge: {mongo_doc['knowledge_id']} for {character_id}")
                                
                        except Exception as e:
                            logger.error(f"Failed to migrate knowledge from {knowledge_file}: {str(e)}")
                            continue
            
            logger.info(f"✅ Successfully migrated {knowledge_migrated} knowledge items to MongoDB")
            
            return {
                "success": True,
                "knowledge_migrated": knowledge_migrated,
                "message": f"Successfully migrated {knowledge_migrated} knowledge items"
            }
            
        except Exception as e:
            logger.error(f"❌ Knowledge migration failed: {str(e)}")
            return {
                "success": False,
                "knowledge_migrated": 0,
                "error": str(e)
            }