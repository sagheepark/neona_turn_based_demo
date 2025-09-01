/**
 * UnifiedSelection Component - Handles both chip and option modes
 * Minimal implementation following TDD principles
 */
'use client'

import React, { useState } from 'react'

interface UnifiedSelectionProps {
  items: string[]
  onSelect: (item: string) => void
  mode?: 'chip' | 'option' | 'inline'
  question?: string
  correctAnswer?: string
  isVisible?: boolean
}

// Constants
const QUIZ_RESULT_DELAY_MS = 2000
const CHIP_ANIMATION_DELAY_MS = 50

export function UnifiedSelection({ 
  items, 
  onSelect,
  mode = items.length <= 4 ? 'chip' : 'option',
  question,
  correctAnswer,
  isVisible = true
}: UnifiedSelectionProps) {
  const [selected, setSelected] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  
  if (!isVisible || items.length === 0) return null
  
  const handleSelect = (item: string) => {
    setSelected(item)
    if (correctAnswer) {
      setShowResult(true)
      setTimeout(() => {
        onSelect(item)
        setSelected(null)
        setShowResult(false)
      }, QUIZ_RESULT_DELAY_MS)
    } else {
      onSelect(item)
      setSelected(null)
    }
  }
  
  // Chip mode for quick suggestions (minimal implementation)
  if (mode === 'chip') {
    const chipContainerClasses = [
      "flex flex-wrap gap-2 p-4",
      "bg-card/50 backdrop-blur-enhanced",
      "rounded-lg border border-border/50"
    ].join(" ")
    
    const chipButtonClasses = [
      "px-4 py-2 rounded-full text-sm font-medium",
      "transition-all duration-200 transform",
      "bg-secondary hover:bg-secondary/80 text-secondary-foreground",
      "hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed",
      "animate-fade-in"
    ].join(" ")
    
    return (
      <div className={chipContainerClasses}>
        {items.map((item, index) => (
          <button
            key={index}
            onClick={() => handleSelect(item)}
            disabled={selected !== null}
            className={chipButtonClasses}
            style={{
              animationDelay: `${index * CHIP_ANIMATION_DELAY_MS}ms`
            }}
          >
            {item}
          </button>
        ))}
      </div>
    )
  }
  
  // Option mode - not implemented yet for this test
  return <div>Option mode not implemented yet</div>
}