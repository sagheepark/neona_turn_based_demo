/**
 * AssistantUIChat Component
 * Minimal implementation to replace manual tool handling
 */

import React from 'react';

interface AssistantUIChatProps {
  response: {
    character: string;
    dialogue: string;
    tools?: Array<{
      type: string;
      data: any;
    }>;
  };
}

export default function AssistantUIChat({ response }: AssistantUIChatProps) {
  return (
    <div data-testid="assistant-ui-chat">
      <div className="dialogue">
        {response.dialogue}
      </div>
      {response.tools && response.tools.map((tool, index) => (
        <div key={index} data-testid="assistant-ui-tool">
          <div>{tool.data.question}</div>
          {tool.data.items && tool.data.items.map((item: string, i: number) => (
            <button key={i} className="tool-option">
              {item}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}