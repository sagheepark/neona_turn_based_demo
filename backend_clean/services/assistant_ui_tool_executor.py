"""
AssistantUIToolExecutor Service
Handles execution of assistant-ui tool calls
"""

from typing import Dict, Any, Optional


class AssistantUIToolExecutor:
    """Executor for assistant-ui tool calls"""
    
    def __init__(self):
        """Initialize the tool executor"""
        pass
    
    def execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call and return the result
        
        Args:
            tool_call: Dict with 'type' and 'data' fields
            
        Returns:
            Dict with execution result
        """
        try:
            tool_type = tool_call.get("type")
            tool_data = tool_call.get("data", {})
            
            if tool_type == "show_selection":
                return self._handle_show_selection(tool_data)
            elif tool_type == "continue_output":
                return self._handle_continue_output(tool_data)
            else:
                return {
                    "success": False,
                    "error": f"Unknown tool type: {tool_type}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}"
            }
    
    def _handle_show_selection(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle show_selection tool execution"""
        return {
            "success": True,
            "tool_type": "show_selection",
            "result": "Selection displayed to user",
            "data": data
        }
    
    def _handle_continue_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle continue_output tool execution"""
        return {
            "success": True,
            "tool_type": "continue_output", 
            "result": "Output continuation triggered",
            "data": data
        }
    
    def format_for_frontend(self, ui_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format UI response for frontend consumption
        
        Args:
            ui_response: Raw UI response from platform handler
            
        Returns:
            Formatted response for frontend components
        """
        ui_type = ui_response.get("ui_type", "none")
        
        if ui_type == "selection":
            selection_type = ui_response.get("selection_type", "topic_selection")
            # Check if it's topic selection (greeting → quiz topics)
            if selection_type in ["topic_selection", "greeting_suggestion"]:
                return {
                    "type": "assistant-ui-topic-selection",
                    "options": ui_response.get("options", []),
                    "title": "퀴즈 주제를 선택하세요"
                }
            # Check if it's quiz question (question with A/B/C/D options)
            elif selection_type == "quiz_question" or ui_response.get("question"):
                return {
                    "type": "assistant-ui-quiz",
                    "question": ui_response.get("question", ""),
                    "options": ui_response.get("options", []),
                    "correct_answer": ui_response.get("correct_answer")
                }
            else:
                # Default to quiz format for other selections
                return {
                    "type": "assistant-ui-quiz",
                    "question": ui_response.get("question", ""),
                    "options": ui_response.get("options", []),
                    "correct_answer": ui_response.get("correct_answer")
                }
        elif ui_type == "quiz":
            return {
                "type": "assistant-ui-quiz",
                "question": ui_response.get("question", ""),
                "options": ui_response.get("options", []),
                "correct_answer": ui_response.get("correct_answer")
            }
        else:
            return {
                "type": "none",
                "requires_ui": False
            }