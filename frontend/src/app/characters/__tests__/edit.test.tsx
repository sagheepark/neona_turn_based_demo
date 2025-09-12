/**
 * Test 12.1: shouldAddToggleToCharacterEditForm
 * RED phase: Character edit form doesn't have greeting suggestions toggle
 * Purpose: Add per-character on/off toggle for greeting suggestions
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import EditCharacterPage from '../[id]/edit/page';
import { useParams, useRouter } from 'next/navigation';
import { CharacterStorage } from '@/lib/storage';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useParams: jest.fn(),
  useRouter: jest.fn(),
}));

// Mock CharacterStorage
jest.mock('@/lib/storage', () => ({
  CharacterStorage: {
    getById: jest.fn(),
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

// Mock KnowledgeManagementSection
jest.mock('@/components/knowledge', () => ({
  KnowledgeManagementSection: function MockKnowledgeManagementSection() {
    return <div>Knowledge Management</div>;
  }
}));

describe('Character Edit Form - Toggle System', () => {
  const mockPush = jest.fn();
  const mockCharacter = {
    id: 'test_character',
    name: 'Test Character',
    description: 'Test Description',
    image: '',
    prompt: 'Test prompt',
    greetings: ['Hello!'],
    conversation_examples: [],
    voice_id: 'test_voice',
    temperature: 0.7,
    greeting_suggestions_enabled: false, // This field should exist
    created_at: new Date(),
    updated_at: new Date(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (useParams as jest.Mock).mockReturnValue({ id: 'test_character' });
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (CharacterStorage.getById as jest.Mock).mockReturnValue(mockCharacter);
  });

  it('should add greeting suggestions toggle to character edit form', async () => {
    // Arrange & Act
    render(<EditCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });

    // Assert - Toggle should exist in the form
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    expect(toggle).toBeInTheDocument();
    
    // Assert - Toggle should reflect current state
    expect(toggle).not.toBeChecked(); // Based on mockCharacter.greeting_suggestions_enabled = false
    
    // Test toggle functionality
    fireEvent.click(toggle);
    expect(toggle).toBeChecked();
    
    // Test that save includes the toggle value
    const saveButton = screen.getByRole('button', { name: /save character/i });
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(CharacterStorage.save).toHaveBeenCalledWith(
        expect.objectContaining({
          greeting_suggestions_enabled: true
        })
      );
    });
  });

  it('should persist greeting suggestions toggle state', async () => {
    // Arrange - Character with greeting suggestions enabled
    const enabledCharacter = {
      ...mockCharacter,
      greeting_suggestions_enabled: true,
    };
    (CharacterStorage.getById as jest.Mock).mockReturnValue(enabledCharacter);
    
    // Act
    render(<EditCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });
    
    // Assert - Toggle should be checked when greeting_suggestions_enabled is true
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    expect(toggle).toBeChecked();
  });

  it('should display toggle in settings section of the form', async () => {
    // Arrange & Act
    render(<EditCharacterPage />);
    
    // Wait for form to load
    await waitFor(() => {
      expect(screen.getByLabelText(/character name/i)).toBeInTheDocument();
    });
    
    // Navigate to settings tab if using tabs
    const settingsTab = screen.queryByRole('tab', { name: /settings/i });
    if (settingsTab) {
      fireEvent.click(settingsTab);
    }
    
    // Assert - Toggle should be in the settings section
    const settingsSection = screen.getByTestId('character-settings-section');
    const toggle = screen.getByRole('checkbox', { 
      name: /enable greeting suggestions/i 
    });
    
    expect(settingsSection).toContainElement(toggle);
  });
});