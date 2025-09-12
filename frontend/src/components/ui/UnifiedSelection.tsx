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

// Helper function for option button classes
function getOptionButtonClasses(isSelected: boolean, isCorrect: boolean, isWrong: boolean): string {
  const baseClasses = [
    "flex items-center gap-3 p-3 rounded-lg",
    "text-left transition-all duration-200",
    "border-2 transform hover:scale-[1.02]",
    "disabled:cursor-not-allowed animate-fade-in"
  ]
  
  let stateClasses: string
  if (isSelected) {
    if (isCorrect) {
      stateClasses = 'border-green-500 bg-green-500/10'
    } else if (isWrong) {
      stateClasses = 'border-destructive bg-destructive/10'
    } else {
      stateClasses = 'border-primary bg-primary/10'
    }
  } else {
    stateClasses = 'border-border hover:border-primary/50 bg-card hover:bg-accent'
  }
  
  return [...baseClasses, stateClasses].join(" ")
}

export function UnifiedSelection({ 
  items, 
  onSelect,
  mode,
  question,
  correctAnswer,
  isVisible = true
}: UnifiedSelectionProps) {
  // Add defensive checks
  console.log('UnifiedSelection received:', { items, question, correctAnswer });
  
  if (!items || !Array.isArray(items)) {
    console.warn('UnifiedSelection: items is not an array or is undefined', items);
    return null;
  }
  
  // Auto-detect mode: if there's a question OR correctAnswer, use option mode (for quizzes)
  // Otherwise use chip mode for ≤4 items, option mode for >4 items
  const resolvedMode = mode ?? ((question || correctAnswer) ? 'option' : (items.length <= 4 ? 'chip' : 'option'))
  const [selected, setSelected] = useState<string | null>(null)
  const [showResult, setShowResult] = useState(false)
  
  if (!isVisible || items.length === 0) return null
  
  const handleSelect = (item: string) => {
    console.log('📱 UnifiedSelection: handleSelect called', { 
      item, 
      question, 
      correctAnswer,
      onSelectFunction: !!onSelect 
    })
    
    // Add explicit logging to track the flow
    console.log('📱 About to call onSelect with:', item)
    
    setSelected(item)
    // No feedback UI - directly call onSelect and let character provide feedback
    onSelect(item)
    
    console.log('📱 onSelect called successfully')
    setSelected(null)
  }
  
  // Chip mode for quick suggestions (minimal implementation)
  if (resolvedMode === 'chip') {
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
  
  // Option mode for quizzes and multiple choices - COMPACT MODE (no white container)
  const optionContainerClasses = [
    "p-2"
  ].join(" ")
  
  return (
    <div className={optionContainerClasses}>
      {/* Question display removed to prevent duplication with chat bubble */}
      <div className="grid gap-2 md:grid-cols-2">
        {items.map((item, index) => {
          const letter = String.fromCharCode(65 + index) // A, B, C, D...
          const isCorrect = showResult && item === correctAnswer
          const isWrong = showResult && selected === item && item !== correctAnswer
          
          return (
            <button
              key={index}
              onClick={() => handleSelect(item)}
              disabled={selected !== null}
              className={getOptionButtonClasses(selected === item, isCorrect, isWrong)}
              style={{
                animationDelay: `${index * CHIP_ANIMATION_DELAY_MS}ms`
              }}
            >
              <span className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-bold">
                {letter}
              </span>
              <span className="text-sm">{item}</span>
              {showResult && (
                <span className="ml-auto">
                  {isCorrect && '✅'}
                  {isWrong && '❌'}
                </span>
              )}
            </button>
          )
        })}
      </div>
      {/* Quiz feedback UI removed per user request - character will provide feedback */}
    </div>
  )
}