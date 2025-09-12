#!/usr/bin/env python3
"""
Comprehensive Continuous Flow Validation Test
Tests that properly validate all aspects of the continuous quiz flow
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# ANSI color codes for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

async def validate_wrong_answer_flow():
    """Test wrong answer flow - should NOT reveal correct answer and should show retry question"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    print(f"{BOLD}🔍 WRONG ANSWER FLOW VALIDATION{ENDC}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Create session and get first question
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "validation_test_user",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
        
        # Get initial question
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "조선시대 퀴즈 시작해주세요",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "validation_test_user",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            first_question = result['tools'][0]['data']
            print(f"✅ Initial question: {first_question['question']}")
            print(f"✅ Correct answer: {first_question['correct_answer']}")
        
        # Submit wrong answer
        wrong_answer = [opt for opt in first_question['options'] 
                       if opt != first_question['correct_answer']][0]
        print(f"\n📝 Submitting WRONG answer: '{wrong_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": wrong_answer,
                "correct_answer": first_question['correct_answer'],
                "question": first_question['question'],
                "items": first_question['options']
            }
        }) as resp:
            result = await resp.json()
            
            print(f"\n🔍 RESPONSE ANALYSIS:")
            print(f"Response keys: {list(result.keys())}")
            
            # Extract response components
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
                audio_present = step_result.get('audio') is not None
                
                print(f"\n📄 DIALOGUE ANALYSIS:")
                print(f"Dialogue: {dialogue}")
                print(f"Audio present: {audio_present}")
                
                print(f"\n🔍 VALIDATION CHECKS:")
                
                # CHECK 1: Should NOT reveal correct answer
                correct_answer_mentioned = first_question['correct_answer'] in dialogue
                if correct_answer_mentioned:
                    print(f"{RED}❌ FAIL: Correct answer '{first_question['correct_answer']}' revealed in feedback{ENDC}")
                else:
                    print(f"{GREEN}✅ PASS: Correct answer not revealed in feedback{ENDC}")
                
                # CHECK 2: Should have encouraging feedback
                encouraging_words = ['다시', '한번더', '생각해보세요', '도전', '아쉽', '괜찮']
                has_encouragement = any(word in dialogue for word in encouraging_words)
                if has_encouragement:
                    print(f"{GREEN}✅ PASS: Encouraging feedback present{ENDC}")
                else:
                    print(f"{RED}❌ FAIL: No encouraging feedback detected{ENDC}")
                
                # CHECK 3: Should provide retry with same question
                if tools and len(tools) > 0:
                    retry_question = tools[0]['data']
                    if retry_question['question'] == first_question['question']:
                        print(f"{GREEN}✅ PASS: Same question presented for retry{ENDC}")
                        
                        # CHECK 4: Retry question should have audio/text
                        retry_mode = retry_question.get('retry_mode', False)
                        if retry_mode:
                            print(f"{GREEN}✅ PASS: Retry mode correctly set{ENDC}")
                        else:
                            print(f"{YELLOW}⚠️  WARNING: Retry mode not set{ENDC}")
                            
                    else:
                        print(f"{RED}❌ FAIL: Different question on retry (should be same){ENDC}")
                        print(f"Original: {first_question['question']}")
                        print(f"Retry: {retry_question['question']}")
                else:
                    print(f"{RED}❌ FAIL: No retry question provided{ENDC}")
                
                # CHECK 5: Audio should be present for feedback
                if audio_present:
                    print(f"{GREEN}✅ PASS: Audio generated for feedback{ENDC}")
                else:
                    print(f"{RED}❌ FAIL: No audio for feedback{ENDC}")
                
            else:
                print(f"{RED}❌ FAIL: No proper flow response received{ENDC}")
    
    return True

async def validate_correct_answer_flow():
    """Test correct answer flow - should celebrate and show new question with text/audio"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    print(f"\n{BOLD}🎯 CORRECT ANSWER FLOW VALIDATION{ENDC}")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Create session and get first question
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "validation_test_user_2",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
        
        # Get initial question
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "조선시대 퀴즈 시작해주세요",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "validation_test_user_2",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            first_question = result['tools'][0]['data']
            print(f"✅ Initial question: {first_question['question']}")
        
        # Submit correct answer
        correct_answer = first_question['correct_answer']
        print(f"\n📝 Submitting CORRECT answer: '{correct_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": correct_answer,
                "correct_answer": correct_answer,
                "question": first_question['question'],
                "items": first_question['options']
            }
        }) as resp:
            result = await resp.json()
            
            print(f"\n🔍 RESPONSE ANALYSIS:")
            
            # Extract response components
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
                audio_present = step_result.get('audio') is not None
                
                print(f"\n📄 DIALOGUE ANALYSIS:")
                print(f"Dialogue: {dialogue}")
                print(f"Audio present: {audio_present}")
                
                print(f"\n🔍 VALIDATION CHECKS:")
                
                # CHECK 1: Should have celebration
                celebration_words = ['잘했', '정답', '축하', '훌륭', '맞', '좋아요']
                has_celebration = any(word in dialogue for word in celebration_words)
                if has_celebration:
                    print(f"{GREEN}✅ PASS: Celebration feedback present{ENDC}")
                else:
                    print(f"{RED}❌ FAIL: No celebration detected{ENDC}")
                
                # CHECK 2: Should provide new question (different from first)
                if tools and len(tools) > 0:
                    new_question = tools[0]['data']
                    if new_question['question'] != first_question['question']:
                        print(f"{GREEN}✅ PASS: New question provided{ENDC}")
                        print(f"New question: {new_question['question']}")
                        
                        # CHECK 3: New question should NOT be in retry mode
                        retry_mode = new_question.get('retry_mode', False)
                        if not retry_mode:
                            print(f"{GREEN}✅ PASS: New question not in retry mode{ENDC}")
                        else:
                            print(f"{RED}❌ FAIL: New question incorrectly in retry mode{ENDC}")
                            
                    else:
                        print(f"{RED}❌ FAIL: Same question repeated (should be new){ENDC}")
                else:
                    print(f"{RED}❌ FAIL: No new question provided{ENDC}")
                
                # CHECK 4: Audio should be present for celebration
                if audio_present:
                    print(f"{GREEN}✅ PASS: Audio generated for celebration{ENDC}")
                else:
                    print(f"{RED}❌ FAIL: No audio for celebration{ENDC}")
                
                # CHECK 5: Check if dialogue includes new question text
                if tools and len(tools) > 0:
                    new_question_text = tools[0]['data']['question']
                    if new_question_text in dialogue:
                        print(f"{GREEN}✅ PASS: New question text included in dialogue{ENDC}")
                    else:
                        print(f"{RED}❌ FAIL: New question text NOT included in dialogue{ENDC}")
                        print(f"Question: {new_question_text}")
                        print(f"Dialogue: {dialogue}")
                
            else:
                print(f"{RED}❌ FAIL: No proper flow response received{ENDC}")
    
    return True

async def main():
    try:
        print(f"{BOLD}🧪 COMPREHENSIVE CONTINUOUS FLOW VALIDATION{ENDC}")
        print("=" * 60)
        
        # Run validation tests
        await validate_wrong_answer_flow()
        await validate_correct_answer_flow()
        
        print(f"\n{BOLD}✅ VALIDATION COMPLETE{ENDC}")
        
    except Exception as e:
        print(f"{RED}❌ Test failed: {e}{ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())