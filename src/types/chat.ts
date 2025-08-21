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
}

export interface ChatResponse {
  character: string;
  dialogue: string;
  emotion: string;
  speed: number;
}