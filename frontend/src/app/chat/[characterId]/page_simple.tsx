'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CharacterStorage } from '@/lib/storage'
import { ApiClient } from '@/lib/api-client'
import { Character } from '@/types/character'
import { ChatMessage, ChatResponse } from '@/types/chat'
import { ArrowLeft, Send, Mic, MicOff, Loader2, X, Trash2 } from 'lucide-react'
import { TypewriterText } from '@/components/chat/TypewriterText'
import { AudioPlayer } from '@/components/chat/AudioPlayer'

export default function ChatPageSimple() {
  const params = useParams()
  const router = useRouter()
  
  const [character, setCharacter] = useState<Character | null>(null)
  const [characterLoading, setCharacterLoading] = useState(true)
  
  // Chat states - simplified
  const [isThinking, setIsThinking] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [currentAudio, setCurrentAudio] = useState<string | null>(null)
  const [inputText, setInputText] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [characterEmotion, setCharacterEmotion] = useState('')
  const [shouldStartTyping, setShouldStartTyping] = useState(false)
  const [welcomeGenerated, setWelcomeGenerated] = useState(false)
  
  // Session state - simplified
  const [sessionId, setSessionId] = useState<string | null>(null)
  
  const characterId = params.characterId as string

  // Load character
  useEffect(() => {
    const loadCharacter = async () => {
      try {
        const characters = CharacterStorage.getAllCharacters()
        const foundCharacter = characters.find(c => c.id === characterId)
        
        if (foundCharacter) {
          setCharacter(foundCharacter)
          console.log('✅ Character loaded:', foundCharacter.name)
        } else {
          console.error('❌ Character not found:', characterId)
          router.push('/characters')
        }
      } catch (error) {
        console.error('❌ Error loading character:', error)
        router.push('/characters')
      } finally {
        setCharacterLoading(false)
      }
    }

    loadCharacter()
  }, [characterId, router])

  // Generate welcome message
  useEffect(() => {
    const generateWelcome = async () => {
      if (!character || welcomeGenerated) return

      console.log('🎬 Generating welcome message...')
      try {
        setIsThinking(true)
        
        const response = await ApiClient.chatWithSession({
          message: '안녕하세요',
          character_prompt: character.prompt,
          character_id: character.id,
          user_id: 'demo_user',
          voice_id: character.voice_id
        })
        
        setSessionId(response.session_id)
        setCurrentResponse(response.dialogue)
        setCharacterEmotion(response.emotion)
        
        if (response.audio) {
          setCurrentAudio(response.audio)
        }
        
        setShouldStartTyping(true)
        setWelcomeGenerated(true)
        
        console.log('✅ Welcome generated, session:', response.session_id)
      } catch (error) {
        console.error('❌ Error generating welcome:', error)
        setCurrentResponse('안녕하세요! 저와 대화해보세요.')
        setShouldStartTyping(true)
        setWelcomeGenerated(true)
      } finally {
        setIsThinking(false)
      }
    }

    generateWelcome()
  }, [character, welcomeGenerated])

  // Send message function - simplified
  const sendMessage = async (textToSend: string) => {
    if (!character || !textToSend.trim()) return

    try {
      console.log('💬 Sending message:', textToSend)
      setIsThinking(true)
      setInputText('')
      
      // Add user message to UI
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: textToSend,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, userMessage])
      
      // Send to session-based chat API
      const response = await ApiClient.chatWithSession({
        session_id: sessionId || undefined,
        message: textToSend,
        character_prompt: character.prompt,
        character_id: character.id,
        user_id: 'demo_user',
        voice_id: character.voice_id
      })
      
      // Update session ID if new
      if (response.session_id && !sessionId) {
        setSessionId(response.session_id)
        console.log('✅ Session created:', response.session_id)
      }
      
      // Set response for typewriter
      setCurrentResponse(response.dialogue)
      setCharacterEmotion(response.emotion)
      
      if (response.audio) {
        setCurrentAudio(response.audio)
      }
      
      // Add assistant message to UI
      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.dialogue,
        timestamp: new Date().toISOString(),
        emotion: response.emotion
      }
      setMessages(prev => [...prev, assistantMessage])
      
      setShouldStartTyping(true)
      
      console.log('✅ Message sent, session messages:', response.message_count || 'unknown')
    } catch (error) {
      console.error('❌ Error sending message:', error)
      setCurrentResponse('죄송해요, 응답에 문제가 있었어요.')
      setShouldStartTyping(true)
    } finally {
      setIsThinking(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (inputText.trim()) {
      sendMessage(inputText.trim())
    }
  }

  const clearChat = () => {
    setMessages([])
    setCurrentResponse('')
    setCurrentAudio(null)
    setSessionId(null)
    setWelcomeGenerated(false)
    console.log('🗑️ Chat cleared, will regenerate welcome')
  }

  if (characterLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
      </div>
    )
  }

  if (!character) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Character not found</h1>
          <Button onClick={() => router.push('/characters')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Characters
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => router.push('/characters')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <div className="flex items-center space-x-3">
              <img
                src={character.image}
                alt={character.name}
                className="w-10 h-10 rounded-full object-cover"
              />
              <div>
                <h1 className="font-semibold text-gray-800">{character.name}</h1>
                {sessionId && (
                  <p className="text-xs text-gray-500">Session: {sessionId.slice(0, 12)}...</p>
                )}
              </div>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={clearChat}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Clear Chat
          </Button>
        </div>
      </div>

      {/* Chat Area */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow-sm min-h-[500px] flex flex-col">
          {/* Messages */}
          <div className="flex-1 p-6 space-y-4 max-h-[500px] overflow-y-auto">
            {/* Character Response */}
            <AnimatePresence>
              {currentResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-start space-x-3"
                >
                  <img
                    src={character.image}
                    alt={character.name}
                    className="w-8 h-8 rounded-full object-cover flex-shrink-0 mt-1"
                  />
                  <div className="bg-gray-100 rounded-lg p-3 max-w-[80%]">
                    <TypewriterText
                      text={currentResponse}
                      speed={50}
                      shouldStart={shouldStartTyping}
                      onComplete={() => {
                        setShouldStartTyping(false)
                        setIsTyping(false)
                      }}
                      onStart={() => setIsTyping(true)}
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Previous Messages */}
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                {message.role === 'assistant' && (
                  <img
                    src={character.image}
                    alt={character.name}
                    className="w-8 h-8 rounded-full object-cover flex-shrink-0 mt-1"
                  />
                )}
                <div
                  className={`rounded-lg p-3 max-w-[80%] ${
                    message.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              </motion.div>
            ))}

            {/* Thinking indicator */}
            {isThinking && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center space-x-2 text-gray-500"
              >
                <img
                  src={character.image}
                  alt={character.name}
                  className="w-8 h-8 rounded-full object-cover"
                />
                <div className="flex items-center space-x-1">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">생각중...</span>
                </div>
              </motion.div>
            )}
          </div>

          {/* Input */}
          <div className="border-t p-4">
            <form onSubmit={handleSubmit} className="flex space-x-2">
              <Input
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="메시지를 입력하세요..."
                disabled={isThinking}
                className="flex-1"
              />
              <Button type="submit" disabled={!inputText.trim() || isThinking}>
                <Send className="w-4 h-4" />
              </Button>
            </form>
          </div>
        </div>
      </div>

      {/* Audio Player */}
      {currentAudio && (
        <AudioPlayer
          audioData={currentAudio}
          onPlayComplete={() => setCurrentAudio(null)}
        />
      )}
    </div>
  )
}