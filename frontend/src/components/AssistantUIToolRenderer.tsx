/**
 * AssistantUIToolRenderer Component
 * Minimal implementation for tool rendering with assistant-ui
 */

import React from 'react';

interface ToolRendererProps {
  tool: {
    type: string;
    data: {
      question: string;
      items: string[];
      metadata?: any;
    };
  };
}

export default function AssistantUIToolRenderer({ tool }: ToolRendererProps) {
  return (
    <div data-testid="assistant-ui-tool-renderer">
      <h3>{tool.data.question}</h3>
      <div className="tool-options">
        {tool.data.items.map((item, index) => (
          <button key={index} className="tool-option">
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}