export interface Character {
  id: string;
  name: string;
  description: string;
  image: string;  // base64 또는 URL
  prompt: string;  // 캐릭터 프롬프트 (태그 포함)
  voice_id: string;
  created_at: Date;
  updated_at: Date;
}