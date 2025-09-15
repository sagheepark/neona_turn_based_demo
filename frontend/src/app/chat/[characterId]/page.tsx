'use client'

import { useEffect, useState, useRef } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CharacterStorage } from '@/lib/storage'
import { ApiClient } from '@/lib/api-client'
import { Character } from '@/types/character'

// API Base URL for consistent backend calls
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
import { ChatMessage, ChatResponse } from '@/types/chat'
import { ArrowLeft, Send, Mic, MicOff, Loader2, X } from 'lucide-react'
import { TypewriterText } from '@/components/chat/TypewriterText'
import { AudioPlayer } from '@/components/chat/AudioPlayer'
import { SessionContinuationModal } from '@/components/chat/SessionContinuationModal'
import { SessionStartResponse } from '@/lib/api-client'
import { UnifiedSelection } from '@/components/ui/UnifiedSelection'

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
  const characterId = params.characterId as string  // Extract characterId at component level
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  
  const [character, setCharacter] = useState<Character | null>(null)
  const [characterLoading, setCharacterLoading] = useState(true)
  
  // Chat states
  const [isThinking, setIsThinking] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [currentResponse, setCurrentResponse] = useState('')
  const [currentAudio, setCurrentAudio] = useState<string | null>(null)
  const [lastUserMessage, setLastUserMessage] = useState('')
  const [inputText, setInputText] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isTyping, setIsTyping] = useState(false)
  const [characterEmotion, setCharacterEmotion] = useState('')
  const [shouldStartTyping, setShouldStartTyping] = useState(false)
  const [userHasInteracted, setUserHasInteracted] = useState(false)
  const [isAudioPlaying, setIsAudioPlaying] = useState(false)
  
  // Tool-based interactions state
  const [currentTools, setCurrentTools] = useState<any[]>([])

  // Continuous response handling state
  const [pendingContinuousResponse, setPendingContinuousResponse] = useState<any>(null)

  // Continuous flow state
  const [activeContinuousFlow, setActiveContinuousFlow] = useState<{
    sessionId: string
    flowId: string
    stepId: string
    nextStepTrigger?: string
    nextStepIndex?: number | null
  } | null>(null)

  // Session state for enhanced memory
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [welcomeGenerated, setWelcomeGenerated] = useState(false)
  
  // Session continuation modal states
  const [showSessionModal, setShowSessionModal] = useState(false)
  const [sessionData, setSessionData] = useState<SessionStartResponse | null>(null)
  const [isLoadingSessionData, setIsLoadingSessionData] = useState(false)

  useEffect(() => {
    const loadCharacter = async () => {
      // Force refresh demo characters to get latest data
      await CharacterStorage.initializeDemo(true)
      
      const char = CharacterStorage.getAll().find(c => c.id === characterId)
      
      if (!char) {
        router.push('/characters')
        return
      }
      
      setCharacter(char)
      setCharacterLoading(false)
      
      // Reset states when character changes (but not welcomeGenerated here to avoid loop)
      setCurrentResponse('')
      setCurrentAudio(null)
      setMessages([])
      setWelcomeGenerated(false) // Reset welcome state for new character
      setSessionId(null) // Reset session for new character
      
      // Check for existing sessions
      checkForExistingSessions(characterId)
    }
    
    loadCharacter()
    
  }, [params.characterId, router]) // Removed welcomeGenerated dependency

  const checkForExistingSessions = async (characterId: string) => {
    try {
      setIsLoadingSessionData(true)
      const sessionStartResponse = await ApiClient.startSession({
        user_id: 'demo_user',
        character_id: characterId
      })
      
      if (sessionStartResponse.data.can_continue && sessionStartResponse.data.previous_sessions.length > 0) {
        setSessionData(sessionStartResponse)
        setShowSessionModal(true)
      } else {
        // No previous sessions, start fresh
        setShowSessionModal(false)
        setSessionData(null)
      }
    } catch (error) {
      console.error('Failed to check existing sessions:', error)
      // If error, just start fresh
      setShowSessionModal(false)
      setSessionData(null)
    } finally {
      setIsLoadingSessionData(false)
    }
  }

  // Cleanup effect for recording resources
  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
      if (audioContextRef.current) {
        audioContextRef.current.close().catch(console.warn)
      }
    }
  }, [])

  // Enhanced welcome message generation with session support
  useEffect(() => {
    console.log('🔍 Welcome generation check:', {
      hasCharacter: !!character,
      characterName: character?.name,
      welcomeGenerated,
      showSessionModal,
      isLoadingSessionData,
      hasGreetings: character?.greetings?.length || 0
    })
    
    if (!character || welcomeGenerated || showSessionModal || isLoadingSessionData) return
    
    const generateWelcome = async () => {
      // Use random greeting from greetings array if available, otherwise generate default welcome
      let welcomeMessage = `안녕하세요! 저는 ${character.name}입니다. ${character.description}. 궁금한 것이 있으시면 언제든지 물어보세요!`
      
      if (character.greetings && character.greetings.length > 0) {
        const randomIndex = Math.floor(Math.random() * character.greetings.length)
        welcomeMessage = character.greetings[randomIndex]
      }
      
      // Show thinking state briefly
      setIsThinking(true)
      setWelcomeGenerated(true) // Prevent duplicate calls
      
      try {
        // For characters with predefined greetings, use them directly but also store in backend session
        if (character.greetings && character.greetings.length > 0) {
          console.log('🎭 Character has predefined greetings:', character.greetings)
          console.log('🎭 Using predefined greeting:', welcomeMessage)
          
          // Send the predefined greeting to backend with a special flag to store it properly
          const response: ChatResponse = await ApiClient.chatWithSession({
            session_id: sessionId || undefined,
            message: `__PREDEFINED_GREETING__:${welcomeMessage}`, // Special flag for backend
            character_prompt: character.prompt,
            character_id: character.id,
            user_id: 'demo_user',
            voice_id: character.voice_id
          })
          
          // Update session ID if new
          if (response.session_id && !sessionId) {
            setSessionId(response.session_id)
            console.log('✅ Session created for predefined greeting:', response.session_id)
          }
          
          // Generate TTS for the predefined greeting (use predefined, not backend response)
          const ttsResponse = await ApiClient.textToSpeech(welcomeMessage, character.voice_id, 'happy', character.id)
          
          // Set response data using predefined greeting
          setCurrentResponse(welcomeMessage)
          setCharacterEmotion('happy')
          
          // Handle tools from backend response
          if (response.tools && response.tools.length > 0) {
            console.log('Welcome tools received:', response.tools)
            setCurrentTools(response.tools)
          } else {
            setCurrentTools([])
          }
          
          if (ttsResponse.audio) {
            console.log('Setting welcome TTS audio, length:', ttsResponse.audio.length)
            setCurrentAudio(ttsResponse.audio)
            setShouldStartTyping(false) // Wait for audio to start
          } else {
            console.log('No TTS audio generated')
            setShouldStartTyping(true) // No audio, start typing immediately
          }
          
          // Add the welcome message to history as assistant message
          const welcomeHistoryMessage: ChatMessage = {
            role: 'assistant',
            content: welcomeMessage,
            timestamp: new Date().toISOString()
          }
          setMessages([welcomeHistoryMessage])
          
        } else {
          // For characters without predefined greetings, use LLM-generated welcome
          const response: ChatResponse = await ApiClient.chatWithSession({
            session_id: sessionId || undefined,
            message: '안녕하세요', // Simple greeting to trigger welcome
            character_prompt: character.prompt,
            character_id: character.id,
            user_id: 'demo_user',
            voice_id: character.voice_id
          })
          
          // Update session ID if new
          if (response.session_id && !sessionId) {
            setSessionId(response.session_id)
            console.log('✅ Session created for welcome:', response.session_id)
          }
          
          // Set response data
          setCurrentResponse(response.dialogue)
          setCharacterEmotion(response.emotion)
          
          console.log('Welcome chat response:', { 
            dialogue: response.dialogue, 
            emotion: response.emotion, 
            audioLength: response.audio?.length 
          })
          
          if (response.audio) {
            console.log('Setting welcome audio, length:', response.audio.length)
            setCurrentAudio(response.audio)
            setShouldStartTyping(false) // Wait for audio to start
          } else {
            console.log('No audio in welcome response')
            setShouldStartTyping(true) // No audio, start typing immediately
          }
          
          // Add the welcome message to history as assistant message
          const welcomeHistoryMessage: ChatMessage = {
            role: 'assistant',
            content: response.dialogue,
            timestamp: new Date().toISOString()
          }
          setMessages([welcomeHistoryMessage])
        }
        
      } catch (error) {
        console.error('Failed to generate welcome message:', error)
        // Fallback to simple welcome message
        setCurrentResponse(welcomeMessage)
        setCharacterEmotion('happy')
        setShouldStartTyping(true)
      } finally {
        setIsThinking(false)
      }
    }

    // Delay welcome message generation
    const timer = setTimeout(generateWelcome, 1000)
    return () => clearTimeout(timer)
    
  }, [character, welcomeGenerated, sessionId, showSessionModal, isLoadingSessionData])

  const handleContinueSession = async (selectedSessionId: string) => {
    try {
      console.log('Continuing session:', selectedSessionId)
      const continueResponse = await ApiClient.continueSession(selectedSessionId, 'demo_user')
      
      if (continueResponse.success) {
        setSessionId(selectedSessionId)
        
        // Load previous messages if any
        if (continueResponse.data.session.messages.length > 0) {
          const loadedMessages = continueResponse.data.session.messages.map(msg => ({
            id: msg.id,
            role: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: msg.timestamp
          }))
          setMessages(loadedMessages)
        }
        
        // Show last assistant response if available
        if (continueResponse.data.last_qa.assistant_message) {
          setCurrentResponse(continueResponse.data.last_qa.assistant_message)
          setShouldStartTyping(true)
        }
        
        console.log('Session continued successfully:', {
          session_id: selectedSessionId,
          message_count: continueResponse.data.session.message_count
        })
      }
    } catch (error) {
      console.error('Failed to continue session:', error)
      // Fall back to new session
      handleCreateNewSession()
    } finally {
      setWelcomeGenerated(true) // Prevent welcome generation
    }
  }

  const handleCreateNewSession = () => {
    // Clear any existing session data
    setSessionId(null)
    setMessages([])
    setCurrentResponse('')
    setCurrentAudio(null)
    setWelcomeGenerated(false) // Allow welcome generation
    
    console.log('🔄 Starting new session - welcome generation allowed')
  }

  const handleDeleteSession = async (sessionIdToDelete: string) => {
    try {
      console.log('Delete session requested:', sessionIdToDelete)
      
      // Call the API to delete the session
      await ApiClient.deleteSession(sessionIdToDelete, 'demo_user')
      
      // Refresh the session data after successful deletion
      if (character) {
        await checkForExistingSessions(character.id)
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }

  const handleSend = async (message?: string) => {
    const textToSend = message || inputText.trim()
    if (!textToSend || !character) return
    
    // Mark user interaction for autoplay
    setUserHasInteracted(true)
    
    // Clear input and show user message
    setInputText('')
    setIsTyping(false)
    setLastUserMessage(textToSend)
    
    // Add user message to history
    const userMessage: ChatMessage = {
      role: 'user',
      content: textToSend,
      timestamp: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    
    // Show thinking state  
    setIsThinking(true)
    setCurrentResponse('')
    setCurrentAudio(null) // Clear previous audio when starting new message
    setShouldStartTyping(false)
    
    try {
      // Use session-based chat API with memory
      const response: ChatResponse = await ApiClient.chatWithSession({
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
      
      // Set response data
      setCurrentResponse(response.dialogue)
      setCharacterEmotion(response.emotion)
      
      // Handle tools if present
      if (response.tools && response.tools.length > 0) {
        console.log('Tools received:', response.tools)
        
        // Check if we received a continuous_quiz_response tool
        const continuousQuizTool = response.tools.find(tool => tool.type === 'continuous_quiz_response')
        if (continuousQuizTool) {
          console.log('🎯 Received continuous_quiz_response from regular chat - processing directly')
          // Don't set currentTools, process continuous response directly
          handleContinuousQuizResponse(response, continuousQuizTool)
          return // Exit early, don't set currentTools
        }
        
        setCurrentTools(response.tools)
      } else {
        setCurrentTools([])
      }
      
      console.log('Chat response:', { 
        dialogue: response.dialogue, 
        emotion: response.emotion, 
        audioLength: response.audio?.length,
        tools: response.tools 
      })
      
      if (response.audio) {
        console.log('Setting chat audio, length:', response.audio.length)
        setCurrentAudio(response.audio)
        // Don't start typing until audio starts playing
        setShouldStartTyping(false)
      } else {
        console.log('No audio in chat response')
        // No audio, start typing immediately
        setShouldStartTyping(true)
      }
      
      // Add assistant message to history
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.dialogue,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, assistantMessage])
      
    } catch (error) {
      console.error('Chat error:', error)
      setCurrentResponse('죄송해요, 잠시 문제가 있어요.')
      setCharacterEmotion('neutral')
      setShouldStartTyping(true)
    } finally {
      setIsThinking(false)
    }
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
  
  const handleToolSelection = (selection: string) => {
    console.log('🔧 UNIVERSAL TOOL HANDLER - handleToolSelection called with:', selection)
    
    const currentTool = currentTools[0]
    if (!currentTool) {
      console.log('📝 No current tool - using regular message send')
      handleSend(selection)
      return
    }
    
    console.log('🔍 Tool analysis:', {
      toolType: currentTool.type,
      toolData: currentTool.data,
      hasCorrectAnswer: currentTool.data?.correct_answer !== undefined,
      hasContinuousFlow: currentTool.data?.continuous_flow_enabled || false
    })
    
    // FIXED: Always use regular handleSend for ALL tools
    // The handleSend function now has continuous_quiz_response detection built-in
    // This eliminates the conflict between old and new continuous flow systems
    console.log('📝 Using handleSend for all tool selections (continuous quiz response handled inside)')
    setCurrentTools([])
    handleSend(selection)
  }

  const triggerContinuousFlow = async (flowData: {
    toolType: string
    selection: string
    correctAnswer: string
    question: string
    items: string[]
  }) => {
    try {
      if (!sessionId) {
        console.error('❌ No session ID for continuous flow')
        return
      }

      // ISSUE 1 FIX: Show thinking state during flow processing
      console.log('🔄 Triggering continuous flow - showing thinking state')
      setIsThinking(true)
      setCurrentResponse('')
      setCurrentAudio(null)
      setShouldStartTyping(false)

      console.log('🔄 Triggering continuous flow:', flowData)
      
      const response = await fetch(`${API_BASE_URL}/api/platform-chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: flowData.selection, // The user's quiz answer
          character_id: characterId,
          session_id: sessionId,
          user_id: "demo_user"
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('✅ Continuous flow triggered:', result)

      // ISSUE 1 FIX: Hide thinking state now that we have response
      setIsThinking(false)

      // Handle continuous quiz response from ToolOrchestrator
      let continuousResponseTool = null;
      
      // Check for continuous_quiz_response tool in the modern ToolOrchestrator format
      if (result.tools && result.tools.length > 0) {
        continuousResponseTool = result.tools.find(tool => tool.type === 'continuous_quiz_response');
      }
      
      if (continuousResponseTool) {
        console.log('🎯 Processing continuous quiz response tool:', continuousResponseTool);
        handleContinuousQuizResponse(result, continuousResponseTool);
      } else {
        console.log('❌ No continuous_quiz_response tool found. Tools available:', result.tools?.map(t => t.type));
        // Fallback: Check for show_selection tool (single-phase response)
        const showSelectionTool = result.tools?.find((tool: any) => tool.type === 'show_selection');
        if (showSelectionTool) {
          console.log('📝 Found show_selection tool, handling as single-phase response');
          // Handle single-phase response
          if (result.dialogue) {
            const assistantMessage: ChatMessage = {
              id: Date.now().toString(),
              role: 'assistant',
              content: result.dialogue,
              timestamp: new Date().toISOString(),
              character: characterId,
              audioUrl: result.audio_url
            }
            setMessages(prev => [...prev, assistantMessage]);
          }
          if (showSelectionTool) {
            setCurrentTools([showSelectionTool]);
          }
        } else {
          console.log('🔍 Available tools:', result.tools);
          // Just show dialogue if no recognized tools
          if (result.dialogue) {
            const assistantMessage: ChatMessage = {
              id: Date.now().toString(),
              role: 'assistant',
              content: result.dialogue,
              timestamp: new Date().toISOString(),
              character: characterId,
              audioUrl: result.audio_url
            }
            setMessages(prev => [...prev, assistantMessage]);
          }
        }
      }

      // Tools already cleared before calling this function
      
    } catch (error) {
      console.error('❌ Error triggering continuous flow:', error)
      // ISSUE 1 FIX: Hide thinking state on error too
      setIsThinking(false)
      // Fallback to normal behavior 
      handleSend(flowData.selection)
    }
  }

  const handleContinuousQuizResponse = (response: any, tool: any) => {
    console.log('🎯 Handling continuous quiz response:', tool)
    
    const toolData = tool.data
    
    // Phase 1: Show feedback with audio
    if (toolData.phase1) {
      setCurrentResponse(toolData.phase1.text)
      setShouldStartTyping(true)
      
      // 🚀 PRIORITY 2 OPTIMIZATION: Stream-Ready TTS Playback
      // Start Phase 1 audio immediately
      if (toolData.phase1.audio_url) {
        console.log('🎵 Starting Phase 1 TTS playback immediately')
        setCurrentAudio(toolData.phase1.audio_url)
      }
      
      // 🚀 CRITICAL OPTIMIZATION: Pre-generate Phase 2 TTS in parallel
      // Don't wait for Phase 1 to complete - start Phase 2 TTS generation now
      if (toolData.phase2) {
        console.log('🚀 Pre-generating Phase 2 TTS in parallel with Phase 1 playback')
        
        // Store phase 2 data with TTS ready status
        setPendingContinuousResponse({
          phase2: toolData.phase2,
          delay: toolData.phase1.delay_ms || 3000,
          phase2TtsReady: !!toolData.phase2.audio_url, // TTS already generated by backend
          phase2AudioUrl: toolData.phase2.audio_url
        })
        
        console.log('📊 TTS Generation Status:', {
          phase1Ready: !!toolData.phase1.audio_url,
          phase2Ready: !!toolData.phase2.audio_url,
          phase1Playing: !!toolData.phase1.audio_url,
          phase2Queued: true
        })
      } else {
        // No phase 2, clear pending response
        setPendingContinuousResponse(null)
      }

      // Add phase 1 to message history
      const phase1Message = {
        role: 'assistant' as const,
        content: toolData.phase1.text,
        timestamp: Date.now().toString(),
        audio_url: toolData.phase1.audio_url
      }
      setMessages(prev => [...prev, phase1Message])
    }
  }
  
  const processPhase2 = (phase2Data: any, preGeneratedAudioUrl?: string) => {
    console.log('⏭️ Processing phase 2:', phase2Data)
    console.log('🚀 Pre-generated audio available:', !!preGeneratedAudioUrl)
    
    if (phase2Data) {
      // Use phase2 text directly (already contains quiz question from backend)
      // No need to combine with question again - causes duplication
      setCurrentResponse(phase2Data.text)
      setShouldStartTyping(true)
      
      // 🚀 PRIORITY 2 OPTIMIZATION: Use pre-generated TTS if available
      const audioUrl = preGeneratedAudioUrl || phase2Data.audio_url
      if (audioUrl) {
        console.log('🎵 Starting Phase 2 TTS playback (pre-generated:', !!preGeneratedAudioUrl, ')')
        setCurrentAudio(audioUrl)
      } else {
        console.log('⚠️ No Phase 2 audio available')
      }

      // Show tools after phase 2 audio or immediately if no audio
      if (phase2Data.tool) {
        console.log('🔍 Phase 2 tool data:', phase2Data.tool)
        console.log('🔍 Phase 2 tool data.options:', phase2Data.tool.data?.options)
        console.log('🔍 Phase 2 tool data.items:', phase2Data.tool.data?.items)
        setTimeout(() => {
          setCurrentTools([phase2Data.tool])
          console.log('🎯 Phase 2 quiz tools displayed:', [phase2Data.tool])
          console.log('🎯 currentTools[0].data.options:', phase2Data.tool.data?.options)
        }, phase2Data.audio_url ? 1000 : 0)
      }

      // Add phase 2 to message history
      const phase2Message = {
        role: 'assistant' as const,
        content: phase2Data.text,
        timestamp: Date.now().toString(),
        audio_url: phase2Data.audio_url
      }
      setMessages(prev => [...prev, phase2Message])
    }
  }

  const handleFlowStepComplete = async (stepId: string) => {
    console.log('🏁 First audio completed, checking for flow continuation')
    console.log('🔧 DEBUG: handleFlowStepComplete called with stepId:', stepId)
    console.log('🔧 DEBUG: activeContinuousFlow:', activeContinuousFlow)
    console.log('🔧 DEBUG: secondPhaseContent exists:', !!(window as any).secondPhaseContent)
    
    // Check if we have stored second phase content (legacy approach)
    if ((window as any).secondPhaseContent) {
      console.log('✅ Using stored second phase content (legacy)')
      
      const { dialogue, tools } = (window as any).secondPhaseContent
      
      // Display second phase dialogue text
      setCurrentResponse(dialogue)
      setShouldStartTyping(true)
      
      // Add second dialogue to messages for conversation history
      const secondMessage = {
        role: 'assistant' as const,
        content: dialogue,
        character: 'Assistant',
        emotion: 'encouraging',
        timestamp: Date.now().toString()
      }
      setMessages(prev => [...prev, secondMessage])
      
      // Generate TTS audio for second phase dialogue
      try {
        if (character) {
          const ttsResponse = await ApiClient.textToSpeech(dialogue, character.voice_id, 'encouraging', character.id)
          setCurrentAudio(ttsResponse.audio_base64 || null)
        }
        console.log('🎵 Second phase audio generated')
      } catch (error) {
        console.error('Failed to generate second phase TTS:', error)
      }
      
      // Display quiz tools after slight delay to allow text to start
      setTimeout(() => {
        try {
          setCurrentTools(tools)
          console.log('🎯 Second phase quiz tools displayed:', tools)
        } catch (error) {
          console.error('❌ Error setting current tools in handleFlowStepComplete:', error)
        }
      }, 1000)
      
      // Clean up stored content
      ;(window as any).secondPhaseContent = null
      
      // Clear continuous flow state
      setActiveContinuousFlow(null)
      
    } else if (activeContinuousFlow && activeContinuousFlow.nextStepIndex !== null) {
      // NEW: Multi-step flow approach - trigger next step
      console.log('🔄 Triggering next step in continuous flow:', activeContinuousFlow.nextStepIndex)
      
      try {
        setIsThinking(true)
        
        const progressResponse = await fetch(`${API_BASE_URL}/api/continuous-flow/progress`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: activeContinuousFlow.sessionId,
            trigger_type: 'audio_completion',
            step_index: activeContinuousFlow.nextStepIndex
          })
        })
        
        if (!progressResponse.ok) {
          throw new Error(`HTTP error! status: ${progressResponse.status}`)
        }
        
        const progressResult = await progressResponse.json()
        console.log('✅ Next step triggered:', progressResult)
        
        setIsThinking(false)
        
        if (progressResult.step_result) {
          // Handle the next step result (should contain retry quiz with tools)
          // Handle continuous quiz response
          if (progressResult.tools && progressResult.tools[0]?.type === 'continuous_quiz_response') {
            handleContinuousQuizResponse(progressResult, progressResult.tools[0])
          }
          
          // Clear continuous flow state to prevent infinite loop
          setActiveContinuousFlow(null)
        }
        
      } catch (error) {
        console.error('❌ Error progressing continuous flow:', error)
        setIsThinking(false)
        setActiveContinuousFlow(null)
      }
      
    } else {
      console.log('❌ No second phase content or flow continuation available')
      setActiveContinuousFlow(null)
    }
  }

  const [recordingState, setRecordingState] = useState<'idle' | 'requesting' | 'recording'>('idle')
  const [audioLevel, setAudioLevel] = useState(0)
  const audioContextRef = useRef<AudioContext | null>(null)
  const animationFrameRef = useRef<number | null>(null)

  const startRecording = async () => {
    try {
      // Mark user interaction for autoplay
      setUserHasInteracted(true)
      
      setRecordingState('requesting')
      console.log('Requesting microphone permission...')
      
      // Request high-quality audio for better STT recognition
      const audioConstraints = { 
        echoCancellation: true,
        noiseSuppression: true,
        autoGainControl: true,
        sampleRate: { ideal: 48000, min: 16000 }, // Higher sample rate
        channelCount: { ideal: 1 }, // Mono for STT
        sampleSize: { ideal: 16 }
      }
      
      console.log('🎤 Requesting microphone with constraints:', audioConstraints)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: audioConstraints })
      
      // Log actual stream settings
      const audioTrack = stream.getAudioTracks()[0]
      const settings = audioTrack.getSettings()
      console.log('🎛️ Actual audio settings:', settings)
      
      // Set up audio level monitoring for visual feedback
      const audioContext = new AudioContext()
      const analyser = audioContext.createAnalyser()
      const microphone = audioContext.createMediaStreamSource(stream)
      const dataArray = new Uint8Array(analyser.frequencyBinCount)
      
      audioContextRef.current = audioContext
      microphone.connect(analyser)
      analyser.fftSize = 256
      
      let isMonitoring = true
      const updateAudioLevel = () => {
        if (!isMonitoring) return
        
        analyser.getByteFrequencyData(dataArray)
        
        // Get volume level using RMS instead of simple average for better sensitivity
        const sum = dataArray.reduce((acc, value) => acc + (value * value), 0)
        const rms = Math.sqrt(sum / dataArray.length)
        
        // Scale and normalize for better visualization (0-100 range)
        const normalizedLevel = Math.min(Math.max(rms * 1.5, 0), 100)
        
        // Audio level updated - reduced logging
        setAudioLevel(Math.round(normalizedLevel))
        
        animationFrameRef.current = requestAnimationFrame(updateAudioLevel)
      }
      
      console.log('Microphone permission granted, starting recording...')
      
      // Check what formats are supported
      const formats = [
        'audio/wav',
        'audio/webm;codecs=opus', 
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus'
      ];
      
      console.log('Supported audio formats:');
      formats.forEach(format => {
        console.log(`  ${format}: ${MediaRecorder.isTypeSupported(format)}`);
      });
      
      // For better STT compatibility, try WAV first, then fallback to WebM
      let mimeType = 'audio/wav';
      if (!MediaRecorder.isTypeSupported('audio/wav')) {
        // Fallback to WebM but we'll need to convert on backend
        mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm';
        console.log('WAV not supported, using WebM (will convert on backend):', mimeType);
      } else {
        console.log('Using WAV format for better STT compatibility');
      }
      
      console.log('Selected mimeType:', mimeType);
      
      const mediaRecorder = new MediaRecorder(stream, { mimeType })
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []
      
      // Add comprehensive recording diagnostics
      console.log('MediaRecorder created:', {
        mimeType: mediaRecorder.mimeType,
        state: mediaRecorder.state,
        audioBitsPerSecond: mediaRecorder.audioBitsPerSecond,
        videoBitsPerSecond: mediaRecorder.videoBitsPerSecond
      })
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data)
          console.log('📼 Audio chunk received:', {
            size: event.data.size,
            type: event.data.type,
            totalChunks: audioChunksRef.current.length,
            totalSize: audioChunksRef.current.reduce((sum, chunk) => sum + chunk.size, 0)
          })
        } else {
          console.warn('⚠️ Empty audio chunk received')
        }
      }
      
      mediaRecorder.onstop = async () => {
        console.log('Recording stopped, processing directly...')
        setRecordingState('idle')
        setAudioLevel(0)
        
        // Stop audio level monitoring
        isMonitoring = false
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
          animationFrameRef.current = null
        }
        
        // Cleanup audio context
        if (audioContextRef.current) {
          await audioContextRef.current.close()
          audioContextRef.current = null
        }
        
        // Show processing state in last message area
        setLastUserMessage('음성을 처리하고 있습니다...')
        
        // Use the same mimeType that was used for recording
        const recordedMimeType = mediaRecorder.mimeType || mimeType
        const audioBlob = new Blob(audioChunksRef.current, { type: recordedMimeType })
        
        console.log('🎙️ Recording complete:', {
          blobSize: audioBlob.size,
          blobType: recordedMimeType,
          chunks: audioChunksRef.current.length
        })
        
        // Check if recording is too short
        const estimatedDuration = audioBlob.size / (16000 * 2)
        
        if (audioBlob.size === 0) {
          console.warn('⚠️ No audio data recorded')
          setLastUserMessage('')
          alert('녹음된 오디오가 없습니다. 다시 시도해주세요.')
          return
        }
        
        // Check minimum recording size (roughly 0.5 seconds)
        if (audioBlob.size < 8000) {
          console.warn('⚠️ Recording too short:', audioBlob.size, 'bytes')
          setLastUserMessage('')
          alert('녹음이 너무 짧습니다. 더 오래 녹음해주세요.')
          return
        }
        
        // Convert to base64 and send directly to STT
        const reader = new FileReader()
        reader.onload = async () => {
          try {
            const base64Audio = (reader.result as string).split(',')[1]
            
            console.log('Sending recording directly to STT API...')
            const sttResponse = await ApiClient.speechToText(base64Audio)
            console.log('STT response:', sttResponse)
            
            if (sttResponse.text && sttResponse.text.trim()) {
              console.log('Speech recognized:', sttResponse.text)
              
              // Stop any current audio playback to prevent restart
              setCurrentAudio(null)
              setIsAudioPlaying(false)
              
              setLastUserMessage(sttResponse.text)
              // Auto-send the recognized text
              await handleSend(sttResponse.text)
            } else {
              console.warn('No speech detected or empty text')
              setLastUserMessage('')
              alert('음성을 인식하지 못했습니다. 다시 시도해주세요.')
            }
          } catch (error) {
            console.error('STT processing error:', error)
            setLastUserMessage('')
            alert('음성 처리 중 오류가 발생했습니다.')
          }
        }
        reader.onerror = (error) => {
          console.error('FileReader error:', error)
          setLastUserMessage('')
          alert('오디오 파일 처리 중 오류가 발생했습니다.')
        }
        reader.readAsDataURL(audioBlob)
        
        // Stop all tracks
        stream.getTracks().forEach(track => {
          track.stop()
          console.log('Media track stopped')
        })
      }
      
      mediaRecorder.onerror = (error) => {
        console.error('MediaRecorder error:', error)
        setRecordingState('idle')
        alert('녹음 중 오류가 발생했습니다.')
      }
      
      // Stop any playing audio to prevent interference during recording
      if (isAudioPlaying) {
        setCurrentAudio(null)
        setIsAudioPlaying(false)
        setShouldStartTyping(false)
        console.log('🔇 Stopped character audio for clear recording')
      }
      
      // Start recording with longer intervals for better quality
      mediaRecorder.start(250) // Collect data every 250ms for better stability
      setRecordingState('recording')
      updateAudioLevel() // Start audio level monitoring
      
      console.log('🔴 Recording started with settings:', {
        interval: '250ms',
        state: mediaRecorder.state,
        streamActive: stream.active,
        audioTracks: stream.getAudioTracks().length
      })
      
    } catch (error) {
      console.error('Error accessing microphone:', error)
      setRecordingState('idle')
      
      const mediaError = error as any
      if (mediaError.name === 'NotAllowedError') {
        alert('마이크 권한이 거부되었습니다. 브라우저 설정에서 마이크 접근을 허용해주세요.')
      } else if (mediaError.name === 'NotFoundError') {
        alert('마이크를 찾을 수 없습니다. 마이크가 연결되어 있는지 확인해주세요.')
      } else {
        alert('마이크 접근 중 오류가 발생했습니다.')
      }
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState === 'recording') {
      console.log('⏹️ Stopping recording...')
      mediaRecorderRef.current.stop()
      setAudioLevel(0) // Reset audio level
      // recordingState는 onstop에서 'idle'로 변경됨
    }
  }

  const cancelRecording = async () => {
    if (recordingState === 'recording' && mediaRecorderRef.current) {
      console.log('Cancelling recording...')
      
      // Stop audio level monitoring immediately
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
      
      // Cleanup audio context
      if (audioContextRef.current) {
        try {
          await audioContextRef.current.close()
          audioContextRef.current = null
        } catch (error) {
          console.warn('Error closing AudioContext:', error)
        }
      }
      
      // Reset states
      setRecordingState('idle')
      setAudioLevel(0)
      
      // Stop the recorder without processing
      mediaRecorderRef.current.onstop = null // Remove the processing handler
      
      try {
        if (mediaRecorderRef.current.state !== 'inactive') {
          mediaRecorderRef.current.stop()
        }
      } catch (error) {
        console.warn('Error stopping MediaRecorder:', error)
      }
      
      // Stop media tracks
      if (mediaRecorderRef.current.stream) {
        mediaRecorderRef.current.stream.getTracks().forEach(track => {
          track.stop()
          console.log('Media track stopped during cancel')
        })
      }
      
      // Clear audio chunks
      audioChunksRef.current = []
    }
  }


  const handleMicClick = () => {
    if (recordingState === 'idle') {
      startRecording()
    } else if (recordingState === 'recording') {
      stopRecording()
    }
    // 'requesting' 상태에서는 아무것도 하지 않음
  }
  
  const handleAudioPlayStart = () => {
    console.log('🎵 Audio play started - setting isAudioPlaying to true')
    setShouldStartTyping(true)
    setIsAudioPlaying(true)
  }
  
  const handleAudioPlayEnd = () => {
    console.log('🎵 Audio play ended - setting isAudioPlaying to false')
    setIsAudioPlaying(false)
    
    // Process pending continuous response if any
    if (pendingContinuousResponse) {
      console.log('🔄 Processing pending continuous response after audio completion')
      console.log('🚀 Phase 2 TTS ready status:', pendingContinuousResponse.phase2TtsReady)
      
      setTimeout(() => {
        // 🚀 PRIORITY 2 OPTIMIZATION: Pass pre-generated audio URL
        processPhase2(
          pendingContinuousResponse.phase2, 
          pendingContinuousResponse.phase2AudioUrl
        )
        setPendingContinuousResponse(null)
      }, pendingContinuousResponse.delay || 3000)
    }
  }
  
  if (characterLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-b from-background to-muted/20">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-lg text-muted-foreground">캐릭터를 불러오고 있습니다...</p>
        </div>
      </div>
    )
  }
  
  if (!character) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center space-y-4">
          <p className="text-xl text-muted-foreground">캐릭터를 찾을 수 없습니다</p>
          <Button onClick={() => router.push('/characters')}>
            캐릭터 목록으로 돌아가기
          </Button>
        </div>
      </div>
    )
  }
  
  return (
    <div className="flex h-screen h-dvh flex-col bg-gradient-to-b from-slate-50 to-slate-100/40">
      {/* Header - Improved with shadcn/ui patterns */}
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-slate-50/95 backdrop-blur supports-[backdrop-filter]:bg-slate-50/60">
        <div className="container flex h-16 max-w-2xl mx-auto items-center justify-between px-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push('/characters')}
            className="h-9 w-9 rounded-full p-0"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="sr-only">뒤로 가기</span>
          </Button>
          
          <div className="flex flex-1 flex-col items-center text-center">
            <h1 className="text-lg font-semibold leading-tight">{character.name}</h1>
            <p className="text-sm text-muted-foreground">{character.description}</p>
          </div>
          
          {/* Logo for 설민석 AI 퀴즈 튜터 - Enlarged for better visibility */}
          <div className="flex h-12 w-16 items-center justify-end">
            {character?.id === 'seol_min_seok_quiz' && (
              <div className="group relative">
                <div className="flex h-14 w-14 items-center justify-center rounded-lg border bg-card p-1 shadow-sm transition-all hover:shadow-md">
                  <img 
                    src="/images/seol_logo.png" 
                    alt="설민석 AI 퀴즈 튜터 로고"
                    className="h-full w-full object-contain transition-transform hover:scale-105"
                    onError={(e) => {
                      const target = e.currentTarget;
                      target.style.display = 'none';
                      const parent = target.parentElement!;
                      parent.innerHTML = '<div class="flex h-full w-full items-center justify-center rounded bg-gradient-to-r from-orange-500 to-orange-600 text-sm font-bold text-white">설</div>';
                    }}
                  />
                </div>
                {/* Tooltip */}
                <div className="absolute -bottom-8 right-0 rounded bg-popover px-2 py-1 text-xs text-popover-foreground opacity-0 shadow-md transition-opacity group-hover:opacity-100">
                  퀴즈 튜터
                </div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main content area - Enhanced with shadcn/ui patterns */}
      <main className="flex flex-1 flex-col items-center justify-center space-y-8 px-6 py-8">
        <div className="flex w-full max-w-2xl flex-col items-center space-y-6 text-center">
          
          {/* Character avatar - Enlarged and improved */}
          <div className="relative">
            {/* Extra Large Thinking wave pulse rings - Reduced shadow */}
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
            
            {/* Extra Large character avatar container */}
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
                        onFlowStepComplete={handleFlowStepComplete}
                        flowContext={activeContinuousFlow ? {
                          sessionId: activeContinuousFlow.sessionId,
                          stepId: activeContinuousFlow.stepId,
                          nextStepTrigger: activeContinuousFlow.nextStepTrigger
                        } : undefined}
                      />
                    </motion.div>
                  )}
                  
                  {/* Quiz UI moved to bottom-right above input - see line 1008 */}
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

      {/* Recording Level Indicator (appears above input) */}
      <AnimatePresence>
        {recordingState === 'recording' && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="px-4 pb-2"
          >
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <div className="flex items-center justify-center gap-3">
                <Mic className="w-5 h-5 text-red-600 animate-pulse" />
                <span className="text-sm font-medium text-red-700 dark:text-red-300">녹음 중</span>
                <div className="flex items-center gap-1">
                  {[...Array(5)].map((_, i) => {
                    const threshold = i * 15;
                    const isActive = audioLevel > threshold;
                    const height = isActive ? Math.min(8 + (audioLevel - threshold) / 3, 20) : 3;
                    return (
                      <div
                        key={i}
                        className={`w-1.5 rounded-full transition-all duration-100 ${
                          isActive ? 'bg-red-500' : 'bg-red-200'
                        }`}
                        style={{
                          height: `${height}px`
                        }}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Quiz UI - Positioned horizontally centered above input */}
      <AnimatePresence>
        {currentTools.length > 0 && currentTools[0].type === 'show_selection' && currentTools[0].data && (
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
              correctAnswer={currentTools[0].data.correct_answer || currentTools[0].data.correctAnswer}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area - Enhanced with shadcn/ui patterns */}
      <footer className="sticky bottom-0 border-t border-border/40 bg-slate-50/95 backdrop-blur supports-[backdrop-filter]:bg-slate-50/60">
        <div className="container max-w-2xl mx-auto px-6 py-4" style={{ paddingBottom: 'max(16px, env(safe-area-inset-bottom))' }}>
          <div className="flex items-end gap-3">
            
            {/* Text input - Enhanced */}
            <div className="flex-1">
              <Input
                value={inputText}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder={
                  recordingState === 'requesting' ? "마이크 권한 요청 중..." :
                  recordingState === 'recording' ? "🎤 녹음 중..." :
                  "메시지 입력..."
                }
                className="h-12 rounded-full border-2 bg-background transition-colors focus:border-primary"
                disabled={isThinking || recordingState !== 'idle'}
              />
            </div>
            
            {/* Mic button - Enhanced */}
            {recordingState === 'idle' ? (
              <Button
                size="icon"
                variant="outline"
                className="h-12 w-12 shrink-0 rounded-full border-2 transition-all hover:border-primary"
                onClick={handleMicClick}
                disabled={isThinking}
                title="음성 입력 시작"
              >
                <Mic className="h-5 w-5" />
                <span className="sr-only">음성 입력 시작</span>
              </Button>
            ) : recordingState === 'requesting' ? (
              <Button
                size="icon"
                variant="outline"
                className="h-12 w-12 shrink-0 rounded-full border-2 opacity-50"
                disabled={true}
                title="마이크 권한 요청 중..."
              >
                <Mic className="h-5 w-5" />
                <span className="sr-only">마이크 권한 요청 중</span>
              </Button>
            ) : recordingState === 'recording' ? (
              <Button
                size="icon"
                className="h-12 w-12 shrink-0 rounded-full border-2 border-primary"
                onClick={stopRecording}
                title="녹음 완료 및 전송"
              >
                <Send className="h-5 w-5" />
                <span className="sr-only">녹음 완료 및 전송</span>
              </Button>
            ) : null}
            
            {/* Send/Cancel button - Enhanced */}
            {recordingState === 'recording' ? (
              <Button
                size="icon"
                variant="destructive"
                className="h-12 w-12 shrink-0 rounded-full border-2"
                onClick={cancelRecording}
                title="녹음 취소"
              >
                <X className="h-5 w-5" />
                <span className="sr-only">녹음 취소</span>
              </Button>
            ) : (
              <Button
                size="icon"
                onClick={() => handleSend()}
                disabled={!inputText.trim() || isThinking || recordingState !== 'idle'}
                className="h-12 w-12 shrink-0 rounded-full border-2 transition-all disabled:opacity-50"
                variant={inputText.trim() && recordingState === 'idle' ? "default" : "outline"}
                title="메시지 전송"
              >
                <Send className="h-5 w-5" />
                <span className="sr-only">메시지 전송</span>
              </Button>
            )}
          </div>
        </div>
      </footer>

      {/* Session Continuation Modal */}
      {sessionData && (
        <SessionContinuationModal
          isOpen={showSessionModal}
          onClose={() => setShowSessionModal(false)}
          sessionData={sessionData}
          onContinueSession={handleContinueSession}
          onCreateNew={handleCreateNewSession}
          onDeleteSession={handleDeleteSession}
          characterName={character.name}
        />
      )}
    </div>
  )
}