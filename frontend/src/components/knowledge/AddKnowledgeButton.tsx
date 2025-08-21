/**
 * Add Knowledge Button Component
 * Full implementation with proper styling and interaction
 */

import React from 'react';

interface AddKnowledgeButtonProps {
  onClick?: () => void;
  disabled?: boolean;
}

export default function AddKnowledgeButton({ 
  onClick, 
  disabled = false 
}: AddKnowledgeButtonProps) {
  return (
    <button 
      className="add-knowledge-button inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      onClick={onClick}
      disabled={disabled}
    >
      <svg 
        className="w-4 h-4 mr-2" 
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24" 
        xmlns="http://www.w3.org/2000/svg"
      >
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M12 4v16m8-8H4" 
        />
      </svg>
      Add Knowledge Item
    </button>
  );
}