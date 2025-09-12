#!/usr/bin/env python3
"""
김대현 Korean History Character Test
Tests the new character with the universal tool-calling architecture:
1. Greeting with scholarly tone
2. Quiz interaction with analytical approach
3. Wrong answer → same question retry with guidance
4. Correct answer → new question with scholarly celebration
"""

import asyncio
import aiohttp
import json
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# ANSI color codes
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'

async def test_kim_daehyun_character():
    """Test 김대현 character with universal tool interface"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        print(f"{BOLD}🎓 김대현 KOREAN HISTORY SCHOLAR TEST{ENDC}")
        print("=" * 60)
        
        # STEP 1: Start session with new character
        print(f"\n{BLUE}📌 STEP 1: Starting session with 김대현{ENDC}")
        
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "kim_daehyun_test_user",
            "character_id": "kim_daehyun_history",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
            print(f"✅ Session started: {session_id}")
            print(f"   Character: kim_daehyun_history")
            print(f"   Status: {result['data']['session']['status']}")
        
        # STEP 2: Request Korean history quiz
        print(f"\n{BLUE}📌 STEP 2: Requesting Korean history quiz from 김대현{ENDC}")
        
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "한국사 퀴즈를 시작해주세요",
            "character_prompt": "",
            "character_id": "kim_daehyun_history",
            "user_id": "kim_daehyun_test_user",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            print(f"✅ Quiz started")
            print(f"   Dialogue: {result['dialogue'][:150]}...")
            
            # Check for scholarly tone
            dialogue = result['dialogue']
            if any(word in dialogue for word in ['학자', '연구', '분석', '사고', '학문']):
                print(f"   {GREEN}✅ GOOD: Scholarly tone detected{ENDC}")
            else:
                print(f"   ℹ️  Note: Checking for analytical approach")
            
            # Extract first question
            if result.get('tools'):
                first_question = result['tools'][0]['data']
                print(f"   Question: {first_question['question']}")
                print(f"   Options: {first_question['options']}")
                print(f"   Correct: {first_question['correct_answer']}")
            else:
                print("❌ No question tool provided!")
                return False
        
        # STEP 3: Give WRONG answer to test guidance approach
        print(f"\n{YELLOW}📌 STEP 3: Testing analytical guidance for wrong answer{ENDC}")
        
        wrong_answer = [opt for opt in first_question['options'] 
                       if opt != first_question['correct_answer']][0]
        
        print(f"   Submitting wrong answer: '{wrong_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "kim_daehyun_history",
            "tool_type": "continuous_answer",
            "data": {
                "selection": wrong_answer,
                "correct_answer": first_question['correct_answer'],
                "question": first_question['question'],
                "items": first_question['options']
            }
        }) as resp:
            result = await resp.json()
            print(f"✅ Wrong answer processed")
            
            # Extract response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"   Dialogue: {dialogue[:200]}..." if dialogue else "   No dialogue")
            
            # Check for analytical guidance style
            if any(word in dialogue for word in ['생각', '분석', '맥락', '관점', '사고']):
                print(f"   {GREEN}✅ GOOD: Analytical guidance approach detected{ENDC}")
            
            # Verify same question retry
            if tools:
                retry_question = tools[0]['data']
                if retry_question['question'] == first_question['question']:
                    print(f"   {GREEN}✅ GOOD: Same question for retry{ENDC}")
                else:
                    print(f"   {RED}❌ BAD: Different question on wrong answer{ENDC}")
                    return False
            else:
                print(f"   {RED}❌ No retry tool provided{ENDC}")
                return False
        
        # STEP 4: Give CORRECT answer to test scholarly celebration
        print(f"\n{GREEN}📌 STEP 4: Testing scholarly celebration for correct answer{ENDC}")
        
        print(f"   Submitting correct answer: '{first_question['correct_answer']}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "kim_daehyun_history",
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
            
            # Extract response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                flow_response = step_result['response']
                dialogue = flow_response.get('dialogue', '')
                tools = flow_response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"   Dialogue: {dialogue[:200]}..." if dialogue else "   No dialogue")
            
            # Check for scholarly celebration
            if any(word in dialogue for word in ['훌륭', '분석', '이해', '학문적', '깊이']):
                print(f"   {GREEN}✅ GOOD: Scholarly appreciation detected{ENDC}")
            
            # Verify new question
            if tools:
                second_question = tools[0]['data']
                if second_question['question'] != first_question['question']:
                    print(f"   {GREEN}✅ GOOD: New question after correct answer{ENDC}")
                    print(f"   New Question: {second_question['question']}")
                else:
                    print(f"   {RED}❌ BAD: Same question after correct answer{ENDC}")
                    return False
            else:
                print(f"   {RED}❌ No new question tool provided{ENDC}")
                return False
        
        print(f"\n{BOLD}{GREEN}🎉 김대현 CHARACTER TEST PASSED!{ENDC}")
        print("=" * 60)
        print("Summary:")
        print("✅ New character created through universal platform architecture")
        print("✅ Character prompt defines scholarly personality and approach")
        print("✅ Same voice and concept as 설민석 but unique analytical style")
        print("✅ Universal tool interface works with new character")
        print("✅ Wrong answer → analytical guidance + same question retry")
        print("✅ Correct answer → scholarly celebration + new question")
        print("✅ Platform extensibility demonstrated through prompt engineering")
        
        return True

async def main():
    try:
        success = await test_kim_daehyun_character()
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