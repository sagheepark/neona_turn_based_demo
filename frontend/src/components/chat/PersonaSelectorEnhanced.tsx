'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { User, Plus, Settings, UserCheck, Edit, Trash2, Users, X } from 'lucide-react'
import { PersonaCreateRequest, PersonaResponse, ApiClient } from '@/lib/api-client'

interface PersonaSelectorProps {
  currentPersona?: PersonaResponse['persona'] | null;
  onPersonaCreate: (persona: PersonaCreateRequest) => Promise<void>;
  onPersonaSelect: (personaId: string) => Promise<void>;
  className?: string;
}

export function PersonaSelectorEnhanced({ 
  currentPersona, 
  onPersonaCreate, 
  onPersonaSelect,
  className = '' 
}: PersonaSelectorProps) {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [showPersonaList, setShowPersonaList] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editingPersona, setEditingPersona] = useState<any>(null)
  const [allPersonas, setAllPersonas] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
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

  const userId = 'demo_user' // In real app, get from auth

  const loadAllPersonas = async () => {
    setIsLoading(true)
    try {
      const response = await ApiClient.getUserPersonas(userId)
      if (response.success) {
        setAllPersonas(response.personas)
      }
    } catch (error) {
      console.error('Failed to load personas:', error)
      setAllPersonas([])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (showPersonaList) {
      loadAllPersonas()
    }
  }, [showPersonaList])

  const handleCreate = async () => {
    if (!formData.name.trim() || !formData.description.trim()) {
      return
    }

    if (isEditing && editingPersona) {
      setIsCreating(true)
      try {
        const personaRequest: PersonaCreateRequest = {
          user_id: userId,
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

        await ApiClient.updatePersona(editingPersona.id, personaRequest)
        
        // Reset form
        resetForm()
        await loadAllPersonas() // Refresh persona list
      } catch (error) {
        console.error('Failed to update persona:', error)
      } finally {
        setIsCreating(false)
      }
    } else {
      setIsCreating(true)
      try {
        const personaRequest: PersonaCreateRequest = {
          user_id: userId,
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
        resetForm()
        if (showPersonaList) {
          await loadAllPersonas() // Refresh persona list if showing
        }
      } catch (error) {
        console.error('Failed to create persona:', error)
      } finally {
        setIsCreating(false)
      }
    }
  }

  const resetForm = () => {
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
    setIsEditing(false)
    setEditingPersona(null)
  }

  const handleEdit = (persona: any) => {
    setEditingPersona(persona)
    setIsEditing(true)
    setFormData({
      name: persona.name || '',
      description: persona.description || '',
      age: persona.attributes?.age || '',
      occupation: persona.attributes?.occupation || '',
      personality: persona.attributes?.personality || '',
      interests: Array.isArray(persona.attributes?.interests) ? persona.attributes.interests.join(', ') : '',
      speaking_style: persona.attributes?.speaking_style || '',
      background: persona.attributes?.background || ''
    })
    setShowCreateForm(true)
    setShowPersonaList(false)
  }

  const handleDelete = async (persona: any) => {
    if (!confirm(`"${persona.name}" 페르소나를 삭제하시겠습니까?`)) {
      return
    }

    try {
      await ApiClient.deletePersona(userId, persona.id)
      await loadAllPersonas() // Refresh persona list
    } catch (error) {
      console.error('Failed to delete persona:', error)
    }
  }

  const handlePersonaSelect = async (personaId: string) => {
    await onPersonaSelect(personaId)
    setShowPersonaList(false)
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

      {/* Action Buttons */}
      {!showCreateForm && !showPersonaList && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex gap-2"
        >
          <Button
            variant="outline"
            onClick={() => setShowCreateForm(true)}
            className="flex-1 border-blue-200 text-blue-700 hover:bg-blue-50"
          >
            <Plus className="w-4 h-4 mr-2" />
            새 페르소나 만들기
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowPersonaList(true)}
            className="flex-1 border-purple-200 text-purple-700 hover:bg-purple-50"
          >
            <Users className="w-4 h-4 mr-2" />
            페르소나 관리
          </Button>
        </motion.div>
      )}

      {/* Persona List */}
      <AnimatePresence>
        {showPersonaList && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <Card className="border-purple-200">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Users className="w-5 h-5 text-purple-600" />
                    <CardTitle className="text-purple-900">페르소나 목록</CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setShowPersonaList(false)}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <CardDescription>
                  저장된 페르소나를 선택, 편집 또는 삭제할 수 있습니다
                </CardDescription>
              </CardHeader>
              <CardContent>
                {isLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center space-y-2">
                      <div className="w-6 h-6 border-2 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
                      <p className="text-sm text-muted-foreground">페르소나 목록을 불러오고 있습니다...</p>
                    </div>
                  </div>
                ) : allPersonas.length > 0 ? (
                  <div className="space-y-2">
                    {allPersonas.map((persona) => (
                      <Card key={persona.id} className={`transition-all ${persona.is_active ? 'border-green-200 bg-green-50' : 'hover:border-gray-300'}`}>
                        <CardContent className="p-3">
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h4 className="font-semibold">{persona.name}</h4>
                                {persona.is_active && (
                                  <UserCheck className="w-4 h-4 text-green-600" />
                                )}
                              </div>
                              <p className="text-sm text-gray-600 mt-1">{persona.description}</p>
                            </div>
                            <div className="flex gap-1">
                              {!persona.is_active && (
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => handlePersonaSelect(persona.id)}
                                  className="h-8 px-2 text-blue-600 hover:bg-blue-50"
                                >
                                  선택
                                </Button>
                              )}
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleEdit(persona)}
                                className="h-8 px-2 text-amber-600 hover:bg-amber-50"
                              >
                                <Edit className="w-3 h-3" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDelete(persona)}
                                className="h-8 px-2 text-red-600 hover:bg-red-50"
                              >
                                <Trash2 className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Users className="w-12 h-12 mx-auto mb-2 text-gray-300" />
                    <p>저장된 페르소나가 없습니다</p>
                    <p className="text-sm">새 페르소나를 만들어보세요</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create/Edit Persona Form */}
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
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <User className="w-5 h-5 text-blue-600" />
                    <CardTitle className="text-blue-900">
                      {isEditing ? '페르소나 편집' : '새 페르소나 만들기'}
                    </CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={resetForm}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
                <CardDescription>
                  {isEditing ? '페르소나 정보를 수정하세요' : '대화에서 사용할 성격을 만들어보세요'}
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
                        {isEditing ? '수정 중...' : '생성 중...'}
                      </>
                    ) : (
                      <>
                        {isEditing ? <Edit className="w-4 h-4 mr-2" /> : <Plus className="w-4 h-4 mr-2" />}
                        {isEditing ? '페르소나 수정' : '페르소나 생성'}
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={resetForm}
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