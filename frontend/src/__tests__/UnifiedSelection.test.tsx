/**
 * TDD Test Group 2: Unified Selection Component
 * Testing chip and option rendering modes
 */
import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { UnifiedSelection } from '@/components/ui/UnifiedSelection'

describe('UnifiedSelection', () => {
  describe('Test Group 2: Unified Selection Component', () => {
    it('should render chip mode for 4 or fewer items', () => {
      /**
       * Test 2.1: shouldRenderChipModeForFewItems
       * Red phase: This test should fail because UnifiedSelection component doesn't exist yet
       */
      // Arrange
      const items = ['Option 1', 'Option 2', 'Option 3']
      const onSelect = jest.fn()
      
      // Act
      render(<UnifiedSelection items={items} onSelect={onSelect} />)
      
      // Assert - chips should be rendered as horizontal buttons
      const option1Button = screen.getByRole('button', { name: 'Option 1' })
      expect(option1Button).toBeInTheDocument()
      
      // In chip mode, should NOT have letter indicators (A, B, C)
      expect(screen.queryByText(/^A$/)).not.toBeInTheDocument()
      expect(screen.queryByText(/^B$/)).not.toBeInTheDocument()
      
      // Should have chip-style classes
      expect(option1Button).toHaveClass(/chip|rounded-full/)
    })

    it('should render option mode for more than 4 items', () => {
      /**
       * Test 2.2: shouldRenderOptionModeForManyItems
       * Red phase: This test should fail because option mode is not implemented yet
       */
      // Arrange
      const items = ['Option A', 'Option B', 'Option C', 'Option D', 'Option E']
      const onSelect = jest.fn()
      
      // Act
      render(<UnifiedSelection items={items} onSelect={onSelect} />)
      
      // Assert - should render in option mode with letter indicators
      expect(screen.getByText('A')).toBeInTheDocument() // Letter indicator present
      expect(screen.getByText('B')).toBeInTheDocument()
      
      // Should NOT be chip mode (no rounded-full class)
      const optionButton = screen.getByRole('button', { name: /Option A/ })
      expect(optionButton).toBeInTheDocument()
      expect(optionButton).not.toHaveClass(/rounded-full/)
    })

    it('should call onSelect when item is clicked', () => {
      /**
       * Test 2.3: shouldHandleSelectionCallback
       * Red phase: This test checks if selection callback works correctly
       */
      // Arrange
      const items = ['Test Option']
      const onSelect = jest.fn()
      
      // Act
      render(<UnifiedSelection items={items} onSelect={onSelect} />)
      
      const testButton = screen.getByText('Test Option')
      fireEvent.click(testButton)
      
      // Assert
      expect(onSelect).toHaveBeenCalledWith('Test Option')
      expect(onSelect).toHaveBeenCalledTimes(1)
    })
  })

  describe('Test Group 3: Quiz Flow with Validation', () => {
    it('should display quiz with correct answer validation', () => {
      /**
       * Test 3.1: shouldDisplayQuizWithCorrectAnswer
       * Red phase: This test checks if quiz questions display properly with correct answer tracking
       */
      // Arrange
      const items = ['1919년', '1920년', '1921년', '1922년']
      const correctAnswer = '1919년'
      const question = '3·1 운동이 일어난 연도는?'
      const onSelect = jest.fn()
      
      // Act
      render(
        <UnifiedSelection 
          items={items} 
          onSelect={onSelect}
          correctAnswer={correctAnswer}
          question={question}
        />
      )
      
      // Assert - quiz question should be displayed
      expect(screen.getByText('3·1 운동이 일어난 연도는?')).toBeInTheDocument()
      
      // All answer options should be present
      expect(screen.getByText('1919년')).toBeInTheDocument()
      expect(screen.getByText('1920년')).toBeInTheDocument()
      expect(screen.getByText('1921년')).toBeInTheDocument()
      expect(screen.getByText('1922년')).toBeInTheDocument()
      
      // Should use option mode (not chip mode) because it has a question
      expect(screen.getByText('A')).toBeInTheDocument() // Letter indicators
      expect(screen.getByText('B')).toBeInTheDocument()
    })

    it('should show correct answer feedback', async () => {
      /**
       * Test 3.2: shouldShowCorrectAnswerFeedback
       * Red phase: This test should check if correct answer feedback appears and then calls onSelect
       */
      // Arrange
      const items = ['1919년', '1920년'] 
      const correctAnswer = '1919년'
      const onSelect = jest.fn()
      
      // Act
      render(
        <UnifiedSelection 
          items={items}
          onSelect={onSelect} 
          correctAnswer={correctAnswer}
        />
      )
      
      // Click the correct answer
      fireEvent.click(screen.getByText('1919년'))
      
      // Assert - should show correct answer feedback immediately
      expect(screen.getByText('🎉 정답입니다!')).toBeInTheDocument()
      
      // Should not have called onSelect yet (waiting for feedback display)
      expect(onSelect).not.toHaveBeenCalled()
      
      // Wait for the delay and check that onSelect is eventually called
      await waitFor(() => {
        expect(onSelect).toHaveBeenCalledWith('1919년')
      }, { timeout: 3000 })
    })

    it('should show wrong answer feedback', async () => {
      /**
       * Test 3.3: shouldShowWrongAnswerFeedback  
       * Red phase: This test checks if wrong answer feedback appears with correct answer displayed
       */
      // Arrange
      const items = ['1919년', '1920년']
      const correctAnswer = '1919년'
      const onSelect = jest.fn()
      
      // Act
      render(
        <UnifiedSelection 
          items={items}
          onSelect={onSelect}
          correctAnswer={correctAnswer}
        />
      )
      
      // Click the wrong answer
      fireEvent.click(screen.getByText('1920년'))
      
      // Assert - should show wrong answer feedback with correct answer
      expect(screen.getByText(/정답: 1919년/)).toBeInTheDocument()
      
      // Should not have called onSelect yet (waiting for feedback display)
      expect(onSelect).not.toHaveBeenCalled()
      
      // Wait for the delay and check that onSelect is eventually called
      await waitFor(() => {
        expect(onSelect).toHaveBeenCalledWith('1920년') // Still calls with user's selection
      }, { timeout: 3000 })
    })
  })
})