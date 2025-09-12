'use client'

import { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { ApiClient, PlatformChatResponse, PlatformTool } from '@/lib/api-client'
import { Character } from '@/types/character'
import { Send, Mic, MicOff, Loader2, X } from 'lucide-react'
import { TypewriterText } from '@/components/chat/TypewriterText'
import { AudioPlayer } from '@/components/chat/AudioPlayer'
import { UnifiedSelection } from '@/components/ui/UnifiedSelection'

interface PlatformChatInterfaceProps {
  character: Character
  userId: string
}

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  tools?: PlatformTool[]
  audio_url?: string
}

export default function PlatformChatInterface({ character, userId }: PlatformChatInterfaceProps) {
  // Core chat state
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentResponse, setCurrentResponse] = useState('')
  const [currentAudio, setCurrentAudio] = useState<string | null>(null)
  const [currentTools, setCurrentTools] = useState<PlatformTool[]>([])
  const [isThinking, setIsThinking] = useState(false)
  const [shouldStartTyping, setShouldStartTyping] = useState(false)
  const [isAudioPlaying, setIsAudioPlaying] = useState(false)
  const [userHasInteracted, setUserHasInteracted] = useState(false)

  // Input state
  const [inputText, setInputText] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  // Continuous response handling state
  const [pendingContinuousResponse, setPendingContinuousResponse] = useState<any>(null)

  // Initialize with greeting
  useEffect(() => {
    const initializeSession = async () => {
      console.log('🎬 Initializing platform chat session')
      setIsThinking(true)

      try {
        const response = await ApiClient.createPlatformSession(character.id, userId)
        console.log('✅ Session initialized:', response)

        setSessionId(response.session_id)
        setCurrentResponse(response.dialogue)
        setShouldStartTyping(true)

        // Handle greeting tools
        if (response.tools && response.tools.length > 0) {
          console.log('🔧 Greeting tools received:', response.tools)
          setCurrentTools(response.tools)
        }

        // Handle greeting audio
        if (response.audio_url) {
          setCurrentAudio(response.audio_url)
          setShouldStartTyping(false) // Wait for audio
        }

        // Add greeting to message history
        const greetingMessage: ChatMessage = {
          role: 'assistant',
          content: response.dialogue,
          timestamp: response.timestamp,
          tools: response.tools,
          audio_url: response.audio_url
        }
        setMessages([greetingMessage])

      } catch (error) {
        console.error('❌ Failed to initialize session:', error)
        setCurrentResponse('안녕하세요! 연결에 문제가 있었습니다. 메시지를 보내서 대화를 시작해보세요.')
        setShouldStartTyping(true)
      } finally {
        setIsThinking(false)
      }
    }

    initializeSession()
  }, [character.id, userId])

  const handleSend = async (message?: string) => {
    const textToSend = message || inputText.trim()
    if (!textToSend || !sessionId) return

    setUserHasInteracted(true)
    setInputText('')
    setIsTyping(false)

    // Add user message to history
    const userMessage: ChatMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])

    // Clear current state
    setIsThinking(true)
    setCurrentResponse('')
    setCurrentAudio(null)
    setCurrentTools([])
    setShouldStartTyping(false)

    try {
      const response = await ApiClient.platformChat({
        user_input: textToSend,
        character_id: character.id,
        session_id: sessionId,
        user_id: userId
      })

      console.log('📨 Platform chat response:', response)

      // Handle different tool types
      const primaryTool = response.tools?.[0]
      if (primaryTool?.type === 'continuous_quiz_response') {
        handleContinuousQuizResponse(response, primaryTool)
      } else {
        handleStandardResponse(response)
      }

    } catch (error) {
      console.error('❌ Chat error:', error)
      setCurrentResponse('죄송해요, 문제가 발생했습니다. 다시 시도해주세요.')
      setShouldStartTyping(true)
    } finally {
      setIsThinking(false)
    }
  }

  const handleStandardResponse = (response: PlatformChatResponse) => {
    console.log('📝 Handling standard response')
    
    // Set dialogue and audio
    setCurrentResponse(response.dialogue)
    if (response.audio_url) {
      setCurrentAudio(response.audio_url)
      setShouldStartTyping(false) // Wait for audio
    } else {
      setShouldStartTyping(true)
    }

    // Set tools
    if (response.tools && response.tools.length > 0) {
      setCurrentTools(response.tools)
    }

    // Add to message history
    const assistantMessage: ChatMessage = {
      role: 'assistant',
      content: response.dialogue,
      timestamp: response.timestamp,
      tools: response.tools,
      audio_url: response.audio_url
    }
    setMessages(prev => [...prev, assistantMessage])
  }

  const handleContinuousQuizResponse = (response: PlatformChatResponse, tool: PlatformTool) => {
    console.log('🔄 Handling continuous quiz response')
    
    const toolData = tool.data
    
    // Phase 1: Show feedback with audio
    if (toolData.phase1) {
      setCurrentResponse(toolData.phase1.text)
      
      if (toolData.phase1.audio_url) {
        setCurrentAudio(toolData.phase1.audio_url)
        setShouldStartTyping(false) // Wait for audio
        
        // Store phase 2 data for later
        setPendingContinuousResponse({
          phase2: toolData.phase2,
          delay: toolData.phase1.delay_ms || 3000
        })
      } else {
        setShouldStartTyping(true)
        // Process phase 2 immediately if no audio
        setTimeout(() => processPhase2(toolData.phase2), toolData.phase1.delay_ms || 3000)
      }

      // Add phase 1 to message history
      const phase1Message: ChatMessage = {
        role: 'assistant',
        content: toolData.phase1.text,
        timestamp: response.timestamp,
        audio_url: toolData.phase1.audio_url
      }
      setMessages(prev => [...prev, phase1Message])
    }
  }

  const processPhase2 = (phase2Data: any) => {
    console.log('⏭️ Processing phase 2')
    
    if (phase2Data) {
      // Display phase 2 text
      setCurrentResponse(phase2Data.text)
      
      if (phase2Data.audio_url) {
        setCurrentAudio(phase2Data.audio_url)
        setShouldStartTyping(false) // Wait for audio
      } else {
        setShouldStartTyping(true)
      }

      // Show tools after phase 2 audio or immediately if no audio
      if (phase2Data.tool) {
        setTimeout(() => {
          setCurrentTools([phase2Data.tool])
        }, phase2Data.audio_url ? 1000 : 0)
      }

      // Add phase 2 to message history
      const phase2Message: ChatMessage = {
        role: 'assistant',
        content: phase2Data.text,
        timestamp: new Date().toISOString(),
        tools: phase2Data.tool ? [phase2Data.tool] : [],
        audio_url: phase2Data.audio_url
      }
      setMessages(prev => [...prev, phase2Message])
    }

    setPendingContinuousResponse(null)
  }

  const handleToolSelection = (selection: string) => {
    console.log('🔧 Tool selection:', selection)
    setCurrentTools([]) // Clear tools immediately
    handleSend(selection)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setInputText(value)
    setIsTyping(value.length > 0)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleAudioPlayStart = () => {
    console.log('🎵 Audio started playing')
    setShouldStartTyping(true)
    setIsAudioPlaying(true)
  }

  const handleAudioPlayEnd = () => {
    console.log('🎵 Audio finished playing')
    setIsAudioPlaying(false)
    
    // Process pending continuous response if any
    if (pendingContinuousResponse) {
      setTimeout(() => {
        processPhase2(pendingContinuousResponse.phase2)
      }, pendingContinuousResponse.delay || 3000)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-gradient-to-b from-slate-50 to-slate-100/40">
      {/* Main content area */}
      <main className="flex flex-1 flex-col items-center justify-center space-y-8 px-6 py-8">
        <div className="flex w-full max-w-2xl flex-col items-center space-y-6 text-center">
          
          {/* Character avatar */}
          <div className="relative">
            {/* Thinking pulse rings */}
            {isThinking && (
              <div className="absolute inset-0 -m-10">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute inset-0 rounded-full border-2 border-primary/20"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ 
                      scale: [0.8, 2.0], 
                      opacity: [0, 0.2, 0.1, 0] 
                    }}
                    transition={{
                      duration: 2.5,
                      delay: i * 0.5,
                      repeat: Infinity,
                      ease: [0.25, 0.46, 0.45, 0.94]
                    }}
                  />
                ))}
              </div>
            )}
            
            {/* Character avatar */}
            <div className="relative">
              <div 
                className={`h-40 w-40 overflow-hidden rounded-full border-4 border-border bg-white shadow-lg ${
                  isAudioPlaying && !isThinking ? 'animate-pulse-scale' : ''
                }`}
              >
                {character.image ? (
                  <img 
                    src={character.image} 
                    alt={character.name}
                    className="h-full w-full object-cover object-top transition-transform hover:scale-105"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center">
                    <span className="text-4xl font-bold text-muted-foreground">
                      {character.name[0]?.toUpperCase()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Response area */}
          <div className="min-h-[120px] w-full max-w-xl flex items-center justify-center">
            <AnimatePresence mode="wait">
              {isThinking ? (
                <motion.div
                  key="thinking"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex items-center gap-3 text-muted-foreground"
                >
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span className="text-lg">Thinking...</span>
                </motion.div>
              ) : currentResponse ? (
                <motion.div
                  key="response"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className="text-lg leading-relaxed">
                    <TypewriterText
                      text={currentResponse}
                      speed={50}
                      startTyping={shouldStartTyping}
                      onComplete={() => {}}
                    />
                  </div>
                  
                  {/* Audio player */}
                  {currentAudio && (
                    <motion.div
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="flex justify-center"
                    >
                      <AudioPlayer
                        audioBase64={currentAudio}
                        autoPlay={true}
                        userHasInteracted={userHasInteracted}
                        onPlayStart={handleAudioPlayStart}
                        onPlayEnd={handleAudioPlayEnd}
                        onError={(error) => console.error('Audio error:', error)}
                      />
                    </motion.div>
                  )}
                </motion.div>
              ) : (
                <motion.div
                  key="waiting"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-lg text-muted-foreground"
                >
                  대화를 시작해보세요...
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </main>

      {/* Tool UI - Selection interface */}
      <AnimatePresence>
        {currentTools.length > 0 && currentTools[0].type === 'show_selection' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-24 left-1/2 transform -translate-x-1/2 max-w-md z-50"
          >
            <UnifiedSelection
              items={currentTools[0].data.options || currentTools[0].data.items || []}
              onSelect={handleToolSelection}
              question={currentTools[0].data.question}
              correctAnswer={currentTools[0].data.correct_answer}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <footer className="sticky bottom-0 border-t border-border/40 bg-slate-50/95 backdrop-blur supports-[backdrop-filter]:bg-slate-50/60">
        <div className="container max-w-2xl mx-auto px-6 py-4">
          <div className="flex items-end gap-3">
            
            {/* Text input */}
            <div className="flex-1">
              <Input
                value={inputText}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="메시지 입력..."
                className="h-12 rounded-full border-2 bg-background transition-colors focus:border-primary"
                disabled={isThinking}
              />
            </div>
            
            {/* Send button */}
            <Button
              size="icon"
              onClick={() => handleSend()}
              disabled={!inputText.trim() || isThinking}
              className="h-12 w-12 shrink-0 rounded-full border-2 transition-all disabled:opacity-50"
              variant={inputText.trim() ? "default" : "outline"}
              title="메시지 전송"
            >
              <Send className="h-5 w-5" />
              <span className="sr-only">메시지 전송</span>
            </Button>
          </div>
        </div>
      </footer>
    </div>
  )
}