'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ChevronDown, Play, Pause, Loader2, Search, ChevronLeft, ChevronRight } from 'lucide-react'

interface Voice {
  id: string
  name: string
  gender?: string
  age?: string
  language?: string
  description?: string
}

interface VoiceSelectorProps {
  selectedVoiceId?: string
  onSelect: (voiceId: string) => void
}

export default function VoiceSelector({ selectedVoiceId, onSelect }: VoiceSelectorProps) {
  const [voices, setVoices] = useState<Voice[]>([])
  const [filteredVoices, setFilteredVoices] = useState<Voice[]>([])
  const [isOpen, setIsOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [loadingComplete, setLoadingComplete] = useState(false)
  const [previewingVoiceId, setPreviewingVoiceId] = useState<string | null>(null)
  const [loadingVoiceId, setLoadingVoiceId] = useState<string | null>(null)
  const [audioCache] = useState<Map<string, string>>(new Map())
  const [currentAudio, setCurrentAudio] = useState<HTMLAudioElement | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [loadingProgress, setLoadingProgress] = useState<string>('')
  const ITEMS_PER_PAGE = 10

  // Load quick access voices immediately, then full list
  useEffect(() => {
    loadQuickVoices()
    loadFullVoices()
  }, [])

  // Load cached previews from localStorage
  useEffect(() => {
    const cached = localStorage.getItem('voice_preview_cache')
    if (cached) {
      try {
        const cacheData = JSON.parse(cached)
        cacheData.forEach(([key, value]: [string, string]) => {
          audioCache.set(key, value)
        })
      } catch (e) {
        console.error('Failed to load voice cache:', e)
      }
    }
  }, [audioCache])

  // Filter voices based on search term
  useEffect(() => {
    const filtered = voices.filter(voice => 
      voice.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (voice.gender && voice.gender.includes(searchTerm)) ||
      (voice.description && voice.description.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    setFilteredVoices(filtered)
    setCurrentPage(1) // Reset to first page when searching
  }, [searchTerm, voices])

  const loadQuickVoices = () => {
    // 즉시 사용 가능한 인기 목소리들 (로컬 데이터)
    const quickVoices = [
      { id: 'tc_61c97b56f1b7877a74df625b', name: 'Emma', gender: '여성', age: '20대', description: '부드럽고 친근한 여성 목소리' },
      { id: 'tc_6073b2f6817dccf658bb159f', name: 'Duke', gender: '남성', age: '30대', description: '차분하고 신뢰감 있는 남성 목소리' },
      { id: 'tc_624152dced4a43e78f703148', name: 'Tyson', gender: '남성', age: '40대', description: '강인하고 카리스마 있는 남성 목소리' },
      { id: 'tc_6621c95cd872405d1a6de98e', name: 'Kristen', gender: '여성', age: '30대', description: '전문적이고 명확한 여성 목소리' }
    ]
    setVoices(quickVoices)
    setFilteredVoices(quickVoices)
  }

  const loadFullVoices = async () => {
    setLoading(true)
    setLoadingProgress('목소리 리스트를 불러오는 중...')
    
    try {
      const startTime = Date.now()
      const response = await fetch('http://localhost:8000/api/voices/korean')
      
      if (response.ok) {
        setLoadingProgress('목소리 정보를 처리 중...')
        const data = await response.json()
        const voiceList = data.voices || []
        
        const formattedVoices = voiceList.map((v: any) => ({
          id: v.voice_id || v.id,
          name: v.voice_name || v.name,
          gender: v.gender,
          age: v.age,
          language: v.language,
          description: v.description
        }))
        
        const loadTime = Date.now() - startTime
        setLoadingProgress(`${formattedVoices.length}개 목소리 로드 완료! (${(loadTime/1000).toFixed(1)}초)`)
        
        setVoices(formattedVoices)
        setFilteredVoices(formattedVoices)
        setLoadingComplete(true)
        
        // 성공 메시지 잠시 표시 후 숨김
        setTimeout(() => setLoadingProgress(''), 2000)
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (error) {
      console.error('Failed to load full voices:', error)
      setLoadingProgress('일부 목소리만 표시됩니다 (네트워크 오류)')
      setTimeout(() => setLoadingProgress(''), 3000)
    } finally {
      setLoading(false)
    }
  }

  const playAudio = (base64: string) => {
    // Stop current audio if playing
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
    // If already playing this voice, stop it
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
          text: "안녕하세요, 제 목소리입니다.",
          voice_id: voiceId,
          emotion: "normal"
        })
      })

      if (response.ok) {
        const data = await response.json()
        if (data.audio_base64) {
          // Cache the audio
          audioCache.set(voiceId, data.audio_base64)
          
          // Save to localStorage
          const cacheArray = Array.from(audioCache.entries())
          localStorage.setItem('voice_preview_cache', JSON.stringify(cacheArray))
          
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

  const selectedVoice = voices.find(v => v.id === selectedVoiceId)
  
  // Pagination logic
  const totalPages = Math.ceil(filteredVoices.length / ITEMS_PER_PAGE)
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE
  const paginatedVoices = filteredVoices.slice(startIndex, startIndex + ITEMS_PER_PAGE)

  return (
    <div className="relative">
      <Button 
        onClick={() => setIsOpen(!isOpen)} 
        variant="outline" 
        className="w-full justify-between"
        disabled={loading}
      >
        <>
          {selectedVoice ? selectedVoice.name : 'Select a voice'}
          {loading && <Loader2 className="ml-2 h-4 w-4 animate-spin" />}
          {!loading && <ChevronDown className={`ml-2 h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />}
        </>
      </Button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border rounded-lg shadow-lg">
          {/* Search box */}
          <div className="p-3 border-b">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search voices..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            {/* Loading progress */}
            {loadingProgress && (
              <div className="mt-2 text-xs text-blue-600 flex items-center gap-2">
                {loading && <Loader2 className="h-3 w-3 animate-spin" />}
                {loadingProgress}
              </div>
            )}
          </div>
          
          {/* Voice list */}
          <div className="max-h-80 overflow-y-auto">
            {filteredVoices.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                {searchTerm ? 'No voices found' : 'No voices available'}
              </div>
            ) : (
              paginatedVoices.map(voice => (
              <div 
                key={voice.id} 
                className="flex items-center justify-between p-3 hover:bg-gray-50 border-b last:border-b-0"
              >
                <div 
                  className="flex-1 cursor-pointer"
                  onClick={() => {
                    onSelect(voice.id)
                    setIsOpen(false)
                    stopAudio()
                  }}
                >
                  <div className="font-medium">{voice.name}</div>
                  {(voice.gender || voice.age) && (
                    <div className="text-sm text-gray-500">
                      {voice.gender && voice.gender}
                      {voice.gender && voice.age && ' · '}
                      {voice.age && voice.age}
                    </div>
                  )}
                  {voice.description && (
                    <div className="text-xs text-gray-400 mt-1">
                      {voice.description}
                    </div>
                  )}
                </div>
                
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation()
                    previewVoice(voice.id)
                  }}
                  disabled={loadingVoiceId !== null && loadingVoiceId !== voice.id}
                  className="flex items-center justify-center w-8 h-8"
                >
                  {loadingVoiceId === voice.id ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : previewingVoiceId === voice.id ? (
                    <Pause className="h-4 w-4" />
                  ) : (
                    <Play className="h-4 w-4" />
                  )}
                </Button>
              </div>
            ))
            )}
          </div>
          
          {/* Pagination */}
          {filteredVoices.length > ITEMS_PER_PAGE && (
            <div className="p-3 border-t bg-gray-50 flex items-center justify-between">
              <div className="text-sm text-gray-500">
                {filteredVoices.length} voices total
              </div>
              <div className="flex items-center gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <span className="text-sm">
                  {currentPage} / {totalPages}
                </span>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}