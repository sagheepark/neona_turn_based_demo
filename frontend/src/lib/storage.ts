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
  
  static async initializeDemo(forceRefresh: boolean = false): Promise<void> {
    if (typeof window === 'undefined') return;
    const existing = this.getAll();
    
    // Force refresh or initialize if empty
    if (forceRefresh || existing.length === 0) {
      try {
        const { DEMO_CHARACTERS } = await import('@/data/demo-characters');
        localStorage.setItem(CHARACTERS_KEY, JSON.stringify(DEMO_CHARACTERS));
      } catch (error) {
        console.warn('Failed to load demo characters:', error);
      }
    } else {
      // Smart update: sync demo character updates while preserving user edits
      await this.syncDemoCharacterUpdates();
    }
  }

  static async syncDemoCharacterUpdates(): Promise<void> {
    if (typeof window === 'undefined') return;
    
    try {
      const { DEMO_CHARACTERS } = await import('@/data/demo-characters');
      const existing = this.getAll();
      let hasUpdates = false;
      
      // Update each demo character if it exists in localStorage
      for (const demoChar of DEMO_CHARACTERS) {
        const existingIndex = existing.findIndex(c => c.id === demoChar.id);
        if (existingIndex >= 0) {
          const existingChar = existing[existingIndex];
          
          // Check if core demo properties need updating (name, description, etc.)
          // Only update if the existing character hasn't been significantly modified by user
          const isUserModified = existingChar.updated_at && 
            existingChar.updated_at.getTime() > (existingChar.created_at?.getTime() || 0);
          
          if (!isUserModified || this.shouldForceUpdate(demoChar, existingChar)) {
            // Update core properties while preserving user modifications
            existing[existingIndex] = {
              ...existingChar,
              name: demoChar.name,
              description: demoChar.description,
              image: demoChar.image || existingChar.image,
              // Preserve user edits to prompt, greetings, etc.
              updated_at: new Date()
            };
            hasUpdates = true;
          }
        }
      }
      
      if (hasUpdates) {
        localStorage.setItem(CHARACTERS_KEY, JSON.stringify(existing));
      }
    } catch (error) {
      console.warn('Failed to sync demo character updates:', error);
    }
  }

  private static shouldForceUpdate(demoChar: Character, existingChar: Character): boolean {
    // Force update if core display properties have changed in demo file
    return demoChar.name !== existingChar.name || 
           demoChar.description !== existingChar.description;
  }
  
  static refreshDemoCharacters(): void {
    // Force refresh demo characters from the latest data
    this.initializeDemo(true);
  }
}