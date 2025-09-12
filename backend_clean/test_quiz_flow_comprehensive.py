#!/usr/bin/env python3
"""
Comprehensive Quiz Flow Test
Tests both correct and incorrect answer paths with detailed verification
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

async def test_comprehensive_quiz_flow():
    """Test the complete quiz workflow with verification"""
    
    base_url = "http://localhost:8001"
    session_id = None
    
    async with aiohttp.ClientSession() as session:
        print(f"{BOLD}🧪 COMPREHENSIVE QUIZ FLOW TEST{ENDC}")
        print("=" * 60)
        
        # STEP 1: Start session 
        print(f"\n{BLUE}📌 STEP 1: Starting quiz session{ENDC}")
        
        async with session.post(f"{base_url}/api/sessions/create", json={
            "user_id": "comprehensive_test_user",
            "character_id": "seol_min_seok_quiz",
            "persona_id": "default"
        }) as resp:
            result = await resp.json()
            session_id = result['data']['session']['session_id']
            print(f"✅ Session started: {session_id}")
        
        # STEP 2: Start quiz to get topic selection
        print(f"\n{BLUE}📌 STEP 2: Starting quiz{ENDC}")
        
        async with session.post(f"{base_url}/api/chat-with-session", json={
            "message": "한국사 퀴즈를 시작해주세요",
            "character_prompt": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": "comprehensive_test_user",
            "session_id": session_id
        }) as resp:
            result = await resp.json()
            
            print(f"✅ Quiz started - topic selection")
            
            if not result.get('tools'):
                print(f"❌ No topic selection provided")
                return False
                
            topic_selection = result['tools'][0]['data']
            topic_options = topic_selection.get('options', [])
            print(f"   Topics available: {topic_options}")
        
        # STEP 3: Select a topic to get actual quiz question
        print(f"\n{BLUE}📌 STEP 3: Selecting topic to get quiz question{ENDC}")
        
        selected_topic = topic_options[0] if topic_options else "조선시대"
        print(f"   Selecting topic: '{selected_topic}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer",
            "data": {
                "selection": selected_topic,
                "options": topic_options
            }
        }) as resp:
            result = await resp.json()
            
            # Extract response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                response = step_result['response']
                dialogue = response.get('dialogue', '')
                tools = response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"✅ Topic selected")
            print(f"   Dialogue: {dialogue[:100]}...")
            
            if not tools:
                print(f"❌ No quiz question provided after topic selection")
                return False
                
            first_question = tools[0]['data']
            print(f"   Tool data structure: {json.dumps(first_question, indent=2, ensure_ascii=False)}")
            
            # Handle different possible key names
            question = first_question.get('question') or first_question.get('quiz_question') or first_question.get('text', '')
            correct_answer = first_question.get('correct_answer') or first_question.get('answer', '')
            options = first_question.get('options') or first_question.get('items') or first_question.get('choices', [])
            
            print(f"   Question: {question}")
            print(f"   Correct Answer: {correct_answer}")
            print(f"   Options: {options}")
            
            if not question or not correct_answer:
                print(f"❌ Invalid quiz question structure")
                return False
        
        # STEP 4: Test WRONG answer
        print(f"\n{YELLOW}📌 STEP 4: Testing WRONG answer workflow{ENDC}")
        
        # Find a wrong answer
        wrong_answer = None
        for option in options:
            if option != correct_answer:
                wrong_answer = option
                break
                
        print(f"   Submitting wrong answer: '{wrong_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz", 
            "tool_type": "continuous_answer",
            "data": {
                "selection": wrong_answer,
                "correct_answer": correct_answer,
                "question": question,
                "items": options
            }
        }) as resp:
            result = await resp.json()
            
            # Extract response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                response = step_result['response']
                dialogue = response.get('dialogue', '')
                tools = response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"✅ Wrong answer processed")
            print(f"   Dialogue: {dialogue[:100]}...")
            
            # CRITICAL VERIFICATION: Check if the wrong answer appears in dialogue
            if wrong_answer in dialogue:
                print(f"   {GREEN}✅ GOOD: Wrong answer '{wrong_answer}' appears in feedback{ENDC}")
                wrong_feedback_correct = True
            else:
                print(f"   {RED}❌ BAD: Wrong answer '{wrong_answer}' missing from feedback{ENDC}")
                print(f"   {RED}   This indicates the user answer is not being delivered properly{ENDC}")
                wrong_feedback_correct = False
            
            # Check for retry with same question
            if tools:
                retry_question = tools[0]['data']
                retry_q = retry_question.get('question') or retry_question.get('quiz_question') or retry_question.get('text', '')
                if retry_q == question:
                    print(f"   {GREEN}✅ GOOD: Same question provided for retry{ENDC}")
                    retry_correct = True
                else:
                    print(f"   {RED}❌ BAD: Different question for retry{ENDC}")
                    retry_correct = False
            else:
                print(f"   {RED}❌ BAD: No retry question provided{ENDC}")
                retry_correct = False
        
        # STEP 5: Test CORRECT answer  
        print(f"\n{GREEN}📌 STEP 5: Testing CORRECT answer workflow{ENDC}")
        
        print(f"   Submitting correct answer: '{correct_answer}'")
        
        async with session.post(f"{base_url}/api/continuous-flow/trigger", json={
            "session_id": session_id,
            "character_id": "seol_min_seok_quiz",
            "tool_type": "continuous_answer", 
            "data": {
                "selection": correct_answer,
                "correct_answer": correct_answer,
                "question": question,
                "items": options
            }
        }) as resp:
            result = await resp.json()
            
            # Extract response
            step_result = result.get('step_result')
            if step_result and step_result.get('response'):
                response = step_result['response']
                dialogue = response.get('dialogue', '') 
                tools = response.get('tools', [])
            else:
                dialogue = result.get('dialogue', '')
                tools = result.get('tools', [])
            
            print(f"✅ Correct answer processed")
            print(f"   Dialogue: {dialogue[:100]}...")
            
            # CRITICAL VERIFICATION: Check if the correct answer appears in dialogue
            if correct_answer in dialogue:
                print(f"   {GREEN}✅ GOOD: Correct answer '{correct_answer}' appears in feedback{ENDC}")
                correct_feedback_correct = True
            else:
                print(f"   {RED}❌ BAD: Correct answer '{correct_answer}' missing from feedback{ENDC}")
                print(f"   {RED}   This indicates the user answer is not being delivered properly{ENDC}")
                correct_feedback_correct = False
            
            # Check for new question
            if tools:
                second_question = tools[0]['data']
                second_q = second_question.get('question') or second_question.get('quiz_question') or second_question.get('text', '')
                if second_q != question:
                    print(f"   {GREEN}✅ GOOD: New question after correct answer{ENDC}")
                    print(f"   New Question: {second_q}")
                    new_question_correct = True
                else:
                    print(f"   {RED}❌ BAD: Same question after correct answer{ENDC}")
                    new_question_correct = False
            else:
                print(f"   {RED}❌ BAD: No new question provided{ENDC}")
                new_question_correct = False
        
        # FINAL ASSESSMENT
        print(f"\n{BOLD}📊 TEST RESULTS{ENDC}")
        print("=" * 60)
        
        all_tests_passed = all([
            wrong_feedback_correct,
            retry_correct, 
            correct_feedback_correct,
            new_question_correct
        ])
        
        if all_tests_passed:
            print(f"{BOLD}{GREEN}🎉 ALL TESTS PASSED!{ENDC}")
            print("✅ Wrong answer feedback includes the actual user selection")
            print("✅ Wrong answer triggers retry with same question")
            print("✅ Correct answer feedback includes the actual user selection")
            print("✅ Correct answer triggers new question generation")
        else:
            print(f"{BOLD}{RED}❌ TESTS FAILED!{ENDC}")
            if not wrong_feedback_correct:
                print(f"❌ Wrong answer feedback missing user selection")
            if not retry_correct:
                print(f"❌ Wrong answer retry mechanism broken")
            if not correct_feedback_correct:
                print(f"❌ Correct answer feedback missing user selection")
            if not new_question_correct:
                print(f"❌ Correct answer new question mechanism broken")
        
        return all_tests_passed

async def main():
    try:
        success = await test_comprehensive_quiz_flow()
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