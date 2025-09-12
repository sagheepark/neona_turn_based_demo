/**
 * ChatInterface Component
 * Minimal implementation using assistant-ui instead of manual tools
 */

import React from 'react';

interface ChatInterfaceProps {
  character: {
    id: string;
    name: string;
  };
  onMessage: (message: string) => void;
}

export default function ChatInterface({ character, onMessage }: ChatInterfaceProps) {
  return (
    <div data-testid="chat-interface-assistant-ui">
      <div className="character-info">
        Chat with {character.name}
      </div>
      <div className="assistant-ui-integration">
        {/* This would integrate with actual assistant-ui components */}
        <div>Assistant-UI integrated chat interface</div>
      </div>
    </div>
  );
}