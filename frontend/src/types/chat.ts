export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatRequest {
  message: string;
  character_prompt: string;
  history: ChatMessage[];
  character_id: string;
  voice_id?: string;
}

export interface ChatResponse {
  character: string;
  dialogue: string;
  emotion: string;
  speed: number;
  audio?: string;  // base64 encoded audio data
  // Session-related fields
  session_id?: string;
  message_count?: number;
  session_summary?: string;
  // Tool-based interactions
  tools?: Array<{
    type: string;
    data: any;
  }>;
}