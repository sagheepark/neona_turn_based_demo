'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { Volume2, VolumeX, Play, Pause } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface AudioPlayerProps {
  audioBase64: string
  autoPlay?: boolean
  userHasInteracted?: boolean
  onPlayStart?: () => void
  onPlayEnd?: () => void
  onError?: (error: string) => void
}

export function AudioPlayer({ 
  audioBase64, 
  autoPlay = true, 
  userHasInteracted = false,
  onPlayStart, 
  onPlayEnd, 
  onError 
}: AudioPlayerProps) {
  // Reduced logging - only log important events
  
  // Create audio element directly instead of using ref
  const [audio] = useState(() => new Audio())
  const audioRef = useRef<HTMLAudioElement>(audio)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const [duration, setDuration] = useState(0)
  const [currentTime, setCurrentTime] = useState(0)

  useEffect(() => {
    if (!audioBase64 || !audio) {
      return
    }
      
    // Reset states
    setIsLoading(true)
    setHasError(false)
    setIsPlaying(false)
    setCurrentTime(0)
    setDuration(0)
    
    let audioUrl: string | null = null
    
    // Convert base64 to blob URL
    try {
      // Remove data URL prefix if present
      const cleanBase64 = audioBase64.replace(/^data:audio\/[^;]+;base64,/, '')
      
      // Try to decode base64 - validate it's proper base64
      try {
        const binaryString = atob(cleanBase64)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }
        
        // Create blob with proper MIME type
        const blob = new Blob([bytes], { type: 'audio/wav' })
        audioUrl = URL.createObjectURL(blob)
        audio.src = audioUrl
        
      } catch (decodeError) {
        console.error('AudioPlayer: Base64 decode error:', decodeError)
        throw decodeError
      }
      
      // Event listeners
      const handleLoadedData = () => {
        setIsLoading(false)
        setDuration(audio.duration)
        
        if (autoPlay) {
          // Only try autoplay if user has interacted or if we want to test anyway
          if (userHasInteracted) {
            audio.play()
              .catch(err => {
                // This shouldn't happen after user interaction, so it might be a real error
                if (err.name !== 'NotAllowedError') {
                  setHasError(true)
                  onError?.('Audio play failed')
                }
              })
          } else {
            // Try autoplay anyway - if blocked, that's fine
            audio.play()
              .catch(() => {
                // This is expected - don't treat as error
              })
          }
        }
      }

      const handleCanPlay = () => {
        setIsLoading(false)
      }

      const handlePlay = () => {
        setIsPlaying(true)
        onPlayStart?.()
      }

      const handlePause = () => {
        setIsPlaying(false)
      }

      const handleEnded = () => {
        setIsPlaying(false)
        setCurrentTime(0)
        onPlayEnd?.()
      }

      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime)
      }

      const handleError = (e: Event) => {
        console.error('AudioPlayer error:', audio.error)
        setHasError(true)
        setIsLoading(false)
        onError?.('Audio playback error')
      }

      const handleLoadStart = () => {
        // Audio loading started - no logging needed
      }

      audio.addEventListener('loadstart', handleLoadStart)
      audio.addEventListener('loadeddata', handleLoadedData)
      audio.addEventListener('canplay', handleCanPlay)
      audio.addEventListener('play', handlePlay)
      audio.addEventListener('pause', handlePause)
      audio.addEventListener('ended', handleEnded)
      audio.addEventListener('timeupdate', handleTimeUpdate)
      audio.addEventListener('error', handleError)

      // Try to load the audio
      audio.load()

      return () => {
        audio.removeEventListener('loadstart', handleLoadStart)
        audio.removeEventListener('loadeddata', handleLoadedData)
        audio.removeEventListener('canplay', handleCanPlay)
        audio.removeEventListener('play', handlePlay)
        audio.removeEventListener('pause', handlePause)
        audio.removeEventListener('ended', handleEnded)
        audio.removeEventListener('timeupdate', handleTimeUpdate)
        audio.removeEventListener('error', handleError)
        if (audioUrl) {
          URL.revokeObjectURL(audioUrl)
        }
      }
    } catch (err) {
      console.error('AudioPlayer: Error processing audio:', err)
      setHasError(true)
      setIsLoading(false)
      onError?.('Failed to process audio data')
    }
  }, [audioBase64, autoPlay, audio])
  
  // Cleanup audio on unmount
  useEffect(() => {
    return () => {
      if (audio) {
        audio.pause()
        audio.src = ''
      }
    }
  }, [audio])

  const togglePlayPause = () => {
    if (!audioRef.current || hasError) return

    if (isPlaying) {
      audioRef.current.pause()
    } else {
      // User is interacting now, so future autoplay should work
      audioRef.current.play().catch(err => {
        console.error('Play failed:', err)
        setHasError(true)
        onError?.('Audio play failed')
      })
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  if (hasError) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <VolumeX className="w-3 h-3" />
        <span>Audio unavailable</span>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <motion.div
          className="w-3 h-3 border-2 border-current border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
        <span>Loading audio...</span>
      </div>
    )
  }

  return (
    <div className="flex items-center gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={togglePlayPause}
        className="h-6 w-6 p-0 rounded-full"
      >
        {isPlaying ? (
          <Pause className="w-3 h-3" />
        ) : (
          <Play className="w-3 h-3" />
        )}
      </Button>

      {/* Audio waveform visualization */}
      <div className="flex items-center gap-0.5">
        {[...Array(8)].map((_, i) => (
          <motion.div
            key={i}
            className="w-0.5 bg-current rounded-full"
            animate={{
              height: isPlaying ? [4, 12, 6, 16, 8, 14, 10, 6] : [4, 4, 4, 4, 4, 4, 4, 4],
              opacity: isPlaying ? [0.4, 1, 0.6, 1, 0.8, 1, 0.7, 0.5] : [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
            }}
            transition={{
              duration: 0.8,
              repeat: isPlaying ? Infinity : 0,
              delay: i * 0.1,
              ease: "easeInOut"
            }}
          />
        ))}
      </div>

      {/* Time display */}
      <div className="text-xs text-muted-foreground min-w-[30px]">
        {formatTime(currentTime)}
      </div>

      {/* Volume icon */}
      <Volume2 className="w-3 h-3 opacity-60" />
    </div>
  )
}