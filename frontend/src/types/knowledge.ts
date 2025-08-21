/**
 * TypeScript types for Knowledge Management
 * Minimal implementation for TDD GREEN phase
 */

export interface KnowledgeItem {
  id: string;
  title: string;
  content: string;
  keywords: string[];
  category: string;
  created_at?: string;
  updated_at?: string;
}

export interface KnowledgeItemCreate {
  title: string;
  content: string;
  keywords: string[] | string; // Accept both formats
  category: string;
}

export interface CharacterKnowledge {
  character_id: string;
  knowledge_items: KnowledgeItem[];
  total_items?: number;
}

// API Response types
export interface KnowledgeCreateResponse {
  success: boolean;
  knowledge_id: string;
}

export interface KnowledgeUpdateResponse {
  success: boolean;
}

export interface KnowledgeDeleteResponse {
  success: boolean;
}