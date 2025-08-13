import { Character } from '@/types/character';

const CHARACTERS_KEY = 'voice_chat_characters';
const CURRENT_CHARACTER_KEY = 'current_character';

export class CharacterStorage {
  static getAll(): Character[] {
    if (typeof window === 'undefined') return [];
    const data = localStorage.getItem(CHARACTERS_KEY);
    return data ? JSON.parse(data) : [];
  }
  
  static getById(id: string): Character | null {
    const characters = this.getAll();
    return characters.find(c => c.id === id) || null;
  }
  
  static save(character: Character): void {
    if (typeof window === 'undefined') return;
    const characters = this.getAll();
    const index = characters.findIndex(c => c.id === character.id);
    
    character.updated_at = new Date();
    
    if (index >= 0) {
      characters[index] = character;
    } else {
      characters.push(character);
    }
    
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify(characters));
  }
  
  static delete(id: string): void {
    if (typeof window === 'undefined') return;
    const characters = this.getAll().filter(c => c.id !== id);
    localStorage.setItem(CHARACTERS_KEY, JSON.stringify(characters));
  }
  
  static async initializeDemo(): Promise<void> {
    if (typeof window === 'undefined') return;
    const existing = this.getAll();
    if (existing.length === 0) {
      try {
        const { DEMO_CHARACTERS } = await import('@/data/demo-characters');
        localStorage.setItem(CHARACTERS_KEY, JSON.stringify(DEMO_CHARACTERS));
      } catch (error) {
        console.warn('Failed to load demo characters:', error);
      }
    }
  }
}