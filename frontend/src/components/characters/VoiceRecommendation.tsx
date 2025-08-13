'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Sparkles, Play, Pause, Loader2, Check } from 'lucide-react'

interface VoiceRecommendation {
  voice_id: string
  voice_name: string
  score: number
  gender?: string
  age?: string
  description?: string
}

interface VoiceRecommendationProps {
  characterName: string
  characterDescription: string
  characterPersonality: string
  onSelectVoice: (voiceId: string) => void
  currentVoiceId?: string
}

export default function VoiceRecommendation({ 
  characterName,
  characterDescription,
  characterPersonality,
  onSelectVoice,
  currentVoiceId 
}: VoiceRecommendationProps) {
  const [recommendations, setRecommendations] = useState<VoiceRecommendation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [previewingVoiceId, setPreviewingVoiceId] = useState<string | null>(null)
  const [loadingVoiceId, setLoadingVoiceId] = useState<string | null>(null)
  const [audioCache] = useState<Map<string, string>>(new Map())
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)

  const validateFields = () => {
    const missingFields = []
    
    if (!characterName.trim()) {
      missingFields.push('Character Name')
    }
    
    const hasDescription = characterDescription.trim().length > 0
    const hasPersonality = characterPersonality.trim().length > 0
    
    if (!hasDescription && !hasPersonality) {
      missingFields.push('Short Description or Personality & Traits')
    }
    
    return missingFields
  }

  const getRecommendations = async () => {
    const missingFields = validateFields()
    
    if (missingFields.length > 0) {
      alert(`다음 필드를 입력해주세요:\n• ${missingFields.join('\n• ')}`)
      return
    }

    setIsLoading(true)
    try {
      // Combine available information for better recommendations
      const combinedPrompt = {
        name: characterName,
        description: characterDescription,
        personality: characterPersonality
      }
      
      const characterPrompt = [
        characterName && `Name: ${characterName}`,
        characterDescription && `Description: ${characterDescription}`,
        characterPersonality && `Personality: ${characterPersonality}`
      ].filter(Boolean).join('\n')

      console.log('Sending request with prompt:', characterPrompt) // 디버깅용
      
      const response = await fetch('http://localhost:8000/api/voices/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          character_prompt: characterPrompt,
          top_k: 5
        })
      })
      
      console.log('Response status:', response.status, response.statusText) // 디버깅용
      
      if (!response.ok) {
        const errorText = await response.text()
        console.error('API Error Response:', errorText)
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }

      const data = await response.json()
      console.log('Recommendation response:', data) // 디버깅용
      
      if (data.status === 'success' && data.recommendations && data.recommendations.length > 0) {
        console.log('Successfully received', data.recommendations.length, 'recommendations')
        setRecommendations(data.recommendations)
      } else {
        console.error('No recommendations received:', data)
        alert(`추천 결과가 없습니다. (Status: ${data.status}, Message: ${data.message || 'No message'})`)
        setRecommendations([])
      }
    } catch (error) {
      console.error('Error getting recommendations:', error)
      const errorMessage = error instanceof Error ? error.message : String(error)
      alert(`오류가 발생했습니다: ${errorMessage}`)
      setRecommendations([])
    } finally {
      setIsLoading(false)
    }
  }

  const playAudio = (base64: string) => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
    }

    const audio = new Audio(`data:audio/mp3;base64,${base64}`)
    audio.onended = () => {
      setPreviewingVoiceId(null)
      setCurrentAudio(null)
    }
    audio.play()
    setCurrentAudio(audio)
  }

  const stopAudio = () => {
    if (currentAudio) {
      currentAudio.pause()
      currentAudio.currentTime = 0
      setCurrentAudio(null)
      setPreviewingVoiceId(null)
    }
  }

  const previewVoice = async (voiceId: string) => {
    if (previewingVoiceId === voiceId) {
      stopAudio()
      return
    }

    // Check cache first
    if (audioCache.has(voiceId)) {
      setPreviewingVoiceId(voiceId)
      playAudio(audioCache.get(voiceId)!)
      return
    }

    // Generate sample audio with loading state
    setLoadingVoiceId(voiceId)
    try {
      const response = await fetch('http://localhost:8000/api/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: "안녕하세요. 제 목소리입니다. 어떠신가요?",
          voice_id: voiceId,
          emotion: "normal"
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.audio_base64) {
          audioCache.set(voiceId, data.audio_base64)
          
          // Start playing
          setLoadingVoiceId(null)
          setPreviewingVoiceId(voiceId)
          playAudio(data.audio_base64)
        } else {
          throw new Error('No audio data received')
        }
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to preview voice:', error)
      setLoadingVoiceId(null)
      setPreviewingVoiceId(null)
    }
  }

  const isRecommendationEnabled = () => {
    return validateFields().length === 0
  }

  return (
    <div className="space-y-3">
      <Button 
        onClick={getRecommendations}
        disabled={isLoading || !isRecommendationEnabled()}
        size="sm"
        variant="outline"
        className="w-full"
      >
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            AI가 분석 중...
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            AI 목소리 추천받기
          </>
        )}
      </Button>
      
      {!isRecommendationEnabled() && (
        <p className="text-xs text-amber-600 flex items-center gap-1">
          ⚠️ 추천을 받으려면 <strong>캐릭터 이름</strong>과 <strong>설명 또는 성격</strong> 중 하나를 입력해주세요
        </p>
      )}

      {recommendations.length > 0 && (
        <Card className="p-4">
          <h4 className="font-medium mb-3 flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-primary" />
            추천 목소리 (매칭률 순)
          </h4>
          <div className="space-y-2">
            {recommendations.map((rec, idx) => (
              <div 
                key={rec.voice_id}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  currentVoiceId === rec.voice_id ? 'bg-primary/5 border-primary' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="text-sm font-bold text-primary">
                    #{idx + 1}
                  </div>
                  <div>
                    <div className="font-medium flex items-center gap-2">
                      {rec.voice_name}
                      {currentVoiceId === rec.voice_id && (
                        <span className="text-xs bg-primary text-white px-2 py-0.5 rounded">
                          Selected
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {rec.gender && <span>{rec.gender}</span>}
                      {rec.gender && rec.age && <span> · </span>}
                      {rec.age && <span>{rec.age}</span>}
                      <span className="ml-2 text-primary">
                        {(rec.score * 100).toFixed(1)}% 매칭
                      </span>
                    </div>
                    {rec.description && (
                      <div className="text-xs text-gray-400 mt-1">
                        {rec.description}
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => rec.voice_id ? previewVoice(rec.voice_id) : null}
                    disabled={!rec.voice_id || (loadingVoiceId !== null && loadingVoiceId !== rec.voice_id)}
                    className="flex items-center justify-center w-8 h-8"
                    title={!rec.voice_id ? "매핑 작업 후 사용 가능" : "목소리 미리듣기"}
                  >
                    {!rec.voice_id ? (
                      <span className="text-xs text-gray-400">N/A</span>
                    ) : loadingVoiceId === rec.voice_id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : previewingVoiceId === rec.voice_id ? (
                      <Pause className="h-4 w-4" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    disabled={!rec.voice_id}
                    onClick={() => {
                      if (rec.voice_id) {
                        onSelectVoice(rec.voice_id)
                        stopAudio()
                      }
                    }}
                    title={!rec.voice_id ? "매핑 작업 후 사용 가능" : "목소리 선택"}
                  >
                    {!rec.voice_id ? (
                      <span className="text-xs">준비중</span>
                    ) : currentVoiceId === rec.voice_id ? (
                      <Check className="h-4 w-4" />
                    ) : (
                      '선택'
                    )}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}