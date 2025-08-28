'use client'

import { useParams, useRouter } from 'next/navigation'
import { useState, useEffect } from 'react'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SelectiveConfigEditor } from '@/components/characters/SelectiveConfigEditor'
import { CharacterStorage } from '@/lib/storage'
import { Character } from '@/types/character'

export default function CharacterSimulationPage() {
  const params = useParams()
  const router = useRouter()
  const characterId = params.id as string
  const [character, setCharacter] = useState<Character | null>(null)

  useEffect(() => {
    const loadCharacter = async () => {
      await CharacterStorage.initializeDemo()
      const char = CharacterStorage.getById(characterId)
      setCharacter(char || null)
    }
    loadCharacter()
  }, [characterId])

  if (!character) {
    return (
      <div className="container mx-auto p-4 max-w-4xl">
        <div className="text-center py-8">
          <p className="text-muted-foreground">Character not found</p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={() => router.push('/characters')}
          >
            Back to Characters
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push('/characters')}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Characters
        </Button>
        
        <h1 className="text-2xl font-bold">Simulation Configuration</h1>
        <p className="text-muted-foreground mt-2">
          Configure status values, milestones, and memory settings for {character.name}
        </p>
      </div>

      <SelectiveConfigEditor 
        characterId={characterId}
        characterName={character.name}
      />
    </div>
  )
}