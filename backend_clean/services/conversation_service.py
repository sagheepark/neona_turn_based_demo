import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ConversationService:
    def __init__(self, storage_type: str = "file", database_service=None):
        self.storage_type = storage_type
        self.database_service = database_service
        
        # Initialize file storage (existing behavior)
        self.conversations_path = Path("conversations")
        self.conversations_path.mkdir(exist_ok=True)
    
    def create_session(self, user_id: str, character_id: str, persona_id: str = None) -> Dict:
        """
        Create new conversation session - minimal implementation to pass test
        
        Args:
            user_id: ID of the user
            character_id: ID of the character  
            persona_id: ID of the user's persona
            
        Returns:
            Dictionary containing session data with unique ID and metadata
        """
        # Generate unique session ID with timestamp and random component
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:6]
        session_id = f"sess_{timestamp}_{unique_id}"
        
        # Create session data structure
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "character_id": character_id,
            "persona_id": persona_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "messages": [],
            "message_count": 0,
            "session_summary": "",
            "session_tags": []
        }
        
        # Save session to file system (existing behavior for backward compatibility)
        user_dir = self.conversations_path / user_id / character_id
        user_dir.mkdir(parents=True, exist_ok=True)
        
        session_file = user_dir / f"{session_id}.json"
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        
        # Return session for backward compatibility (existing tests expect this)
        return session
    
    async def create_session_async(self, user_id: str, character_id: str, persona_id: str = None) -> Dict:
        """
        Async version for MongoDB compatibility - minimal implementation to pass test
        """
        # Generate unique session ID with timestamp and random component
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:6]
        session_id = f"sess_{timestamp}_{unique_id}"
        
        # Create session data structure
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "character_id": character_id,
            "persona_id": persona_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "status": "active",
            "messages": [],
            "message_count": 0,
            "session_summary": "",
            "session_tags": []
        }
        
        # Save session based on storage type
        if self.storage_type == "mongodb" and self.database_service:
            # Save to MongoDB
            if not self.database_service.is_connected():
                await self.database_service.connect()
            await self.database_service.conversations.replace_one(
                {"session_id": session_id},
                session,
                upsert=True
            )
        else:
            # Save session to file system (fallback behavior)
            user_dir = self.conversations_path / user_id / character_id
            user_dir.mkdir(parents=True, exist_ok=True)
            
            session_file = user_dir / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, ensure_ascii=False, indent=2)
        
        # Return consistent API response
        return {
            "success": True,
            "session_id": session_id,
            "session": session
        }
    
    def add_message_to_session(self, session_id: str, role: str, content: str, user_id: str) -> Dict:
        """
        Add a message to an existing session
        
        Args:
            session_id: ID of the session to add message to
            role: Role of the message sender ('user' or 'assistant')
            content: Message content
            user_id: ID of the user (for security/validation)
            
        Returns:
            Updated session data
        """
        # Find the session file
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            raise ValueError(f"Session {session_id} not found")
        
        # Load existing session
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        # Verify user has access to this session
        if session["user_id"] != user_id:
            raise ValueError("User does not have access to this session")
        
        # Create message object
        message = {
            "id": f"msg_{len(session['messages']) + 1:03d}",
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add message and update metadata
        session["messages"].append(message)
        session["message_count"] = len(session["messages"])
        session["last_updated"] = datetime.now().isoformat()
        
        # Save the message first
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        
        # Check if compression is needed after adding the message
        if session["message_count"] > 100 and "compressed_history" not in session:
            # Trigger automatic compression
            try:
                compressed_session = self.compress_session_if_needed(session_id, user_id)
                # Update the session object with compressed version
                session = compressed_session
            except Exception as e:
                # Log compression error but don't fail message addition
                print(f"Warning: Compression failed for session {session_id}: {e}")
                # Continue with uncompressed session
        
        return session
    
    def get_previous_sessions(self, user_id: str, character_id: str) -> List[Dict]:
        """
        Retrieve previous sessions for a user-character pair with last Q&A context
        
        Args:
            user_id: ID of the user
            character_id: ID of the character
            
        Returns:
            List of session summaries with last message pairs for resuming
        """
        user_char_dir = self.conversations_path / user_id / character_id
        
        if not user_char_dir.exists():
            return []
        
        sessions = []
        
        # Load all session files in the directory
        for session_file in user_char_dir.glob("sess_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Extract last Q&A pair for resuming
                last_message_pair = {"user_message": "", "assistant_message": ""}
                messages = session_data.get("messages", [])
                
                if messages:
                    # Find the last user-assistant pair
                    last_user_msg = None
                    last_assistant_msg = None
                    
                    # Look for the most recent user message and its response
                    for i in range(len(messages) - 1, -1, -1):
                        if messages[i]["role"] == "assistant" and last_assistant_msg is None:
                            last_assistant_msg = messages[i]["content"]
                        elif messages[i]["role"] == "user" and last_user_msg is None:
                            last_user_msg = messages[i]["content"]
                        
                        # If we have both, we're done
                        if last_user_msg and last_assistant_msg:
                            break
                    
                    last_message_pair = {
                        "user_message": last_user_msg or "",
                        "assistant_message": last_assistant_msg or ""
                    }
                
                # Create session summary for UI
                session_summary = {
                    "session_id": session_data["session_id"],
                    "user_id": session_data["user_id"], 
                    "character_id": session_data["character_id"],
                    "persona_id": session_data["persona_id"],
                    "created_at": session_data["created_at"],
                    "last_updated": session_data.get("last_updated", session_data["created_at"]),
                    "message_count": session_data.get("message_count", len(messages)),
                    "session_summary": session_data.get("session_summary", ""),
                    "last_message_pair": last_message_pair,
                    "status": session_data.get("status", "active")
                }
                
                sessions.append(session_summary)
                
            except (json.JSONDecodeError, KeyError) as e:
                # Skip corrupted session files
                continue
        
        # Sort by last_updated (most recent first)
        sessions.sort(key=lambda x: x["last_updated"], reverse=True)
        
        return sessions
    
    def load_session_messages(self, session_id: str, user_id: str) -> Dict:
        """
        Load complete session with all messages for continuation
        
        Args:
            session_id: ID of the session to load
            user_id: ID of the user (for security/validation)
            
        Returns:
            Complete session data with all messages and last Q&A pair
        """
        # Find the session file
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            raise ValueError(f"Session {session_id} not found")
        
        # Load session data
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Verify user has access to this session
        if session_data["user_id"] != user_id:
            raise ValueError("User does not have access to this session")
        
        # Extract last Q&A pair for resume context
        last_message_pair = {"user_message": "", "assistant_message": ""}
        messages = session_data.get("messages", [])
        
        if messages:
            # Find the last user-assistant pair
            last_user_msg = None
            last_assistant_msg = None
            
            # Look for the most recent user message and its response
            for i in range(len(messages) - 1, -1, -1):
                if messages[i]["role"] == "assistant" and last_assistant_msg is None:
                    last_assistant_msg = messages[i]["content"]
                elif messages[i]["role"] == "user" and last_user_msg is None:
                    last_user_msg = messages[i]["content"]
                
                # If we have both, we're done
                if last_user_msg and last_assistant_msg:
                    break
            
            last_message_pair = {
                "user_message": last_user_msg or "",
                "assistant_message": last_assistant_msg or ""
            }
        
        # Add last message pair to session data for resuming
        session_data["last_message_pair"] = last_message_pair
        
        return session_data

    def delete_session(self, session_id: str, user_id: str) -> Dict:
        """
        Delete a conversation session - minimum implementation to pass test
        
        Args:
            session_id: ID of the session to delete
            user_id: ID of the user (for security/validation)
            
        Returns:
            Dictionary indicating success/failure of deletion
        """
        # Find the session file
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            return {"success": False, "error": f"Session {session_id} not found"}
        
        # Load session data to verify ownership
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Verify user has access to this session
            if session_data["user_id"] != user_id:
                return {"success": False, "error": "User does not have access to this session"}
            
            # Delete the session file
            session_file.unlink()
            
            return {"success": True, "message": f"Session {session_id} deleted successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Error deleting session: {str(e)}"}
    
    def continue_session(self, session_id: str) -> Dict:
        """
        Continue an existing session - minimal implementation to make tests pass
        
        Args:
            session_id: ID of the session to continue
            
        Returns:
            Dictionary containing the session data to continue from
        """
        # Find the session file
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            raise ValueError(f"Session {session_id} not found")
        
        # Load and return session data
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # Mark session as continued and update timestamp
        session_data["last_updated"] = datetime.now().isoformat()
        session_data["status"] = "continued"
        
        # Save updated session data
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        
        return session_data
    
    def get_session(self, session_id: str, user_id: str) -> Dict:
        """
        Get session by ID with user validation
        
        Args:
            session_id: ID of the session to retrieve
            user_id: ID of the user (for security/validation)
            
        Returns:
            Session data
        """
        # Find the session file
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            raise ValueError(f"Session {session_id} not found")
        
        # Load session
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        # Verify user has access to this session
        if session["user_id"] != user_id:
            raise ValueError("User does not have access to this session")
        
        return session
    
    # ===== CONVERSATION COMPRESSION METHODS (Phase 2) =====
    
    def should_compress_session(self, session_id: str, user_id: str) -> bool:
        """
        Check if session needs compression based on message count threshold
        
        Args:
            session_id: ID of the session to check
            user_id: ID of the user
            
        Returns:
            True if session needs compression, False otherwise
        """
        try:
            session = self.load_session_messages(session_id, user_id)
            return session["message_count"] >= 100
        except (ValueError, KeyError):
            return False
    
    def compress_session_if_needed(self, session_id: str, user_id: str) -> Dict:
        """
        Compress session if it exceeds 100 messages threshold
        
        Following Phase 2 compression strategy:
        - Keep last 20 messages raw for immediate context
        - Compress older messages into summary and core memories
        - Preserve story continuity elements
        
        Args:
            session_id: ID of the session to compress
            user_id: ID of the user
            
        Returns:
            Updated session data with compression applied
        """
        session = self.load_session_messages(session_id, user_id)
        
        if session["message_count"] < 100:
            return session  # No compression needed
        
        messages = session["messages"]
        
        # Keep last 20 messages raw
        recent_messages = messages[-20:]
        older_messages = messages[:-20]
        
        # Handle multiple compressions by preserving previous compressed history
        existing_compressed_count = 0
        if "compression_metadata" in session:
            existing_compressed_count = session["compression_metadata"].get("original_message_count", 0)
        
        # Create compression with Phase 2 strategy
        compression = {
            "conversation_summary": self._create_conversation_summary(older_messages),
            "core_memories": self._extract_core_memories(older_messages),
            "story_continuity": self._preserve_story_continuity(older_messages)
        }
        
        # If there was previous compressed history, merge it
        if "compressed_history" in session:
            # Append new summary to existing one for continuity
            old_summary = session["compressed_history"].get("conversation_summary", "")
            if old_summary:
                compression["conversation_summary"] = old_summary + " | " + compression["conversation_summary"]
            
            # Merge core memories (keep both old and new insights)
            old_memories = session["compressed_history"].get("core_memories", {})
            for key, value in old_memories.items():
                if key not in compression["core_memories"]:
                    compression["core_memories"][key] = value
        
        # Update session with compressed data
        session["messages"] = recent_messages
        session["compressed_history"] = compression
        session["compression_metadata"] = {
            "original_message_count": len(older_messages) + existing_compressed_count,
            "compression_date": datetime.now().isoformat(),
            "compression_ratio": f"{len(older_messages) + existing_compressed_count}:1"
        }
        
        # Save compressed session
        self._save_session(session_id, session)
        
        return session
    
    def _create_conversation_summary(self, messages: List[Dict]) -> str:
        """
        Create a narrative summary of older messages
        
        Phase 2: Simple concatenation-based summary
        Phase 3: AI-powered intelligent summarization
        """
        if not messages:
            return ""
        
        # Simple summary approach for Phase 2
        topic_keywords = []
        key_exchanges = []
        
        for msg in messages:
            if msg["role"] == "user":
                # Extract potential topics from user messages
                content = msg["content"].lower()
                if any(word in content for word in ["help", "learn", "teach", "explain"]):
                    key_exchanges.append(f"User requested help with: {msg['content'][:50]}...")
                elif "?" in content:
                    key_exchanges.append(f"User asked: {msg['content'][:50]}...")
        
        # Limit to most significant exchanges
        summary_parts = key_exchanges[:5]  # Keep top 5 exchanges
        
        if summary_parts:
            return "Key conversation topics: " + "; ".join(summary_parts)
        else:
            return f"Conversation covered {len(messages)} messages with various topics."
    
    def _extract_core_memories(self, messages: List[Dict]) -> Dict:
        """
        Extract core memories about user-character relationship
        
        Phase 2: Pattern-based extraction
        Phase 3: AI-powered relationship analysis
        """
        core_memories = {
            "user_learning_style": "Not yet determined",
            "relationship_dynamic": "Getting acquainted",
            "user_preferences": [],
            "emotional_context": "Neutral"
        }
        
        user_messages = [msg["content"].lower() for msg in messages if msg["role"] == "user"]
        assistant_messages = [msg["content"].lower() for msg in messages if msg["role"] == "assistant"]
        
        # Extract learning style indicators
        learning_indicators = []
        for msg in user_messages:
            if any(word in msg for word in ["visual", "diagram", "picture", "image"]):
                learning_indicators.append("visual learner")
            elif any(word in msg for word in ["example", "show me", "demonstrate"]):
                learning_indicators.append("visual learner")
            elif any(word in msg for word in ["step by step", "slowly", "explain", "detail"]):
                learning_indicators.append("methodical learner")
            elif "confused" in msg or "don't understand" in msg:
                learning_indicators.append("needs patience")
        
        if learning_indicators:
            core_memories["user_learning_style"] = ", ".join(set(learning_indicators))
        
        # Extract relationship progression
        if any("thank" in msg for msg in user_messages):
            core_memories["relationship_dynamic"] = "Appreciative student relationship"
        elif any("help" in msg for msg in user_messages):
            core_memories["relationship_dynamic"] = "Mentor-student dynamic"
        
        # Extract emotional context
        if any(word in " ".join(user_messages) for word in ["frustrated", "confused", "overwhelmed"]):
            core_memories["emotional_context"] = "Needs encouragement"
        elif any(word in " ".join(user_messages) for word in ["excited", "love", "enjoy", "great"]):
            core_memories["emotional_context"] = "Positive and engaged"
        
        return core_memories
    
    def _preserve_story_continuity(self, messages: List[Dict]) -> Dict:
        """
        Preserve story elements that define character development
        
        Phase 2: Pattern-based story element extraction
        Phase 3: AI-powered narrative analysis
        """
        story_continuity = {
            "character_development": "Standard teaching interactions",
            "user_progression": "Learning in progress",
            "emotional_journey": "Building rapport",
            "memorable_moments": []
        }
        
        # Track character development cues
        assistant_messages = [msg["content"] for msg in messages if msg["role"] == "assistant"]
        user_messages = [msg["content"] for msg in messages if msg["role"] == "user"]
        
        # Look for character personality evolution
        encouraging_responses = [msg for msg in assistant_messages if any(word in msg.lower() for word in ["great", "excellent", "proud", "wonderful"])]
        if len(encouraging_responses) > 2:
            story_continuity["character_development"] = "Becoming more encouraging and supportive"
        
        # Track user progression
        if len(user_messages) > 10:
            early_messages = user_messages[:5]
            recent_messages = user_messages[-5:]
            
            early_complexity = sum(len(msg.split()) for msg in early_messages) / len(early_messages)
            recent_complexity = sum(len(msg.split()) for msg in recent_messages) / len(recent_messages)
            
            if recent_complexity > early_complexity * 1.2:
                story_continuity["user_progression"] = "Growing confidence and complexity in questions"
        
        # Identify memorable moments
        memorable_moments = []
        for i, msg in enumerate(messages):
            if msg["role"] == "user" and any(word in msg["content"].lower() for word in ["first time", "finally", "success", "worked"]):
                memorable_moments.append(f"Breakthrough moment: {msg['content'][:50]}...")
            elif msg["role"] == "assistant" and "proud" in msg["content"].lower():
                memorable_moments.append(f"Encouragement: {msg['content'][:50]}...")
        
        story_continuity["memorable_moments"] = memorable_moments[:3]  # Keep top 3
        
        return story_continuity
    
    def _save_session(self, session_id: str, session_data: Dict):
        """
        Save session data to file system
        
        Args:
            session_id: ID of the session
            session_data: Complete session data to save
        """
        # Find the correct file path for this session
        session_file = None
        for user_dir in self.conversations_path.iterdir():
            if user_dir.is_dir():
                for char_dir in user_dir.iterdir():
                    if char_dir.is_dir():
                        potential_file = char_dir / f"{session_id}.json"
                        if potential_file.exists():
                            session_file = potential_file
                            break
                if session_file:
                    break
        
        if not session_file:
            raise ValueError(f"Session {session_id} file not found")
        
        # Update last_updated timestamp
        session_data["last_updated"] = datetime.now().isoformat()
        
        # Save updated session
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
    
    def get_ai_context(self, session_id: str, user_id: str) -> Dict:
        """
        Get conversation context for AI generation including compressed history
        
        Args:
            session_id: ID of the session
            user_id: ID of the user
            
        Returns:
            Dictionary with recent messages and compressed context
        """
        session = self.load_session_messages(session_id, user_id)
        
        context = {
            "recent_messages": session["messages"],  # Last 20 messages if compressed
            "compressed_summary": None,
            "core_memories": None
        }
        
        # Include compressed history if available
        if "compressed_history" in session:
            compressed = session["compressed_history"]
            context["compressed_summary"] = compressed.get("conversation_summary", "")
            context["core_memories"] = compressed.get("core_memories", {})
        
        return context
    
    def get_enhanced_ai_context(self, session_id: str, user_id: str) -> Dict:
        """
        Get enhanced conversation context for AI generation with compressed history
        
        This method provides a comprehensive context that includes:
        - Recent messages (last 20 if compressed)
        - Compressed conversation summary
        - Core memories about user preferences and relationship
        - Formatted context prompt for AI consumption
        
        Args:
            session_id: ID of the session
            user_id: ID of the user
            
        Returns:
            Dictionary with enhanced context including formatted prompt
        """
        session = self.load_session_messages(session_id, user_id)
        
        # Get basic AI context
        basic_context = self.get_ai_context(session_id, user_id)
        
        # Enhance with formatted context prompt
        enhanced_context = {
            "recent_messages": basic_context["recent_messages"],
            "compressed_summary": basic_context["compressed_summary"],
            "core_memories": basic_context["core_memories"],
            "context_prompt": self._format_context_prompt(
                basic_context["recent_messages"],
                basic_context["compressed_summary"],
                basic_context["core_memories"],
                session
            )
        }
        
        return enhanced_context
    
    def _format_context_prompt(self, recent_messages: List[Dict], compressed_summary: str, 
                              core_memories: Dict, session: Dict) -> str:
        """
        Format conversation context into a prompt for AI consumption with actual message history
        
        Args:
            recent_messages: List of recent message objects
            compressed_summary: Summary of older conversation
            core_memories: Core memories about user and relationship
            session: Full session data
            
        Returns:
            Formatted context prompt string with actual conversation history
        """
        prompt_parts = []
        
        # Add session overview
        prompt_parts.append("CONVERSATION CONTEXT:")
        prompt_parts.append(f"Session has {session.get('message_count', 0)} total messages.")
        
        # Add compressed history if available
        if compressed_summary and len(compressed_summary) > 0:
            prompt_parts.append("\nPrevious conversation summary:")
            prompt_parts.append(compressed_summary)
        
        # Add core memories if available (simplified for platform-agnostic approach)
        if core_memories and isinstance(core_memories, dict):
            prompt_parts.append("\nConversation context:")
            
            relationship = core_memories.get("relationship_dynamic", "")
            if relationship and relationship != "Getting acquainted":
                prompt_parts.append(f"- Relationship: {relationship}")
            
            emotional_context = core_memories.get("emotional_context", "")
            if emotional_context and emotional_context != "Neutral":
                prompt_parts.append(f"- Emotional context: {emotional_context}")
        
        # Add story continuity if available
        if "compressed_history" in session:
            story_continuity = session["compressed_history"].get("story_continuity", {})
            if isinstance(story_continuity, dict):
                char_dev = story_continuity.get("character_development", "")
                if char_dev and char_dev != "Standard teaching interactions":
                    prompt_parts.append(f"\nCharacter development: {char_dev}")
                
                user_prog = story_continuity.get("user_progression", "")
                if user_prog and user_prog != "Learning in progress":
                    prompt_parts.append(f"User progression: {user_prog}")
        
        # Add ACTUAL recent message history content
        if recent_messages and len(recent_messages) > 0:
            prompt_parts.append(f"\nRecent conversation history (last {len(recent_messages)} messages):")
            
            for msg in recent_messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if role == "user":
                    prompt_parts.append(f"User: {content}")
                elif role == "assistant":
                    prompt_parts.append(f"Assistant: {content}")
        
        # Add instruction for AI
        prompt_parts.append("\nBased on this context and conversation history, continue the conversation maintaining:")
        prompt_parts.append("- Consistency with previous interactions")
        prompt_parts.append("- Natural conversation flow from recent messages")
        prompt_parts.append("- Character personality and relationship development")
        
        return "\n".join(prompt_parts)