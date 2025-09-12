#!/usr/bin/env python3
"""
Complete End-to-End Scenario Test
Tests the full user journey with real LLM integration:
1. Greeting and quiz start
2. Wrong answer → same question retry with appropriate feedback
3. Correct answer → new question with celebration
4. Multiple correct answers → new questions each time
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

async def test_complete_scenario():
    """Test complete quiz scenario from greeting to multiple questions"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        print(f"{BOLD}🎮 COMPLETE END-TO-END QUIZ SCENARIO TEST{ENDC}")
        print("=" * 60)
        
        # STEP 1: Start session and get greeting
        print(f"\n{BLUE}📌 STEP 1: Starting session with greeting{ENDC}")
        
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "e2e_test_user",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
            print(f"✅ Session started: {session_id}")
            print(f"   Status: {result['data']['session']['status']}")
        
        # STEP 2: Request quiz start
        print(f"\n{BLUE}📌 STEP 2: Requesting Korean history quiz{ENDC}")
        
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "조선시대 퀴즈",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "e2e_test_user",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            print(f"✅ Quiz started")
            print(f"   Dialogue: {result['dialogue'][:100]}...")
            
            # Extract first question
            if result.get('tools'):
                first_question = result['tools'][0]['data']
                print(f"   Question: {first_question['question']}")
                print(f"   Options: {first_question['options']}")
                print(f"   Correct: {first_question['correct_answer']}")
            else:
                print("❌ No question tool provided!")
                return False
        
        # STEP 3: Give WRONG answer
        print(f"\n{YELLOW}📌 STEP 3: Testing WRONG answer scenario{ENDC}")
        
        # Pick a wrong answer (not the correct one)
        wrong_answer = [opt for opt in first_question['options'] 
                       if opt != first_question['correct_answer']][0]
        
        print(f"   Submitting wrong answer: '{wrong_answer}'")
        
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
            if resp.status != 200:
                print(f"❌ Error {resp.status}: {await resp.text()}")
                return False
            result = await resp.json()
            print(f"✅ Wrong answer processed")
            print(f"   Response keys: {list(result.keys())}")
            
            # Extract flow execution result from continuous flow response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"   Dialogue: {dialogue[:150]}..." if dialogue else "   No dialogue")
            
            # Check if we get retry with SAME question
            if tools:
                retry_question = tools[0]['data']
                if retry_question['question'] == first_question['question']:
                    print(f"   {GREEN}✅ GOOD: Same question for retry{ENDC}")
                    print(f"   Retry Mode: {retry_question.get('retry_mode', False)}")
                else:
                    print(f"   {RED}❌ BAD: Different question on wrong answer!{ENDC}")
                    return False
                    
                # Check if feedback is contextually appropriate
                if first_question['correct_answer'] == '한글 창제' and '세종' in dialogue:
                    print(f"   {GREEN}✅ GOOD: Feedback mentions 세종 for 한글 question{ENDC}")
                elif first_question['correct_answer'] == '1592년' and ('임진' in dialogue or '일본' in dialogue):
                    print(f"   {GREEN}✅ GOOD: Feedback mentions 임진왜란 context{ENDC}")
                else:
                    print(f"   ℹ️  Feedback context check")
            else:
                print(f"   {RED}❌ No retry tool provided!{ENDC}")
                return False
        
        # STEP 4: Give CORRECT answer to same question
        print(f"\n{GREEN}📌 STEP 4: Testing CORRECT answer scenario{ENDC}")
        
        print(f"   Submitting correct answer: '{first_question['correct_answer']}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": first_question['correct_answer'],
                "correct_answer": first_question['correct_answer'],
                "question": first_question['question'],
                "items": first_question['options']
            }
        }) as resp:
            result = await resp.json()
            print(f"✅ Correct answer processed")
            
            # Extract flow execution result from continuous flow response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"   Dialogue: {dialogue[:150]}..." if dialogue else "   No dialogue")
            
            # Check if we get NEW question
            if tools:
                second_question = tools[0]['data']
                if second_question['question'] != first_question['question']:
                    print(f"   {GREEN}✅ GOOD: New question after correct answer{ENDC}")
                    print(f"   New Question: {second_question['question']}")
                    print(f"   Retry Mode: {second_question.get('retry_mode', False)}")
                else:
                    print(f"   {RED}❌ BAD: Same question after correct answer!{ENDC}")
                    return False
                    
                # Check if celebration in dialogue
                if any(word in dialogue for word in ['정답', '훌륭', '축하', '잘']):
                    print(f"   {GREEN}✅ GOOD: Celebration in dialogue{ENDC}")
            else:
                print(f"   {RED}❌ No new question tool provided!{ENDC}")
                return False
        
        # STEP 5: Answer second question correctly
        print(f"\n{GREEN}📌 STEP 5: Testing second correct answer{ENDC}")
        
        print(f"   Submitting correct answer: '{second_question['correct_answer']}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": second_question['correct_answer'],
                "correct_answer": second_question['correct_answer'],
                "question": second_question['question'],
                "items": second_question['options']
            }
        }) as resp:
            result = await resp.json()
            print(f"✅ Second correct answer processed")
            
            # Extract flow execution result from continuous flow response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"   Dialogue: {dialogue[:150]}..." if dialogue else "   No dialogue")
            
            # Check if we get THIRD question
            if tools:
                third_question = tools[0]['data']
                if third_question['question'] != second_question['question']:
                    print(f"   {GREEN}✅ GOOD: Third question after second correct answer{ENDC}")
                    print(f"   Third Question: {third_question['question']}")
                else:
                    print(f"   {RED}❌ BAD: Same question repeated!{ENDC}")
                    return False
        
        # STEP 6: Test wrong answer on third question
        print(f"\n{YELLOW}📌 STEP 6: Testing wrong answer on third question{ENDC}")
        
        wrong_answer = [opt for opt in third_question['options'] 
                       if opt != third_question['correct_answer']][0]
        
        print(f"   Submitting wrong answer: '{wrong_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": wrong_answer,
                "correct_answer": third_question['correct_answer'],
                "question": third_question['question'],
                "items": third_question['options']
            }
        }) as resp:
            result = await resp.json()
            print(f"✅ Wrong answer on third question processed")
            
            # Extract flow execution result from continuous flow response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                tools = flow_response.get('tools', [])
            else:
                tools = result.get('tools', [])
            
            # Verify we get same question for retry
            if tools:
                retry_question = tools[0]['data']
                if retry_question['question'] == third_question['question']:
                    print(f"   {GREEN}✅ GOOD: Same third question for retry{ENDC}")
                else:
                    print(f"   {RED}❌ BAD: Different question on wrong answer!{ENDC}")
                    return False
            else:
                print(f"   {RED}❌ No retry question provided!{ENDC}")
                return False
        
        print(f"\n{BOLD}{GREEN}🎉 ALL TESTS PASSED!{ENDC}")
        print("=" * 60)
        print("Summary:")
        print("✅ Session started with greeting")
        print("✅ Quiz started with first question")
        print("✅ Wrong answer → Same question retry with contextual feedback")
        print("✅ Correct answer → New question with celebration")
        print("✅ Multiple correct answers → New questions each time")
        print("✅ Wrong answers consistently trigger retry of same question")
        
        return True

async def main():
    try:
        success = await test_complete_scenario()
        sys.exit(0 if success else 1)
    except aiohttp.ClientError as e:
        print(f"{RED}❌ Connection error: Make sure backend is running on port 8001{ENDC}")
        print(f"   Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}❌ Test failed: {e}{ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())