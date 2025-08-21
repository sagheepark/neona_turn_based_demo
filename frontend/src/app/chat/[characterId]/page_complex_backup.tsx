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
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'

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

  const [welcomeGenerated, setWelcomeGenerated] = useState(false)
  
  // Session states
  const [showSessionModal, setShowSessionModal] = useState(false)
  const [previousSessions, setPreviousSessions] = useState<any[]>([])
  const [currentSession, setCurrentSession] = useState<any>(null)
  
  // Debug session modal state - only log when modal state actually changes
  const previousModalState = useRef({ showSessionModal: false, sessionsCount: 0 })
  
  useEffect(() => {
    const currentState = { showSessionModal, sessionsCount: previousSessions.length }
    const prevState = previousModalState.current
    
    if (prevState.showSessionModal !== currentState.showSessionModal || 
        prevState.sessionsCount !== currentState.sessionsCount) {
      console.log('🎭 Session modal state changed:', {
        from: prevState,
        to: currentState
      })
      previousModalState.current = currentState
    }
  }, [showSessionModal, previousSessions.length])

  useEffect(() => {
    const characterId = params.characterId as string
    const char = CharacterStorage.getById(characterId)
    
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
    
    // Check for existing sessions
    checkForExistingSessions(characterId)
    
  }, [params.characterId, router]) // Removed welcomeGenerated dependency

  // Check for existing sessions
  const checkForExistingSessions = async (characterId: string) => {
    console.log('🔍 Checking for existing sessions for character:', characterId)
    try {
      const url = `http://localhost:8000/api/sessions/demo_user/${characterId}`
      console.log('📡 Fetching sessions from:', url)
      const response = await fetch(url)
      console.log('📡 Response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('📡 Session data received:', data)
        if (data.success && data.sessions?.length > 0) {
          console.log('✅ Found', data.sessions.length, 'existing sessions - showing modal')
          setPreviousSessions(data.sessions)
          setShowSessionModal(true)
          console.log('🎭 Modal state set to true, previousSessions:', data.sessions.length)
          return // Don't generate welcome message yet
        } else {
          console.log('ℹ️ No sessions found for this character')
        }
      } else {
        console.log('❌ Session API returned error status:', response.status)
      }
    } catch (error) {
      console.log('❌ Error checking sessions:', error)
    }
    // No sessions found, create a new session for this chat
    console.log('➡️ No sessions found, creating new session automatically')
    await createNewSessionAutomatically(characterId)
  }

  const createNewSessionAutomatically = async (characterId: string) => {
    try {
      console.log('🆕 Auto-creating new session for character:', characterId)
      
      // Mark user interaction for autoplay permission (user navigated to chat)
      setUserHasInteracted(true)
      
      const response = await fetch(`http://localhost:8000/api/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          character_id: characterId,
          persona_id: null
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          console.log('📦 Session creation response structure:', data.data)
          setCurrentSession(data.data)
          console.log('✅ Auto-created session:', data.data.session?.session_id || 'Session structure issue')
          console.log('🔍 CurrentSession after set:', data.data)
        }
      }
    } catch (error) {
      console.error('❌ Error auto-creating session:', error)
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

  // Separate effect for welcome message generation to prevent duplicate calls
  useEffect(() => {
    console.log('Welcome effect triggered:', { character: character?.name, welcomeGenerated, showSessionModal, currentSession: currentSession?.session_id || currentSession?.session?.session_id })
    if (!character || welcomeGenerated || showSessionModal) return
    
    const generateWelcome = async () => {
      console.log('Starting welcome generation for:', character.name)
      const welcomeMessage = `안녕하세요! 저는 ${character.name}입니다. ${character.description}. 궁금한 것이 있으시면 언제든지 물어보세요!`
      
      // Show thinking state briefly
      setIsThinking(true)
      setWelcomeGenerated(true) // Prevent duplicate calls
      
      try {
        let response: ChatResponse;
        
        // Use session API if we have an active session, otherwise use regular chat API
        const sessionId = currentSession?.session_id || currentSession?.session?.session_id
        if (currentSession && sessionId) {
          console.log('💬 Using session-aware welcome message for session:', sessionId)
          
          const sessionResponse = await fetch(`http://localhost:8000/api/sessions/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              session_id: sessionId,
              user_id: 'demo_user',
              message: '안녕하세요',
              character_id: character.id
            })
          })
          
          if (!sessionResponse.ok) {
            throw new Error(`Session welcome API failed: ${sessionResponse.status}`)
          }
          
          const sessionData = await sessionResponse.json()
          console.log('📝 Session welcome response:', sessionData)
          
          // Transform session response to ChatResponse format
          response = {
            dialogue: sessionData.data?.ai_response || `안녕하세요! 저는 ${character.name}입니다.`,
            emotion: sessionData.data?.emotion || 'happy',
            audio: null // Session API may not include TTS yet
          }
        } else {
          console.log('💬 Using session-based chat API for welcome message')
          // Use session-based chat API with memory
          response = await ApiClient.chatWithSession({
            message: '안녕하세요', // Simple greeting to trigger welcome
            character_prompt: character.prompt,
            character_id: character.id,
            user_id: 'user123',
            voice_id: character.voice_id
          })
          
          // Update session state
          if (response.session_id) {
            setCurrentSession({ session_id: response.session_id })
          }
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
    
  }, [character, welcomeGenerated, showSessionModal])

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
    setCurrentAudio(null)
    setShouldStartTyping(false)
    
    try {
      let response: ChatResponse;
      
      // Debug current session structure
      console.log('🔍 Current session structure:', {
        hasCurrentSession: !!currentSession,
        currentSession: currentSession,
        sessionId: currentSession?.session_id || currentSession?.session?.session_id
      })
      
      // Use session-aware endpoint if we have an active session
      // Support both direct session_id and nested session.session_id structures
      const sessionId = currentSession?.session_id || currentSession?.session?.session_id
      if (currentSession && sessionId) {
        console.log('💬 Using session-aware message API for session:', sessionId)
        
        const sessionResponse = await fetch(`http://localhost:8000/api/sessions/message`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: sessionId,
            user_id: 'demo_user',
            message: textToSend,
            character_id: character.id,
            character_prompt: character.prompt
          })
        })
        
        if (!sessionResponse.ok) {
          throw new Error(`Session message API failed: ${sessionResponse.status}`)
        }
        
        const sessionData = await sessionResponse.json()
        console.log('📝 Session message response:', sessionData)
        
        // Transform session response to ChatResponse format and generate TTS
        const dialogue = sessionData.data?.ai_response || sessionData.data?.response || textToSend + ' (response pending)'
        const emotion = sessionData.data?.emotion || 'neutral'
        
        // Generate TTS for session response
        try {
          console.log('🎵 Generating TTS for session response:', dialogue.substring(0, 50) + '...')
          
          const ttsResponse = await fetch(`http://localhost:8000/api/tts`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              text: dialogue,
              voice_id: character.voice_id || "tc_61c97b56f1b7877a74df625b",
              emotion: emotion,
              speed: 1.0,
              character_id: character.id
            })
          })
          
          if (ttsResponse.ok) {
            const ttsData = await ttsResponse.json()
            console.log('🎵 Session TTS Response:', { status: ttsData.status, hasAudio: !!ttsData.audio, audioLength: ttsData.audio?.length })
            if (ttsData.status === 'success' && ttsData.audio) {
              console.log('✅ TTS generated for session response, length:', ttsData.audio.length)
              response = {
                dialogue: dialogue,
                emotion: emotion,
                audio: ttsData.audio
              }
            } else {
              console.log('❌ No audio in session TTS response')
              response = {
                dialogue: dialogue,
                emotion: emotion,
                audio: null
              }
            }
          } else {
            console.log('⚠️ TTS API call failed for session response')
            response = {
              dialogue: dialogue,
              emotion: emotion,
              audio: null
            }
          }
        } catch (ttsError) {
          console.error('❌ TTS error for session response:', ttsError)
          response = {
            dialogue: dialogue,
            emotion: emotion,
            audio: null
          }
        }
      } else {
        console.log('⚠️ No active session detected, creating one first...')
        
        // Create session before sending message
        const createResponse = await fetch(`http://localhost:8000/api/sessions/create`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: 'demo_user',
            character_id: character.id,
            persona_id: null
          })
        })
        
        if (createResponse.ok) {
          const createData = await createResponse.json()
          if (createData.success) {
            console.log('🆕 Session created on-demand:', createData.data.session?.session_id)
            setCurrentSession(createData.data)
            
            // Now send message with the new session
            const sessionResponse = await fetch(`http://localhost:8000/api/sessions/message`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                session_id: createData.data.session.session_id,
                user_id: 'demo_user',
                message: textToSend,
                character_id: character.id,
                character_prompt: character.prompt
              })
            })
            
            if (sessionResponse.ok) {
              const sessionData = await sessionResponse.json()
              const dialogue = sessionData.data?.ai_response || textToSend + ' (response pending)'
              const emotion = sessionData.data?.emotion || 'neutral'
              
              // Generate TTS
              try {
                const ttsResponse = await fetch(`http://localhost:8000/api/tts`, {
                  method: 'POST',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({
                    text: dialogue,
                    voice_id: character.voice_id || "tc_61c97b56f1b7877a74df625b",
                    emotion: emotion,
                    speed: 1.0,
                    character_id: character.id
                  })
                })
                
                if (ttsResponse.ok) {
                  const ttsData = await ttsResponse.json()
                  console.log('🎵 TTS Response:', { status: ttsData.status, hasAudio: !!ttsData.audio, audioLength: ttsData.audio?.length })
                  if (ttsData.status === 'success' && ttsData.audio) {
                    response = {
                      dialogue: dialogue,
                      emotion: emotion,
                      audio: ttsData.audio
                    }
                    console.log('✅ Audio set in response, length:', ttsData.audio.length)
                  } else {
                    console.log('❌ No audio in TTS response or failed status')
                    response = {
                      dialogue: dialogue,
                      emotion: emotion,
                      audio: null
                    }
                  }
                } else {
                  response = {
                    dialogue: dialogue,
                    emotion: emotion,
                    audio: null
                  }
                }
              } catch (ttsError) {
                console.error('❌ TTS error:', ttsError)
                response = {
                  dialogue: dialogue,
                  emotion: emotion,
                  audio: null
                }
              }
            } else {
              throw new Error('Failed to send message to new session')
            }
          } else {
            throw new Error('Failed to create session')
          }
        } else {
          // Use session-based chat API with memory
          console.log('💬 Using session-based chat API for conversation')
          response = await ApiClient.chatWithSession({
            message: textToSend,
            character_prompt: character.prompt,
            character_id: character.id,
            user_id: 'user123',
            session_id: currentSession?.session_id,
            voice_id: character.voice_id
          })
          
          // Update session state
          if (response.session_id && !currentSession?.session_id) {
            setCurrentSession({ session_id: response.session_id })
          }
        }
      }
      
      // Set response data
      setCurrentResponse(response.dialogue)
      setCharacterEmotion(response.emotion)
      
      console.log('Chat response:', { 
        dialogue: response.dialogue, 
        emotion: response.emotion, 
        audioLength: response.audio?.length 
      })
      
      console.log('🔊 Final response before setting audio:', { 
        hasAudio: !!response.audio, 
        audioLength: response.audio?.length,
        dialogue: response.dialogue.substring(0, 50) + '...'
      })
      
      if (response.audio) {
        console.log('✅ Setting chat audio, length:', response.audio.length)
        setCurrentAudio(response.audio)
        // Don't start typing until audio starts playing
        setShouldStartTyping(false)
      } else {
        console.log('❌ No audio in chat response - will start typing immediately')
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
              setIsAudioPlaying(false)
              // Keep current audio visible, just stop playing it
              // setCurrentAudio(null) // REMOVED: Don't clear audio unnecessarily
              
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
    // DON'T clear audio after playback - keep it visible for replay
    // setCurrentAudio(null) // REMOVED: This was causing audio to disappear
  }

  // Session management functions
  const handleContinueSession = async (session: any) => {
    try {
      console.log('🔄 Continuing session:', session.session_id)
      setShowSessionModal(false)
      setCurrentSession(session)
      
      // Mark user interaction for autoplay permission
      setUserHasInteracted(true)
      
      // Load session messages using the correct API
      const response = await fetch(`http://localhost:8000/api/sessions/continue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: session.session_id,
          user_id: 'demo_user'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('📜 Session continue response:', data)
        
        if (data.success && data.data) {
          console.log('✅ Continuing session with simplified state restoration')
          
          // Set welcome as generated to skip greeting
          setWelcomeGenerated(true)
          
          // Restore simple session state using new backend fields
          if (data.data.last_ai_output) {
            setCurrentResponse(data.data.last_ai_output)
            setCharacterEmotion('neutral')
            setShouldStartTyping(true) // Show immediately without TTS
            
            // Generate TTS for the restored AI output so audio is available
            try {
              console.log('🎵 Generating TTS for restored session output')
              const ttsResponse = await ApiClient.textToSpeech(
                data.data.last_ai_output,
                character?.voice_id || 'tc_61c97b56f1b7877a74df625b',
                'normal',
                1.0,
                character?.id
              )
              
              if (ttsResponse.audio_base64) {
                setCurrentAudio(ttsResponse.audio_base64)
                console.log('✅ TTS generated for session continuation')
              }
            } catch (ttsError) {
              console.log('⚠️ TTS failed for session continuation:', ttsError)
              // Continue without audio if TTS fails
            }
          }
          
          if (data.data.last_user_input) {
            setLastUserMessage(data.data.last_user_input)
          }
          
          // Keep minimal messages state for history parameter
          setMessages(data.data.session?.messages || [])
          
          console.log('📌 Session state restored:', {
            lastAI: data.data.last_ai_output?.substring(0, 50) + '...',
            lastUser: data.data.last_user_input,
            messageCount: data.data.session?.message_count || 0
          })
        } else {
          console.log('⚠️ No session data:', data)
        }
      } else {
        console.error('❌ Session continue API failed:', response.status)
      }
    } catch (error) {
      console.error('❌ Error continuing session:', error)
    }
  }

  const handleStartNewSession = async () => {
    try {
      setShowSessionModal(false)
      
      // Mark user interaction for autoplay permission
      setUserHasInteracted(true)
      
      // Reset all chat states for fresh start
      setCurrentSession(null)
      setCurrentResponse('')
      setLastUserMessage('')
      setMessages([])
      // DON'T clear currentAudio here - let it persist after completion
      setCharacterEmotion('')
      setIsThinking(false)
      setShouldStartTyping(false)
      
      // Create new session
      const response = await fetch(`http://localhost:8000/api/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: 'demo_user',
          character_id: character?.id,
          persona_id: null
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        if (data.success) {
          setCurrentSession(data.data)
          console.log('✅ Created new session for greeting:', data.data.session?.session_id)
        }
      }
      
      // Trigger welcome generation for new conversation
      setWelcomeGenerated(false)
      console.log('🎬 New conversation started, greeting will be triggered')
    } catch (error) {
      console.error('Error creating new session:', error)
    }
  }

  const handleDeleteSession = async (session: any) => {
    try {
      console.log('🗑️ Deleting session:', session.session_id)
      
      const response = await fetch(`http://localhost:8000/api/sessions/${session.session_id}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'demo_user' })
      })
      
      if (response.ok) {
        const result = await response.json()
        if (result.success) {
          console.log('✅ Session deleted successfully')
          // Remove from local state
          const updatedSessions = previousSessions.filter(s => s.session_id !== session.session_id)
          setPreviousSessions(updatedSessions)
          
          // If no sessions left, close modal and start new session
          if (updatedSessions.length === 0) {
            setShowSessionModal(false)
            setWelcomeGenerated(false) // Allow welcome message
          }
        }
      } else {
        console.error('❌ Failed to delete session:', response.status)
      }
    } catch (error) {
      console.error('❌ Error deleting session:', error)
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
                      />
                    </motion.div>
                  )}
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

      {/* Last user message display (appears when typing/recording/processing) */}
      <AnimatePresence>
        {(lastUserMessage && (!isTyping || lastUserMessage.includes('처리하고'))) && (
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
            >
              <Send className="w-5 h-5" />
            </Button>
          )}
        </div>
      </div>

      {/* Session Continuation Modal */}
      <Dialog open={showSessionModal} onOpenChange={(open) => !open && handleStartNewSession()}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>이전 대화 계속하기</DialogTitle>
            <DialogDescription>
              {character?.name}와의 이전 대화가 있습니다. 계속하시겠습니까?
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
            {previousSessions.map((session, index) => (
              <div 
                key={session.session_id}
                className="border rounded-lg p-3 relative group"
              >
                {/* Delete button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteSession(session)
                  }}
                  className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-red-500 hover:bg-red-600 text-white rounded-full p-1"
                  title="세션 삭제"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
                
                {/* Session content - clickable */}
                <div 
                  className="cursor-pointer hover:bg-muted/50 transition-colors rounded -m-3 p-3"
                  onClick={() => handleContinueSession(session)}
                >
                  <div className="text-sm font-medium mb-1">
                    {new Date(session.last_updated).toLocaleDateString('ko-KR')}
                  </div>
                  <div className="text-xs text-muted-foreground mb-2">
                    메시지 {session.message_count}개
                  </div>
                  {session.last_messages && (
                    <div className="space-y-1">
                      {session.last_messages.user && (
                        <div className="text-xs bg-blue-50 p-1 rounded">
                          👤 {session.last_messages.user}
                        </div>
                      )}
                      {session.last_messages.assistant && (
                        <div className="text-xs bg-gray-50 p-1 rounded">
                          🤖 {session.last_messages.assistant}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}
            
            <div className="flex gap-2 pt-2">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={handleStartNewSession}
              >
                새 대화 시작
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}