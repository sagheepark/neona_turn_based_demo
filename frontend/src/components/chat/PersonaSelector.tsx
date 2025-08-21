'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { User, Plus, Settings, UserCheck } from 'lucide-react'
import { PersonaCreateRequest, PersonaResponse } from '@/lib/api-client'

interface PersonaSelectorProps {
  currentPersona?: PersonaResponse['persona'] | null;
  onPersonaCreate: (persona: PersonaCreateRequest) => Promise<void>;
  onPersonaSelect: (personaId: string) => Promise<void>;
  className?: string;
}

export function PersonaSelector({ 
  currentPersona, 
  onPersonaCreate, 
  onPersonaSelect,
  className = '' 
}: PersonaSelectorProps) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    age: '',
    occupation: '',
    personality: '',
    interests: '',
    speaking_style: '',
    background: ''
  })

  const handleCreate = async () => {
    if (!formData.name.trim() || !formData.description.trim()) {
      return
    }

    setIsCreating(true)
    try {
      const personaRequest: PersonaCreateRequest = {
        user_id: 'demo_user', // In real app, get from auth
        name: formData.name,
        description: formData.description,
        attributes: {
          age: formData.age,
          occupation: formData.occupation,
          personality: formData.personality,
          interests: formData.interests.split(',').map(i => i.trim()).filter(Boolean),
          speaking_style: formData.speaking_style,
          background: formData.background
        }
      }

      await onPersonaCreate(personaRequest)
      
      // Reset form
      setFormData({
        name: '',
        description: '',
        age: '',
        occupation: '',
        personality: '',
        interests: '',
        speaking_style: '',
        background: ''
      })
      setShowCreateForm(false)
    } catch (error) {
      console.error('Failed to create persona:', error)
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Current Persona Display */}
      {currentPersona && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card className="border-green-200 bg-green-50">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-green-600" />
                <CardTitle className="text-sm font-medium text-green-900">
                  활성 페르소나
                </CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <h3 className="font-semibold text-green-900">{currentPersona.name}</h3>
                <p className="text-sm text-green-700">{currentPersona.description}</p>
                
                {currentPersona.attributes && Object.keys(currentPersona.attributes).length > 0 && (
                  <div className="grid grid-cols-2 gap-2 mt-3 text-xs">
                    {Object.entries(currentPersona.attributes).map(([key, value]) => (
                      <div key={key} className="bg-white rounded p-2">
                        <span className="font-medium text-gray-600 capitalize">
                          {key.replace('_', ' ')}:
                        </span>
                        <span className="ml-1 text-gray-800">
                          {Array.isArray(value) ? value.join(', ') : String(value)}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Create New Persona Button */}
      {!showCreateForm && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Button
            variant="outline"
            onClick={() => setShowCreateForm(true)}
            className="w-full border-blue-200 text-blue-700 hover:bg-blue-50"
          >
            <Plus className="w-4 h-4 mr-2" />
            새 페르소나 만들기
          </Button>
        </motion.div>
      )}

      {/* Create Persona Form */}
      <AnimatePresence>
        {showCreateForm && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <Card className="border-blue-200">
              <CardHeader>
                <div className="flex items-center gap-2">
                  <User className="w-5 h-5 text-blue-600" />
                  <CardTitle className="text-blue-900">새 페르소나 만들기</CardTitle>
                </div>
                <CardDescription>
                  대화에서 사용할 성격을 만들어보세요
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">이름 *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="예: 호기심 많은 학생"
                    />
                  </div>
                  <div>
                    <Label htmlFor="age">나이</Label>
                    <Input
                      id="age"
                      value={formData.age}
                      onChange={(e) => setFormData(prev => ({ ...prev, age: e.target.value }))}
                      placeholder="예: 22세"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">설명 *</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="이 페르소나에 대한 간단한 설명을 입력하세요"
                    rows={2}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="occupation">직업/상황</Label>
                    <Input
                      id="occupation"
                      value={formData.occupation}
                      onChange={(e) => setFormData(prev => ({ ...prev, occupation: e.target.value }))}
                      placeholder="예: 대학생, 직장인"
                    />
                  </div>
                  <div>
                    <Label htmlFor="speaking_style">말하는 방식</Label>
                    <Input
                      id="speaking_style"
                      value={formData.speaking_style}
                      onChange={(e) => setFormData(prev => ({ ...prev, speaking_style: e.target.value }))}
                      placeholder="예: 존댓말, 친근하게"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="personality">성격</Label>
                  <Input
                    id="personality"
                    value={formData.personality}
                    onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
                    placeholder="예: 호기심 많음, 꼼꼼함, 활발함"
                  />
                </div>

                <div>
                  <Label htmlFor="interests">관심사 (쉼표로 구분)</Label>
                  <Input
                    id="interests"
                    value={formData.interests}
                    onChange={(e) => setFormData(prev => ({ ...prev, interests: e.target.value }))}
                    placeholder="예: 프로그래밍, 게임, 음악"
                  />
                </div>

                <div>
                  <Label htmlFor="background">배경/상황</Label>
                  <Textarea
                    id="background"
                    value={formData.background}
                    onChange={(e) => setFormData(prev => ({ ...prev, background: e.target.value }))}
                    placeholder="현재 상황이나 배경에 대해 설명해주세요"
                    rows={2}
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button
                    onClick={handleCreate}
                    disabled={!formData.name.trim() || !formData.description.trim() || isCreating}
                    className="flex-1"
                  >
                    {isCreating ? (
                      <>
                        <Settings className="w-4 h-4 mr-2 animate-spin" />
                        생성 중...
                      </>
                    ) : (
                      <>
                        <Plus className="w-4 h-4 mr-2" />
                        페르소나 생성
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => setShowCreateForm(false)}
                    disabled={isCreating}
                  >
                    취소
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}