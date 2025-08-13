'use client'

import { useState, useEffect } from 'react'

interface TypewriterTextProps {
  text: string
  speed?: number
  onComplete?: () => void
  startTyping?: boolean
}

export function TypewriterText({ text, speed = 50, onComplete, startTyping = true }: TypewriterTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  
  useEffect(() => {
    if (startTyping && currentIndex < text.length) {
      const timer = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)
      
      return () => clearTimeout(timer)
    } else if (currentIndex >= text.length && onComplete) {
      onComplete()
    }
  }, [currentIndex, text, speed, onComplete, startTyping])
  
  // 텍스트가 변경되면 리셋
  useEffect(() => {
    setDisplayedText('')
    setCurrentIndex(0)
  }, [text])
  
  return <span>{displayedText}</span>
}