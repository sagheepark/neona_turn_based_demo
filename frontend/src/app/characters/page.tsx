'use client'

import { useEffect, useState } from 'react'
import { Plus } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { Card, CardContent } from '@/components/ui/card'
import { CharacterCard } from '@/components/characters/CharacterCard'
import { PersonaManagementModal } from '@/components/characters/PersonaManagementModal'
import { CharacterStorage } from '@/lib/storage'
import { Character } from '@/types/character'
import { KnowledgeManagementSection } from '@/components/knowledge/KnowledgeManagementSection'
import { ApiClient } from '@/lib/api-client'

export default function CharactersPage() {
  const [characters, setCharacters] = useState<Character[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedCharacterForPersona, setSelectedCharacterForPersona] = useState<Character | null>(null)
  const [editingCharacter, setEditingCharacter] = useState<Character | null>(null)
  const [knowledgeItems, setKnowledgeItems] = useState<any[]>([])
  const router = useRouter()
  
  useEffect(() => {
    const loadCharacters = async () => {
      await CharacterStorage.initializeDemo()
      setCharacters(CharacterStorage.getAll())
      setLoading(false)
    }
    loadCharacters()
  }, [])

  const getCharacterKnowledge = async (characterId: string) => {
    try {
      const knowledge = await ApiClient.getCharacterKnowledge(characterId)
      setKnowledgeItems(knowledge)
    } catch (error) {
      console.error('Failed to fetch character knowledge:', error)
      setKnowledgeItems([])
    }
  }

  const handleKnowledgeChange = async (items: any[]) => {
    setKnowledgeItems(items)
    if (editingCharacter) {
      // Save knowledge items for the character
      for (const item of items) {
        if (item.id?.startsWith('temp_')) {
          // Create new item
          await createKnowledgeItem(editingCharacter.id, item)
        } else {
          // Update existing item
          await ApiClient.updateKnowledgeItem(item.id, editingCharacter.id, item)
        }
      }
    }
  }

  const createKnowledgeItem = async (characterId: string, item: any) => {
    try {
      await ApiClient.createKnowledgeItem(characterId, item)
    } catch (error) {
      console.error('Failed to create knowledge item:', error)
    }
  }
  
  if (loading) {
    return (
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="flex items-center justify-center min-h-[200px]">
          <div className="text-lg">Loading characters...</div>
        </div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Voice Character Chat</h1>
        <p className="text-muted-foreground">Select a character to start chatting</p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {characters.map(character => (
          <CharacterCard
            key={character.id}
            character={character}
            onClick={() => router.push(`/chat/${character.id}`)}
            onEdit={() => router.push(`/characters/${character.id}/edit`)}
            onDelete={() => {
              CharacterStorage.delete(character.id)
              setCharacters(CharacterStorage.getAll())
            }}
            onPersona={() => setSelectedCharacterForPersona(character)}
          />
        ))}
        
        <Card 
          className="border-dashed border-2 cursor-pointer hover:border-primary transition-colors"
          onClick={() => router.push('/characters/create')}
        >
          <CardContent className="flex flex-col items-center justify-center h-48">
            <Plus className="w-12 h-12 mb-2 text-muted-foreground" />
            <span className="text-muted-foreground">Create New Character</span>
          </CardContent>
        </Card>
      </div>

      {/* Persona Management Modal */}
      {selectedCharacterForPersona && (
        <PersonaManagementModal
          isOpen={!!selectedCharacterForPersona}
          onClose={() => setSelectedCharacterForPersona(null)}
          character={selectedCharacterForPersona}
        />
      )}
    </div>
  )
}