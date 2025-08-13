'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CharacterStorage } from '@/lib/storage'
import { Character } from '@/types/character'
import { ArrowLeft } from 'lucide-react'
import VoiceSelector from '@/components/characters/VoiceSelector'
import VoiceRecommendation from '@/components/characters/VoiceRecommendation'

export default function EditCharacterPage() {
  const params = useParams()
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [character, setCharacter] = useState<Character | null>(null)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    image: '',
    voice_id: '',
    personality: '',
    speaking_style: '',
    age: '',
    gender: '',
    role: '',
    backstory: '',
    scenario: ''
  })
  
  useEffect(() => {
    const characterId = params.id as string
    const char = CharacterStorage.getById(characterId)
    
    if (!char) {
      router.push('/characters')
      return
    }
    
    setCharacter(char)
    
    // Parse character prompt to extract data
    const parsePrompt = (prompt: string) => {
      const patterns = {
        personality: /<personality>(.*?)<\/personality>/s,
        speaking_style: /<speaking_style>(.*?)<\/speaking_style>/s,
        age: /<age>(.*?)<\/age>/s,
        gender: /<gender>(.*?)<\/gender>/s,
        role: /<role>(.*?)<\/role>/s,
        backstory: /<backstory>(.*?)<\/backstory>/s,
        scenario: /<scenario>(.*?)<\/scenario>/s
      }
      
      const extracted: any = {}
      Object.entries(patterns).forEach(([key, pattern]) => {
        const match = prompt.match(pattern)
        extracted[key] = match ? match[1].trim() : ''
      })
      
      return extracted
    }
    
    const parsedData = parsePrompt(char.prompt)
    
    setFormData({
      name: char.name,
      description: char.description,
      image: char.image,
      voice_id: char.voice_id,
      ...parsedData
    })
  }, [params.id, router])
  
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
  
  const buildPrompt = () => {
    let prompt = `<personality>${formData.personality}</personality>\n`
    
    if (formData.speaking_style) {
      prompt += `<speaking_style>${formData.speaking_style}</speaking_style>\n`
    }
    if (formData.age) {
      prompt += `<age>${formData.age}</age>\n`
    }
    if (formData.gender) {
      prompt += `<gender>${formData.gender}</gender>\n`
    }
    if (formData.role) {
      prompt += `<role>${formData.role}</role>\n`
    }
    if (formData.backstory) {
      prompt += `<backstory>${formData.backstory}</backstory>\n`
    }
    if (formData.scenario) {
      prompt += `<scenario>${formData.scenario}</scenario>\n`
    }
    
    return prompt
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!character) return
    
    setLoading(true)
    
    try {
      const updatedCharacter: Character = {
        ...character,
        name: formData.name,
        description: formData.description,
        image: formData.image,
        prompt: buildPrompt(),
        voice_id: formData.voice_id,
        updated_at: new Date()
      }
      
      CharacterStorage.save(updatedCharacter)
      router.push('/characters')
    } catch (error) {
      console.error('Error updating character:', error)
    } finally {
      setLoading(false)
    }
  }
  
  if (!character) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading character...</div>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto p-4 max-w-2xl">
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.back()}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold">Edit Character: {character.name}</h1>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
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
            
            <div>
              <Label htmlFor="voice_id">Voice Selection</Label>
              <VoiceSelector
                selectedVoiceId={formData.voice_id}
                onSelect={(voiceId) => setFormData(prev => ({ ...prev, voice_id: voiceId }))}
              />
              <p className="text-sm text-gray-500 mt-1">
                Select a voice for your character or leave empty for default
              </p>
              
              {/* Voice Recommendation Button */}
              <div className="mt-3">
                <VoiceRecommendation
                  characterName={formData.name}
                  characterDescription={formData.description}
                  characterPersonality={formData.personality}
                  onSelectVoice={(voiceId) => setFormData(prev => ({ ...prev, voice_id: voiceId }))}
                  currentVoiceId={formData.voice_id}
                />
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle>Character Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="personality">Personality & Traits *</Label>
              <Textarea
                id="personality"
                value={formData.personality}
                onChange={(e) => setFormData(prev => ({ ...prev, personality: e.target.value }))}
                required
                rows={4}
                placeholder="Describe the character's personality, how they speak and behave..."
              />
            </div>
            
            <div>
              <Label htmlFor="speaking_style">Speaking Style</Label>
              <Input
                id="speaking_style"
                value={formData.speaking_style}
                onChange={(e) => setFormData(prev => ({ ...prev, speaking_style: e.target.value }))}
                placeholder="e.g. Uses casual speech, '~ya', '~ah' endings"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  value={formData.age}
                  onChange={(e) => setFormData(prev => ({ ...prev, age: e.target.value }))}
                  placeholder="e.g. 25"
                />
              </div>
              
              <div>
                <Label htmlFor="gender">Gender</Label>
                <Input
                  id="gender"
                  value={formData.gender}
                  onChange={(e) => setFormData(prev => ({ ...prev, gender: e.target.value }))}
                  placeholder="e.g. Female"
                />
              </div>
            </div>
            
            <div>
              <Label htmlFor="role">Role</Label>
              <Input
                id="role"
                value={formData.role}
                onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                placeholder="e.g. Math tutor"
              />
            </div>
            
            <div>
              <Label htmlFor="backstory">Background Story</Label>
              <Textarea
                id="backstory"
                value={formData.backstory}
                onChange={(e) => setFormData(prev => ({ ...prev, backstory: e.target.value }))}
                rows={3}
                placeholder="Character's background story..."
              />
            </div>
            
            <div>
              <Label htmlFor="scenario">Scenario/Context</Label>
              <Textarea
                id="scenario"
                value={formData.scenario}
                onChange={(e) => setFormData(prev => ({ ...prev, scenario: e.target.value }))}
                rows={3}
                placeholder="The situation where conversations take place..."
              />
            </div>
          </CardContent>
        </Card>
        
        <div className="flex gap-4">
          <Button type="submit" disabled={loading}>
            {loading ? 'Updating...' : 'Update Character'}
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