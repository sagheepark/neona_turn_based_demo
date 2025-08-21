'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { PersonaSelectorEnhanced } from '@/components/chat/PersonaSelectorEnhanced'
import { ApiClient, PersonaCreateRequest, PersonaResponse } from '@/lib/api-client'
import { Character } from '@/types/character'

interface PersonaManagementModalProps {
  isOpen: boolean;
  onClose: () => void;
  character: Character;
}

export function PersonaManagementModal({ 
  isOpen,
  onClose,
  character
}: PersonaManagementModalProps) {
  const [currentPersona, setCurrentPersona] = useState<PersonaResponse['persona'] | null>(null)
  const [loading, setLoading] = useState(false)
  
  const userId = 'demo_user' // In real app, get from auth

  // Load current active persona when modal opens
  useEffect(() => {
    if (isOpen) {
      loadCurrentPersona()
    }
  }, [isOpen])

  const loadCurrentPersona = async () => {
    setLoading(true)
    try {
      const response = await ApiClient.getActivePersona(userId)
      if (response.success && response.persona) {
        setCurrentPersona(response.persona)
      }
    } catch (error) {
      console.log('No active persona found')
      setCurrentPersona(null)
    } finally {
      setLoading(false)
    }
  }

  const handlePersonaCreate = async (personaRequest: PersonaCreateRequest) => {
    try {
      const response = await ApiClient.createPersona(personaRequest)
      if (response.success) {
        // Activate the new persona
        await ApiClient.activatePersona(userId, response.persona.id)
        setCurrentPersona(response.persona)
      }
    } catch (error) {
      console.error('Failed to create persona:', error)
    }
  }

  const handlePersonaSelect = async (personaId: string) => {
    try {
      await ApiClient.activatePersona(userId, personaId)
      // Refresh persona data
      const response = await ApiClient.getActivePersona(userId)
      if (response.success) {
        setCurrentPersona(response.persona)
      }
    } catch (error) {
      console.error('Failed to activate persona:', error)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            페르소나 관리 - {character.name}
          </DialogTitle>
          <DialogDescription>
            {character.name}와의 대화에서 사용할 페르소나를 관리하세요. 
            페르소나는 대화 스타일과 맥락을 결정합니다.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="text-center space-y-2">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-sm text-muted-foreground">페르소나 정보를 불러오고 있습니다...</p>
              </div>
            </div>
          ) : (
            <PersonaSelectorEnhanced
              currentPersona={currentPersona}
              onPersonaCreate={handlePersonaCreate}
              onPersonaSelect={handlePersonaSelect}
            />
          )}

          <div className="flex justify-end pt-4 border-t">
            <Button onClick={onClose}>
              완료
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}