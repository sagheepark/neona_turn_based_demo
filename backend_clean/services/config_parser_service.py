"""
Configuration Parser Service for Selective Knowledge System
Parses text-based character configuration for simulation parameters
"""

import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ConfigParserService:
    """
    Service for parsing text-based character configuration
    Converts human-readable config format to structured data
    """
    
    def parse_configuration(self, config_text: str) -> Dict:
        """
        Parse text-based configuration into structured format
        
        Args:
            config_text: Multi-line configuration text
            
        Returns:
            Parsed configuration dictionary
        """
        try:
            config = {
                "status_values": {},
                "milestones": {},
                "event_triggers": {},
                "memory_compression_prompt": "",
                "prompt_injection_template": ""
            }
            
            if not config_text:
                return config
            
            lines = config_text.strip().split('\n')
            current_section = None
            multi_line_buffer = []
            multi_line_key = None
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    # Check for section headers in comments
                    if line.startswith('# '):
                        section_name = line[2:].lower()
                        if 'status' in section_name and 'value' in section_name:
                            current_section = 'status_values'
                        elif 'milestone' in section_name:
                            current_section = 'milestones'
                        elif 'event' in section_name and 'trigger' in section_name:
                            current_section = 'event_triggers'
                        elif 'memory' in section_name and 'compression' in section_name:
                            current_section = 'memory_compression'
                        elif 'prompt' in section_name and 'injection' in section_name:
                            current_section = 'prompt_injection'
                    continue
                
                # Handle multi-line values
                if line.startswith('"') and not line.endswith('"'):
                    multi_line_buffer = [line[1:]]
                    continue
                elif multi_line_buffer:
                    if line.endswith('"'):
                        multi_line_buffer.append(line[:-1])
                        multi_line_value = '\n'.join(multi_line_buffer)
                        if current_section == 'memory_compression':
                            config["memory_compression_prompt"] = multi_line_value
                        elif current_section == 'prompt_injection':
                            config["prompt_injection_template"] = multi_line_value
                        multi_line_buffer = []
                    else:
                        multi_line_buffer.append(line)
                    continue
                
                # Parse based on current section
                if current_section == 'status_values':
                    self._parse_status_value(line, config["status_values"])
                elif current_section == 'milestones':
                    self._parse_milestone(line, config["milestones"])
                elif current_section == 'event_triggers':
                    self._parse_event_trigger(line, config["event_triggers"])
                elif current_section == 'memory_compression':
                    if line.startswith('"') and line.endswith('"'):
                        config["memory_compression_prompt"] = line[1:-1]
                elif current_section == 'prompt_injection':
                    if line.startswith('"') and line.endswith('"'):
                        config["prompt_injection_template"] = line[1:-1]
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to parse configuration: {str(e)}")
            return {
                "status_values": {},
                "milestones": {},
                "event_triggers": {},
                "memory_compression_prompt": "",
                "prompt_injection_template": ""
            }
    
    def _parse_status_value(self, line: str, status_values: Dict):
        """
        Parse a status value definition
        Format: name: min-max, default=value, "description"
        
        Args:
            line: Configuration line
            status_values: Dictionary to add parsed value to
        """
        try:
            # Match pattern: name: 0-100, default=50, "description"
            match = re.match(r'(\w+):\s*(\d+)-(\d+),\s*default=(\d+)(?:,\s*"([^"]*)")?', line)
            if match:
                name, min_val, max_val, default, description = match.groups()
                status_values[name] = {
                    "min": int(min_val),
                    "max": int(max_val),
                    "default": int(default),
                    "description": description or ""
                }
                logger.debug(f"Parsed status value: {name}")
                
        except Exception as e:
            logger.error(f"Failed to parse status value: {line} - {str(e)}")
    
    def _parse_milestone(self, line: str, milestones: Dict):
        """
        Parse a milestone definition
        Format: id: "description" -> status+value, status2+value2
        
        Args:
            line: Configuration line
            milestones: Dictionary to add parsed milestone to
        """
        try:
            # Match pattern: milestone_id: "description" -> rewards
            match = re.match(r'(\w+):\s*"([^"]*)"(?:\s*->\s*(.+))?', line)
            if match:
                milestone_id, description, rewards_str = match.groups()
                
                rewards = {}
                if rewards_str:
                    # Parse rewards (e.g., "affection+10, trust+5")
                    reward_parts = rewards_str.split(',')
                    for part in reward_parts:
                        part = part.strip()
                        if '+' in part:
                            status, value = part.split('+')
                            rewards[status.strip()] = int(value)
                        elif '-' in part:
                            status, value = part.split('-')
                            rewards[status.strip()] = -int(value)
                
                milestones[milestone_id] = {
                    "description": description,
                    "rewards": rewards,
                    "conditions": {}  # Can be extended with condition parsing
                }
                logger.debug(f"Parsed milestone: {milestone_id}")
                
        except Exception as e:
            logger.error(f"Failed to parse milestone: {line} - {str(e)}")
    
    def _parse_event_trigger(self, line: str, event_triggers: Dict):
        """
        Parse an event trigger definition
        Format: trigger_name -> status+value, status2-value2
        
        Args:
            line: Configuration line
            event_triggers: Dictionary to add parsed trigger to
        """
        try:
            # Match pattern: trigger -> impacts
            match = re.match(r'(\w+)\s*->\s*(.+)', line)
            if match:
                trigger_name, impacts_str = match.groups()
                
                impacts = {}
                # Parse impacts (e.g., "affection+5, mood='happy'")
                impact_parts = impacts_str.split(',')
                for part in impact_parts:
                    part = part.strip()
                    if '=' in part and "'" in part:
                        # String value (e.g., mood="happy")
                        key, value = part.split('=')
                        impacts[key.strip()] = value.strip().strip("'\"")
                    elif '+' in part:
                        # Positive numeric value
                        status, value = part.split('+')
                        impacts[status.strip()] = int(value)
                    elif '-' in part:
                        # Negative numeric value
                        status, value = part.split('-')
                        impacts[status.strip()] = -int(value)
                
                event_triggers[trigger_name] = {
                    "impacts": impacts,
                    "conditions": {}  # Can be extended with condition parsing
                }
                logger.debug(f"Parsed event trigger: {trigger_name}")
                
        except Exception as e:
            logger.error(f"Failed to parse event trigger: {line} - {str(e)}")
    
    def validate_configuration(self, config: Dict) -> List[str]:
        """
        Validate parsed configuration for errors
        
        Args:
            config: Parsed configuration dictionary
            
        Returns:
            List of validation error messages
        """
        errors = []
        
        try:
            # Validate status values
            for name, status_def in config.get("status_values", {}).items():
                if status_def["min"] > status_def["max"]:
                    errors.append(f"Status '{name}': min value ({status_def['min']}) > max value ({status_def['max']})")
                if not (status_def["min"] <= status_def["default"] <= status_def["max"]):
                    errors.append(f"Status '{name}': default value ({status_def['default']}) out of range")
            
            # Validate milestone rewards reference existing status values
            for milestone_id, milestone_def in config.get("milestones", {}).items():
                for status_name in milestone_def.get("rewards", {}).keys():
                    if status_name not in config.get("status_values", {}):
                        errors.append(f"Milestone '{milestone_id}': references unknown status '{status_name}'")
            
            # Validate event trigger impacts
            for trigger_name, trigger_def in config.get("event_triggers", {}).items():
                for impact_key in trigger_def.get("impacts", {}).keys():
                    if impact_key not in ["mood"] and impact_key not in config.get("status_values", {}):
                        errors.append(f"Event trigger '{trigger_name}': references unknown status '{impact_key}'")
            
            # Check for required templates
            if not config.get("prompt_injection_template"):
                errors.append("Missing prompt injection template")
            
            return errors
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return [f"Validation failed: {str(e)}"]
    
    def generate_default_config(self, character_type: str = "default") -> str:
        """
        Generate a default configuration template
        
        Args:
            character_type: Type of character (e.g., "companion", "teacher", "entertainer")
            
        Returns:
            Default configuration text
        """
        templates = {
            "companion": """# Status Values
affection: 0-100, default=50, "친밀도 수준"
trust: 0-100, default=30, "신뢰도"
mood: 0-100, default=70, "현재 기분"

# Milestones
first_meeting: "첫 만남" -> affection+5, trust+5
deep_conversation: "깊은 대화" -> affection+10, trust+15
shared_secret: "비밀 공유" -> trust+20, affection+10

# Event Triggers
user_compliment -> affection+5, mood+10
user_shares_problem -> trust+5, affection+3
long_conversation -> affection+2, trust+3

# Memory Compression Prompt
"대화에서 사용자의 감정 상태, 고민, 개인적 정보를 중심으로 요약하세요."

# Prompt Injection Template
"관계 상태: 친밀도 {affection}/100, 신뢰도 {trust}/100
현재 기분: {mood}/100
달성한 마일스톤: {milestones}
기억하는 정보: {persistent_facts}
이전 대화: {compressed_history}"
""",
            "teacher": """# Status Values
knowledge: 0-100, default=0, "지식 수준"
confidence: 0-100, default=30, "자신감"
progress: 0-100, default=0, "학습 진도"

# Milestones
first_lesson: "첫 수업 완료" -> confidence+10, progress+5
concept_mastered: "개념 마스터" -> knowledge+20, confidence+15
quiz_passed: "퀴즈 통과" -> progress+10, confidence+10

# Event Triggers
correct_answer -> knowledge+5, confidence+3
wrong_answer -> confidence-2
asks_question -> knowledge+2

# Memory Compression Prompt
"학습한 내용, 이해도, 어려워하는 부분을 중심으로 요약하세요."

# Prompt Injection Template
"학습 상태: 지식 {knowledge}/100, 자신감 {confidence}/100
진도: {progress}/100
달성 내역: {milestones}
학습 기록: {persistent_facts}
이전 수업: {compressed_history}"
""",
            "default": """# Status Values
affection: 0-100, default=50, "관계 수준"
trust: 0-100, default=30, "신뢰도"
stress: 0-100, default=20, "스트레스"

# Milestones
first_chat: "첫 대화" -> affection+5
regular_user: "단골 사용자" -> trust+10

# Event Triggers
positive_interaction -> affection+3, stress-2
negative_interaction -> affection-3, stress+5

# Memory Compression Prompt
"중요한 대화 내용과 감정 변화를 요약하세요."

# Prompt Injection Template
"현재 상태: 친밀도 {affection}, 신뢰도 {trust}, 스트레스 {stress}
마일스톤: {milestones}
기억: {persistent_facts}
요약: {compressed_history}"
"""
        }
        
        return templates.get(character_type, templates["default"])
    
    def format_config_for_display(self, config: Dict) -> str:
        """
        Format parsed configuration back to readable text
        
        Args:
            config: Parsed configuration dictionary
            
        Returns:
            Formatted configuration text
        """
        try:
            lines = []
            
            # Format status values
            if config.get("status_values"):
                lines.append("# Status Values")
                for name, status_def in config["status_values"].items():
                    line = f"{name}: {status_def['min']}-{status_def['max']}, default={status_def['default']}"
                    if status_def.get("description"):
                        line += f', "{status_def["description"]}"'
                    lines.append(line)
                lines.append("")
            
            # Format milestones
            if config.get("milestones"):
                lines.append("# Milestones")
                for milestone_id, milestone_def in config["milestones"].items():
                    line = f'{milestone_id}: "{milestone_def["description"]}"'
                    if milestone_def.get("rewards"):
                        rewards = []
                        for status, value in milestone_def["rewards"].items():
                            rewards.append(f"{status}{value:+d}")
                        line += f" -> {', '.join(rewards)}"
                    lines.append(line)
                lines.append("")
            
            # Format event triggers
            if config.get("event_triggers"):
                lines.append("# Event Triggers")
                for trigger_name, trigger_def in config["event_triggers"].items():
                    impacts = []
                    for key, value in trigger_def.get("impacts", {}).items():
                        if isinstance(value, str):
                            impacts.append(f"{key}='{value}'")
                        else:
                            impacts.append(f"{key}{value:+d}")
                    line = f"{trigger_name} -> {', '.join(impacts)}"
                    lines.append(line)
                lines.append("")
            
            # Format memory compression prompt
            if config.get("memory_compression_prompt"):
                lines.append("# Memory Compression Prompt")
                lines.append(f'"{config["memory_compression_prompt"]}"')
                lines.append("")
            
            # Format prompt injection template
            if config.get("prompt_injection_template"):
                lines.append("# Prompt Injection Template")
                lines.append(f'"{config["prompt_injection_template"]}"')
            
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Failed to format configuration: {str(e)}")
            return ""