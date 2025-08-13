import { ChatRequest, ChatResponse } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
}