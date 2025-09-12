import { ChatRequest, ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// New types for session and persona management
export interface SessionStartRequest {
  user_id: string;
  character_id: string;
  persona_id?: string;
}

export interface SessionStartResponse {
  success: boolean;
  data: {
    previous_sessions: Array<{
      session_id: string;
      message_count: number;
      last_message_pair: {
        user_message: string;
        assistant_message: string;
      };
      last_updated: string;
      created_at: string;
    }>;
    can_continue: boolean;
    active_persona_id: string | null;
    character_id: string;
    user_id: string;
  };
}

export interface SessionCreateResponse {
  success: boolean;
  data: {
    session: {
      session_id: string;
      user_id: string;
      character_id: string;
      persona_id: string;
      created_at: string;
      messages: any[];
      message_count: number;
    };
    persona_context: string;
  };
}

export interface SessionContinueResponse {
  success: boolean;
  data: {
    session: {
      session_id: string;
      messages: Array<{
        id: string;
        role: string;
        content: string;
        timestamp: string;
      }>;
      message_count: number;
    };
    persona_context: string;
    last_qa: {
      user_message: string;
      assistant_message: string;
    };
  };
}

export interface MessageProcessResponse {
  success: boolean;
  data: {
    user_message: string;
    relevant_knowledge: Array<{
      id: string;
      title: string;
      content: string;
      tags: string[];
    }>;
    persona_context: string;
    knowledge_ids: string[];
    session_id: string;
  };
}

export interface PersonaCreateRequest {
  user_id: string;
  name: string;
  description: string;
  attributes: Record<string, any>;
}

export interface PersonaResponse {
  success: boolean;
  persona: {
    id: string;
    name: string;
    description: string;
    attributes: Record<string, any>;
    created_at: string;
    is_active: boolean;
  };
}

export interface ChatWithSessionRequest {
  session_id?: string;
  user_id: string;
  character_id: string;
  persona_id?: string;
  message: string;
  character_prompt: string;
  voice_id?: string;
}

export interface ChatWithSessionResponse {
  character: string;
  dialogue: string;
  emotion: string;
  speed: number;
  audio?: string;
  session_id: string;
  message_count: number;
  session_summary?: string;
}

// NEW PLATFORM CHAT TYPES
export interface PlatformChatRequest {
  user_input: string;
  character_id: string;
  session_id?: string;
  user_id: string;
}

export interface PlatformTool {
  type: string;
  data: any;
}

export interface PlatformChatResponse {
  character: string;
  dialogue: string;
  tools: PlatformTool[];
  audio_url?: string;
  session_id: string;
  timestamp: string;
}

export class ApiClient {
  static async chat(request: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('API call failed:', error);
      // Fallback response for demo
      return {
        character: "Demo Character",
        dialogue: "죄송해요, 서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.",
        emotion: "neutral",
        speed: 1.0
      };
    }
  }

  static async chatWithSession(request: ChatWithSessionRequest): Promise<ChatWithSessionResponse> {
    try {
      // Convert old request format to new platform-chat format
      const platformRequest: PlatformChatRequest = {
        user_input: request.message,
        character_id: request.character_id,
        session_id: request.session_id,
        user_id: request.user_id
      };
      
      // Use the new platform-chat endpoint
      const platformResponse = await this.platformChat(platformRequest);
      
      // Convert platform response to expected ChatResponse format
      const convertedResponse: ChatWithSessionResponse = {
        character: platformResponse.character,
        dialogue: platformResponse.dialogue,
        emotion: "neutral", // Default emotion since platform-chat doesn't provide it
        speed: 1.0, // Default speed
        audio: platformResponse.audio_url || null, // Map audio_url to audio field
        session_id: platformResponse.session_id,
        tools: platformResponse.tools || []
      };
      
      return convertedResponse;
    } catch (error) {
      console.error('Chat with session API call failed:', error);
      // Fallback response for demo
      return {
        character: "Demo Character",
        dialogue: "죄송해요, 서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.",
        emotion: "neutral",
        speed: 1.0,
        session_id: "fallback_session",
        message_count: 0
      };
    }
  }

  static async speechToText(audioBase64: string, language: string = "ko-KR"): Promise<{ status: string; text: string; message?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio: audioBase64,
          language: language
        }),
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('STT API call failed:', error);
      return {
        status: "error",
        text: "",
        message: "Speech recognition failed"
      };
    }
  }

  static async textToSpeech(text: string, voice_id?: string, emotion?: string, character_id?: string): Promise<{ audio?: string; audio_base64?: string; status: string; message?: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice_id: voice_id,
          emotion: emotion || 'happy',
          character_id: character_id
        }),
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('TTS API call failed:', error);
      return {
        status: "error",
        message: "Text-to-speech generation failed"
      };
    }
  }

  // ============================================
  // NEW PLATFORM CHAT METHOD
  // ============================================

  static async platformChat(request: PlatformChatRequest): Promise<PlatformChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/platform-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Platform chat API call failed:', error);
      // Fallback response for demo
      return {
        character: request.character_id,
        dialogue: "죄송해요, 서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.",
        tools: [],
        session_id: "fallback_session",
        timestamp: new Date().toISOString()
      };
    }
  }

  // Create new session using platform orchestrator
  static async createPlatformSession(characterId: string, userId: string): Promise<PlatformChatResponse> {
    try {
      // Use the existing platform-chat endpoint with empty user_input to trigger greeting
      const response = await fetch(`${API_BASE_URL}/api/platform-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          user_input: '', // Empty input triggers greeting
          character_id: characterId, 
          user_id: userId 
          // No session_id - will create new session
        }),
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return response.json();
    } catch (error) {
      console.error('Create platform session failed:', error);
      // Fallback response
      return {
        character: characterId,
        dialogue: "안녕하세요! 서버 연결에 문제가 있어요. 잠시 후 다시 시도해주세요.",
        tools: [],
        session_id: "fallback_session",
        timestamp: new Date().toISOString()
      };
    }
  }

  // ============================================
  // NEW SESSION MANAGEMENT METHODS
  // ============================================

  static async startSession(request: SessionStartRequest): Promise<SessionStartResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Start session API call failed:', error);
      throw error;
    }
  }

  static async createSession(request: SessionStartRequest): Promise<SessionCreateResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Create session API call failed:', error);
      throw error;
    }
  }

  static async continueSession(session_id: string, user_id: string): Promise<SessionContinueResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/continue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id, user_id }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Continue session API call failed:', error);
      throw error;
    }
  }

  static async processMessage(session_id: string, user_id: string, message: string, character_id: string): Promise<MessageProcessResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ session_id, user_id, message, character_id }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Process message API call failed:', error);
      throw error;
    }
  }

  static async deleteSession(session_id: string, user_id: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sessions/${session_id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_id }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Delete session API call failed:', error);
      throw error;
    }
  }

  // ============================================
  // PERSONA MANAGEMENT METHODS
  // ============================================

  static async createPersona(request: PersonaCreateRequest): Promise<PersonaResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Create persona API call failed:', error);
      throw error;
    }
  }

  static async activatePersona(user_id: string, persona_id: string): Promise<any> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/activate?user_id=${user_id}&persona_id=${persona_id}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Activate persona API call failed:', error);
      throw error;
    }
  }

  static async getActivePersona(user_id: string): Promise<PersonaResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${user_id}/active`, {
        method: 'GET',
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Get active persona API call failed:', error);
      throw error;
    }
  }

  static async getUserPersonas(user_id: string): Promise<{ success: boolean; personas: any[] }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${user_id}`, {
        method: 'GET',
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Get user personas API call failed:', error);
      throw error;
    }
  }

  static async updatePersona(persona_id: string, request: PersonaCreateRequest): Promise<PersonaResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${persona_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Update persona API call failed:', error);
      throw error;
    }
  }

  static async deletePersona(user_id: string, persona_id: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/personas/${user_id}/${persona_id}`, {
        method: 'DELETE',
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Delete persona API call failed:', error);
      throw error;
    }
  }

  // Knowledge Management API Methods
  static async getCharacterKnowledge(character_id: string): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/characters/${character_id}/knowledge`, {
        method: 'GET',
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Get character knowledge API call failed:', error);
      throw error;
    }
  }

  static async createKnowledgeItem(character_id: string, knowledge_item: any): Promise<{ success: boolean; knowledge_id: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/characters/${character_id}/knowledge`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(knowledge_item),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Create knowledge item API call failed:', error);
      throw error;
    }
  }

  static async updateKnowledgeItem(knowledge_id: string, character_id: string, update_data: any): Promise<{ success: boolean }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/knowledge/${knowledge_id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ character_id, ...update_data }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Update knowledge item API call failed:', error);
      throw error;
    }
  }

  static async deleteKnowledgeItem(knowledge_id: string, character_id: string): Promise<{ success: boolean }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/knowledge/${knowledge_id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ character_id }),
        mode: 'cors',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      console.error('Delete knowledge item API call failed:', error);
      throw error;
    }
  }
}