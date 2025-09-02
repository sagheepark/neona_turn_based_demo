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
import { ArrowLeft, Send, Mic, MicOff, Loader2, X } from 'lucide-react'
import { TypewriterText } from '@/components/chat/TypewriterText'
import { AudioPlayer } from '@/components/chat/AudioPlayer'
import { SessionContinuationModal } from '@/components/chat/SessionContinuationModal'
import { SessionStartResponse } from '@/lib/api-client'
import { UnifiedSelection } from '@/components/ui/UnifiedSelection'

export default function ChatPage() {
  const params = useParams()
  const router = useRouter()
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

  // Continuous flow state
  const [activeContinuousFlow, setActiveContinuousFlow] = useState<{
    sessionId: string
    flowId: string
    stepId: string
    nextStepTrigger?: string
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
      const characterId = params.characterId as string
      
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
    console.log('🔍 Tool selection debug:', {
      selection,
      characterId,
      currentTools: currentTools,
      currentToolsLength: currentTools.length,
      firstTool: currentTools[0],
      firstToolType: currentTools[0]?.type
    })
    
    // Check if tool supports continuous flow (quiz with seol_min_seok_quiz character)
    const currentTool = currentTools[0]
    
    console.log('🔍 Continuous flow check:', {
      hasCurrentTool: !!currentTool,
      toolType: currentTool?.type,
      isShowSelection: currentTool?.type === 'show_selection',
      characterId,
      isSeolMinSeok: characterId === 'seol_min_seok_quiz',
      shouldTriggerFlow: currentTool?.type === 'show_selection' && characterId === 'seol_min_seok_quiz'
    })
    
    if (currentTool?.type === 'show_selection' && characterId === 'seol_min_seok_quiz') {
      console.log('🚀 Triggering continuous flow for quiz selection')
      // IMPORTANT: Clear tools IMMEDIATELY to prevent race conditions
      setCurrentTools([])
      triggerContinuousFlow({
        toolType: currentTool.type,
        selection,
        correctAnswer: currentTool.data.correctAnswer,
        question: currentTool.data.question,
        items: currentTool.data.items
      })
    } else {
      console.log('❌ Falling back to legacy behavior:', {
        reason: !currentTool ? 'No current tool' : 
                currentTool.type !== 'show_selection' ? `Wrong tool type: ${currentTool.type}` :
                characterId !== 'seol_min_seok_quiz' ? `Wrong character: ${characterId}` : 'Unknown'
      })
      // Legacy behavior for non-continuous flow tools
      setCurrentTools([])
      handleSend(selection)
    }
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

      console.log('🔄 Triggering continuous flow:', flowData)
      
      const response = await fetch('/api/continuous-flow/trigger', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          character_id: characterId,
          tool_type: flowData.toolType,
          data: {
            selection: flowData.selection,
            correct_answer: flowData.correctAnswer,
            question: flowData.question,
            items: flowData.items
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('✅ Continuous flow triggered:', result)

      if (result.step_result) {
        // Display first step (feedback) with audio
        handleFlowStepResult(result)
      }

      // Tools already cleared before calling this function
      
    } catch (error) {
      console.error('❌ Error triggering continuous flow:', error)
      // Fallback to normal behavior 
      handleSend(flowData.selection)
    }
  }

  const handleFlowStepResult = (result: any) => {
    console.log('🎯 Handling flow step result:', result)
    
    const stepResult = result.step_result
    if (!stepResult) return

    // Add the response as a character message
    if (stepResult.response) {
      const dialogue = stepResult.response.dialogue
      
      // Check if this response contains a new quiz question
      const quizPattern = /([A-D])\)\s*([^A-D]+?)(?=[A-D]\)|$)/g
      const hasQuizOptions = quizPattern.test(dialogue)
      
      let cleanDialogue = dialogue
      let newTools = []
      
      if (hasQuizOptions) {
        // Extract the question part (before first option)
        const questionMatch = dialogue.match(/^(.*?)A\)/s)
        if (questionMatch) {
          cleanDialogue = questionMatch[1].trim()
        }
        
        // Extract options
        const options = []
        const optionMatches = [...dialogue.matchAll(/([A-D])\)\s*([^A-D]+?)(?=[A-D]\)|$)/g)]
        
        optionMatches.forEach(match => {
          options.push(match[2].trim())
        })
        
        if (options.length > 0) {
          // Create new quiz tool for the next question
          newTools = [{
            type: 'show_selection',
            data: {
              question: cleanDialogue,
              items: options,
              correctAnswer: options[0], // For demo, assume first option is correct
              metadata: {
                type: 'quiz',
                topic: '조선시대',
                difficulty: 'medium'
              }
            }
          }]
          
          console.log('🎯 Generated new quiz tools from flow response:', newTools)
        }
      }

      const newMessage = {
        role: 'assistant',
        content: cleanDialogue,
        character: stepResult.response.character,
        emotion: stepResult.response.emotion || 'normal',
        timestamp: Date.now(),
        audio: stepResult.audio
      }

      setMessages(prev => [...prev, newMessage])
      
      // Set character emotion
      setCharacterEmotion(stepResult.response.emotion || 'normal')
      
      // Set new quiz tools if found
      if (newTools.length > 0) {
        setCurrentTools(newTools)
      }
      
      // Set audio with flow context if available
      if (stepResult.audio) {
        console.log('🎵 Setting flow step audio')
        setCurrentAudio(stepResult.audio)
        
        // Set up continuous flow context for audio completion
        if (result.flow_continues && stepResult.next_trigger === 'audio_completion') {
          setActiveContinuousFlow({
            sessionId: result.session_id,
            flowId: 'quiz_continuous_v1', // TODO: Get from result
            stepId: stepResult.step_id,
            nextStepTrigger: stepResult.next_trigger
          })
        }
      }
    }
  }

  const handleFlowStepComplete = async (stepId: string) => {
    console.log('🏁 Flow step completed:', stepId)
    
    if (!activeContinuousFlow || !sessionId) {
      console.log('❌ No active flow to progress')
      return
    }

    try {
      console.log('⏭️  Progressing continuous flow')
      
      const response = await fetch('/api/continuous-flow/progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          trigger_type: 'audio_completion',
          data: {
            completed_step_id: stepId
          }
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      console.log('✅ Flow progressed:', result)

      if (result.step_result) {
        // Handle next step result
        handleFlowStepResult(result)
      }

      if (!result.flow_continues) {
        // Flow completed
        console.log('🏆 Continuous flow completed')
        setActiveContinuousFlow(null)
      }

    } catch (error) {
      console.error('❌ Error progressing continuous flow:', error)
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
      
      if (error.name === 'NotAllowedError') {
        alert('마이크 권한이 거부되었습니다. 브라우저 설정에서 마이크 접근을 허용해주세요.')
      } else if (error.name === 'NotFoundError') {
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
    setShouldStartTyping(true)
    setIsAudioPlaying(true)
  }
  
  const handleAudioPlayEnd = () => {
    setIsAudioPlaying(false)
    // Don't clear currentAudio so player UI stays visible for replay
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
    <div className="h-screen h-dvh flex flex-col relative bg-gradient-to-b from-background to-muted/5 max-w-md mx-auto">
      {/* Header with back button */}
      <div className="flex items-center justify-between p-4 border-b bg-background/80 backdrop-blur-sm">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push('/characters')}
          className="rounded-full"
        >
          <ArrowLeft className="w-4 h-4" />
        </Button>
        
        <div className="text-center">
          <h2 className="font-semibold">{character.name}</h2>
          <p className="text-xs text-muted-foreground">{character.description}</p>
          {sessionId && (
            <p className="text-xs text-gray-400">Session: {sessionId.slice(0, 12)}...</p>
          )}
        </div>
        
        <div className="w-10" /> {/* Spacer for centering */}
      </div>

      {/* Main content area - Character response */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm text-center">
          
          {/* Character avatar */}
          <div className="relative w-24 h-24 mx-auto mb-6">
            {/* Thinking wave pulse rings */}
            {isThinking && (
              <div className="absolute inset-0">
                {[...Array(3)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute inset-0 rounded-full border-2 border-gray-400"
                    initial={{ scale: 1, opacity: 0.6 }}
                    animate={{ 
                      scale: [1, 2.5], 
                      opacity: [0.6, 0.3, 0] 
                    }}
                    transition={{
                      duration: 2,
                      delay: i * 0.6,
                      repeat: Infinity,
                      ease: "easeOut"
                    }}
                  />
                ))}
              </div>
            )}
            
            <div 
              className={`w-full h-full rounded-full overflow-hidden bg-muted flex items-center justify-center transition-all duration-300 ${
                isAudioPlaying 
                  ? 'ring-2 ring-blue-500 ring-offset-2 ring-offset-background' 
                  : ''
              }`}
            >
              {character.image ? (
                <img 
                  src={character.image} 
                  alt={character.name}
                  className="w-full h-full object-cover object-top"
                  style={{ aspectRatio: 'auto' }}
                />
              ) : (
                <span className="text-3xl font-bold text-muted-foreground">
                  {character.name[0]?.toUpperCase()}
                </span>
              )}
            </div>
          </div>

          {/* Response area */}
          <div className="min-h-[120px] flex items-center justify-center">
            <AnimatePresence mode="wait">
              {isThinking ? (
                <motion.div
                  key="thinking"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="flex items-center gap-3 text-muted-foreground"
                >
                  <Loader2 className="w-5 h-5 animate-spin" />
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
                  className="text-muted-foreground text-lg"
                >
                  대화를 시작해보세요...
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>

      {/* Last user message display (appears when typing/recording/processing) - Hidden during quiz */}
      <AnimatePresence>
        {(lastUserMessage && (!isTyping || lastUserMessage.includes('처리하고')) && !(currentTools.length > 0 && currentTools[0].type === 'show_selection')) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="px-4 pb-2"
          >
            <div className={`rounded-lg px-4 py-2 text-sm ${
              lastUserMessage.includes('처리하고') 
                ? 'bg-blue-100 text-blue-800 animate-pulse' 
                : 'bg-secondary/50 text-muted-foreground'
            }`}>
              {lastUserMessage.includes('처리하고') && (
                <span className="mr-2">⏳</span>
              )}
              {lastUserMessage}
            </div>
          </motion.div>
        )}
      </AnimatePresence>


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
        {currentTools.length > 0 && currentTools[0].type === 'show_selection' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-24 left-1/2 transform -translate-x-1/2 max-w-md z-50"
          >
            <UnifiedSelection
              items={currentTools[0].data.items}
              onSelect={handleToolSelection}
              question={currentTools[0].data.question}
              correctAnswer={currentTools[0].data.correctAnswer}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <div className="border-t bg-background/90 backdrop-blur-sm p-4"
           style={{ paddingBottom: 'max(16px, env(safe-area-inset-bottom))' }}>
        <div className="flex gap-3 items-end">
          
          {/* Text input */}
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
              className="rounded-full bg-background border-2 transition-colors focus:border-primary h-12"
              disabled={isThinking || recordingState !== 'idle'}
            />
          </div>
          
          {/* Left button - Mic/Send during recording */}
          {recordingState === 'idle' ? (
            <Button
              size="icon"
              variant="outline"
              className="rounded-full h-12 w-12 border-2 transition-all"
              onClick={handleMicClick}
              disabled={isThinking}
              title="음성 입력 시작"
            >
              <Mic className="w-5 h-5" />
            </Button>
          ) : recordingState === 'requesting' ? (
            <Button
              size="icon"
              variant="outline"
              className="rounded-full h-12 w-12 border-2 opacity-50"
              disabled={true}
              title="마이크 권한 요청 중..."
            >
              <Mic className="w-5 h-5" />
            </Button>
          ) : recordingState === 'recording' ? (
            <Button
              size="icon"
              variant="default"
              className="rounded-full h-12 w-12 border-2 bg-black hover:bg-gray-800 text-white"
              onClick={stopRecording}
              title="녹음 완료 및 전송"
            >
              <Send className="w-5 h-5" />
            </Button>
          ) : null}
          
          {/* Right button - Send/Cancel during recording */}
          {recordingState === 'recording' ? (
            <Button
              size="icon"
              variant="destructive"
              className="rounded-full h-12 w-12 border-2 bg-red-500 hover:bg-red-600"
              onClick={cancelRecording}
              title="녹음 취소"
            >
              <X className="w-5 h-5" />
            </Button>
          ) : (
            <Button
              size="icon"
              onClick={() => handleSend()}
              disabled={!inputText.trim() || isThinking || recordingState !== 'idle'}
              className="rounded-full h-12 w-12 border-2"
              variant={inputText.trim() && recordingState === 'idle' ? "default" : "outline"}
              title="메시지 전송"
            >
              <Send className="w-5 h-5" />
            </Button>
          )}
        </div>
      </div>

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