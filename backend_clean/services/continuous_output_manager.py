"""
Continuous Output Manager - Handles multi-turn character responses
Minimal implementation following TDD principles
"""
from typing import Dict, Any, List


class ContinuousOutputManager:
    """Manages continuous output flow for multi-turn character responses"""
    
    def should_continue(self, response_data: Dict[str, Any]) -> bool:
        """
        Determine if character should continue speaking based on response data
        
        Args:
            response_data: Dictionary containing character response and tools
            
        Returns:
            True if character should continue, False otherwise
        """
        # Check for loop prevention first
        continuation_count = response_data.get('continuation_count', 0)
        max_continuations = response_data.get('max_continuations', 3)  # Default limit
        
        if continuation_count >= max_continuations:
            return False
        
        # Check if response contains tools
        tools = response_data.get('tools', [])
        if not tools:
            return False
        
        # Look for continue_output tool
        for tool in tools:
            if tool.get('type') == 'continue_output':
                return True
        
        return False