'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Collapsible } from '@/components/ui/collapsible'
import { ScrollArea } from '@/components/ui/scroll-area'
import { CharacterStorage } from '@/lib/storage'
import { Character } from '@/types/character'
import { ArrowLeft, Plus, X, MessageSquare, Brain, Settings } from 'lucide-react'
import VoiceSelector from '@/components/characters/VoiceSelector'
import VoiceRecommendation from '@/components/characters/VoiceRecommendation'
import { KnowledgeManagementSection } from '@/components/knowledge'

export default function CreateCharacterPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [knowledgeItems, setKnowledgeItems] = useState<any[]>([])
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    image: '',
    voice_id: 'default_voice_001',
    prompt: '',
    greetings: [''],
    conversation_examples: ['']
  })
  
  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = () => {
        setFormData(prev => ({ ...prev, image: reader.result as string }))
      }
      reader.readAsDataURL(file)
    }
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.voice_id || formData.voice_id.trim() === '') {
      alert('Please select a voice for your character.')
      return
    }
    
    setLoading(true)
    
    try {
      const character: Character = {
        id: `char_${Date.now()}`,
        name: formData.name,
        description: formData.description,
        image: formData.image || '/characters/default.png',
        prompt: formData.prompt,
        greetings: formData.greetings.filter(g => g.trim() !== ''),
        conversation_examples: formData.conversation_examples.filter(ex => ex.trim() !== ''),
        voice_id: formData.voice_id || 'default_voice_001',
        created_at: new Date(),
        updated_at: new Date()
      }
      
      CharacterStorage.save(character)
      router.push('/characters')
    } catch (error) {
      console.error('Error creating character:', error)
    } finally {
      setLoading(false)
    }
  }
  
  const addGreeting = () => {
    setFormData(prev => ({ ...prev, greetings: [...prev.greetings, ''] }))
  }
  
  const removeGreeting = (index: number) => {
    if (formData.greetings.length > 1) {
      const newGreetings = formData.greetings.filter((_, i) => i !== index)
      setFormData(prev => ({ ...prev, greetings: newGreetings }))
    }
  }
  
  const updateGreeting = (index: number, value: string) => {
    const newGreetings = [...formData.greetings]
    newGreetings[index] = value
    setFormData(prev => ({ ...prev, greetings: newGreetings }))
  }
  
  const addExample = () => {
    setFormData(prev => ({ ...prev, conversation_examples: [...prev.conversation_examples, ''] }))
  }
  
  const removeExample = (index: number) => {
    if (formData.conversation_examples.length > 1) {
      const newExamples = formData.conversation_examples.filter((_, i) => i !== index)
      setFormData(prev => ({ ...prev, conversation_examples: newExamples }))
    }
  }
  
  const updateExample = (index: number, value: string) => {
    const newExamples = [...formData.conversation_examples]
    newExamples[index] = value
    setFormData(prev => ({ ...prev, conversation_examples: newExamples }))
  }
  
  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Create New Character</h1>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <Tabs defaultValue="basic" className="space-y-4">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="basic" className="flex items-center gap-2">
              <Settings className="w-4 h-4" />
              Basic Info
            </TabsTrigger>
            <TabsTrigger value="prompt" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Character
            </TabsTrigger>
            <TabsTrigger value="examples" className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Examples
            </TabsTrigger>
            <TabsTrigger value="knowledge" className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Knowledge
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="basic" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Character Name *</Label>
                    <Input
                      id="name"
                      value={formData.name}
                      onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                      required
                      placeholder="e.g. Taylor"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="voice_id">Voice Selection *</Label>
                    <VoiceSelector
                      selectedVoiceId={formData.voice_id}
                      onSelect={(voiceId) => setFormData(prev => ({ ...prev, voice_id: voiceId }))}
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="description">Short Description *</Label>
                  <Input
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                    required
                    placeholder="e.g. Friendly math tutor"
                  />
                </div>
                
                <div>
                  <Label htmlFor="image">Character Image</Label>
                  <Input
                    id="image"
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                  />
                  {formData.image && (
                    <img 
                      src={formData.image} 
                      alt="Preview" 
                      className="mt-2 w-32 h-32 object-cover rounded"
                    />
                  )}
                </div>
                
                <VoiceRecommendation
                  characterName={formData.name}
                  characterDescription={formData.description}
                  characterPersonality={formData.prompt}
                  onSelectVoice={(voiceId) => setFormData(prev => ({ ...prev, voice_id: voiceId }))}
                  currentVoiceId={formData.voice_id}
                />
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="prompt" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Character System Prompt</CardTitle>
              </CardHeader>
              <CardContent>
                <div>
                  <Label htmlFor="prompt">Complete Character Prompt *</Label>
                  <Textarea
                    id="prompt"
                    value={formData.prompt}
                    onChange={(e) => setFormData(prev => ({ ...prev, prompt: e.target.value }))}
                    required
                    rows={20}
                    className="font-mono text-sm"
                    placeholder={`Enter the complete character prompt with XML structure, e.g.:

<persona>
<basic_information>
<character_name>Your Character Name</character_name>
<gender>Male/Female</gender>
<age>25</age>
<role>Character Role</role>
</basic_information>

<narrative_psychology>
<personality>Character personality traits and behavior...</personality>
<speaking_style>How the character speaks and communicates...</speaking_style>
<backstory>Character's background story...</backstory>
<scenario>Context where conversations take place...</scenario>
</narrative_psychology>
</persona>

You can use XML, JSON, or any structured format.`}
                  />
                  <p className="text-sm text-muted-foreground mt-2">
                    Create a comprehensive system prompt for your character. Use XML tags, JSON, or any structured format.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="examples" className="space-y-4">
            <div className="space-y-4">
              {/* Greetings Section */}
              <Collapsible title="Initial Greetings" defaultOpen>
                <ScrollArea className="h-80 pr-4">
                  <div className="space-y-3">
                    {formData.greetings.map((greeting, index) => (
                      <div key={index} className="flex gap-2">
                        <Textarea
                          value={greeting}
                          onChange={(e) => updateGreeting(index, e.target.value)}
                          placeholder={`Greeting ${index + 1}`}
                          rows={2}
                          className="flex-1"
                        />
                        {formData.greetings.length > 1 && (
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={() => removeGreeting(index)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={addGreeting}
                      className="w-full"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Greeting
                    </Button>
                  </div>
                </ScrollArea>
                <p className="text-sm text-muted-foreground mt-2">
                  Character will randomly select one greeting when starting a new chat.
                </p>
              </Collapsible>
              
              {/* Conversation Examples Section */}
              <Collapsible title="Conversation Examples" defaultOpen>
                <ScrollArea className="h-80 pr-4">
                  <div className="space-y-3">
                    {formData.conversation_examples.map((example, index) => (
                      <div key={index} className="flex gap-2">
                        <Textarea
                          value={example}
                          onChange={(e) => updateExample(index, e.target.value)}
                          placeholder={`Example ${index + 1}:\\nUser: [User message]\\n${formData.name || 'Character'}: [Character response]`}
                          rows={4}
                          className="flex-1 font-mono text-sm"
                        />
                        {formData.conversation_examples.length > 1 && (
                          <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={() => removeExample(index)}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={addExample}
                      className="w-full"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Add Example
                    </Button>
                  </div>
                </ScrollArea>
                <p className="text-sm text-muted-foreground mt-2">
                  Example conversations demonstrating the character's speaking style and behavior.
                </p>
              </Collapsible>
            </div>
          </TabsContent>
          
          <TabsContent value="knowledge" className="space-y-4">
            <KnowledgeManagementSection
              characterId={undefined}
              knowledgeItems={knowledgeItems}
              onKnowledgeChange={setKnowledgeItems}
            />
          </TabsContent>
        </Tabs>
        
        <div className="flex gap-4 pt-6 border-t">
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Character'}
          </Button>
          <Button 
            type="button" 
            variant="outline"
            onClick={() => router.push('/characters')}
            disabled={loading}
          >
            Cancel
          </Button>
        </div>
      </form>
    </div>
  )
}