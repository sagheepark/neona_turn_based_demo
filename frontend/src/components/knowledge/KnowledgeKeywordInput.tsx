/**
 * Knowledge Keyword Input Component
 * Full implementation with keyword processing and validation
 */

import React, { useState, useEffect } from 'react';

interface KnowledgeKeywordInputProps {
  value?: string;
  onChange?: (keywords: string[]) => void;
  placeholder?: string;
  error?: string;
}

export default function KnowledgeKeywordInput({ 
  value = '', 
  onChange, 
  placeholder = 'Enter keywords separated by commas',
  error
}: KnowledgeKeywordInputProps) {
  const [inputValue, setInputValue] = useState(value);
  const [validationError, setValidationError] = useState('');

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  const processKeywords = (input: string): string[] => {
    // Split by comma, trim whitespace, and filter empty values
    return input
      .split(',')
      .map(keyword => keyword.trim())
      .filter(keyword => keyword.length > 0);
  };

  const validateKeywords = (keywords: string[]): string => {
    if (keywords.length === 0) {
      return 'At least one keyword is required';
    }
    
    const invalidKeywords = keywords.filter(k => k.length < 2 || k.length > 50);
    if (invalidKeywords.length > 0) {
      return 'Keywords must be between 2 and 50 characters';
    }
    
    return '';
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    
    const keywords = processKeywords(newValue);
    const error = validateKeywords(keywords);
    setValidationError(error);
    
    // Always call onChange even if validation fails (for real-time updates)
    onChange?.(keywords);
  };

  const handleBlur = () => {
    // Clean up input on blur
    const keywords = processKeywords(inputValue);
    const cleanedValue = keywords.join(', ');
    
    if (cleanedValue !== inputValue) {
      setInputValue(cleanedValue);
    }
    
    const error = validateKeywords(keywords);
    setValidationError(error);
  };

  const displayError = error || validationError;

  return (
    <div className="knowledge-keyword-input-wrapper">
      <input
        type="text"
        className={`knowledge-keyword-input w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 ${
          displayError ? 'border-red-500' : 'border-gray-300'
        }`}
        value={inputValue}
        onChange={handleInputChange}
        onBlur={handleBlur}
        placeholder={placeholder}
      />
      {inputValue && (
        <div className="mt-2">
          <div className="flex flex-wrap gap-1">
            {processKeywords(inputValue).map((keyword, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full"
              >
                {keyword}
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {processKeywords(inputValue).length} keyword{processKeywords(inputValue).length !== 1 ? 's' : ''}
          </p>
        </div>
      )}
      {displayError && (
        <p className="text-red-500 text-xs mt-1 validation-error">{displayError}</p>
      )}
    </div>
  );
}