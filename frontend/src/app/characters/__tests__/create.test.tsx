/**
 * Test 12.3: shouldShowToggleInCharacterCreateForm
 * RED phase: Character create form doesn't have greeting suggestions toggle
 * Purpose: Add per-character toggle to character creation form
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CreateCharacterPage from '../create/page';
import { useRouter } from 'next/navigation';
import { CharacterStorage } from '@/lib/storage';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

// Mock CharacterStorage
jest.mock('@/lib/storage', () => ({
  CharacterStorage: {
    save: jest.fn(),
  }
}));

// Mock VoiceSelector to avoid fetch errors
jest.mock('@/components/characters/VoiceSelector', () => {
  return function MockVoiceSelector({ selectedVoiceId, onSelect }: any) {
    return (
      <select 
        value={selectedVoiceId} 
        onChange={(e) => onSelect(e.target.value)}
        aria-label="Voice selection"
      >
        <option value="">Select Voice</option>
        <option value="test_voice">Test Voice</option>
      </select>
    );
  };
});

// Mock VoiceRecommendation
jest.mock('@/components/characters/VoiceRecommendation', () => {
  return function MockVoiceRecommendation() {
    return null;
  };
});

describe('Character Create Form - Toggle System', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
  });

  it('should add greeting suggestions toggle to character create form', async () => {
    // Arrange & Act
    render(<CreateCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });

    // Assert - Toggle should exist in the form
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    expect(toggle).toBeInTheDocument();
    
    // Assert - Toggle should default to unchecked (false)
    expect(toggle).not.toBeChecked();
    
    // Test toggle functionality
    fireEvent.click(toggle);
    expect(toggle).toBeChecked();
  });

  it('should include toggle value when creating new character', async () => {
    // Arrange
    render(<CreateCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });

    // Fill in required fields
    const nameInput = screen.getByLabelText(/character name/i);
    const descriptionInput = screen.getByLabelText(/description/i);
    const voiceSelect = screen.getByLabelText(/voice selection/i);

    fireEvent.change(nameInput, { target: { value: 'Test Character' } });
    fireEvent.change(descriptionInput, { target: { value: 'Test Description' } });
    fireEvent.change(voiceSelect, { target: { value: 'test_voice' } });
    
    // Enable greeting suggestions
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    fireEvent.click(toggle);
    
    // Submit form
    const createButton = screen.getByRole('button', { name: /create character/i });
    fireEvent.click(createButton);
    
    // Assert that save was called with the toggle value
    await waitFor(() => {
      expect(CharacterStorage.save).toHaveBeenCalledWith(
        expect.objectContaining({
          greeting_suggestions_enabled: true,
          name: 'Test Character',
          description: 'Test Description',
          voice_id: 'test_voice'
        })
      );
    });
  });

  it('should display toggle in settings section of create form', async () => {
    // Arrange & Act
    render(<CreateCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });
    
    // Assert - Toggle should be in the settings section
    const settingsSection = screen.getByTestId('character-settings-section');
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    
    expect(settingsSection).toContainElement(toggle);
  });

  it('should default greeting suggestions to disabled for new characters', async () => {
    // Arrange & Act
    render(<CreateCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });
    
    // Assert - Toggle should be unchecked by default
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    expect(toggle).not.toBeChecked();
  });
});