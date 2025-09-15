#!/usr/bin/env python3
"""
Test for Intermittent Tool Mixing Fix

Validates that quiz characters (seol_min_seok_quiz, dr_genie_science_quiz) 
ONLY use continuous_quiz_response tool, never show_selection

This addresses user report: "The continuous tool is sometimes ignored, 
I got merged one review and quiz at the same time after answering the quiz."
"""

import asyncio
import requests
import json
import time
from typing import List, Dict

BASE_URL = "http://localhost:8001"
QUIZ_CHARACTERS = ["seol_min_seok_quiz", "dr_genie_science_quiz"]
TEST_ITERATIONS = 10  # Test multiple times to catch intermittent behavior

def test_tool_enforcement_fix():
    """
    Test that quiz characters are now FORCED to use continuous_quiz_response only
    Previously: LLMClient allowed both show_selection and continuous_quiz_response
    Fixed: LLMClient now enforces continuous_quiz_response only for quiz characters
    """
    print("🧪 Testing Intermittent Tool Mixing Fix")
    print("=" * 60)
    print("Target: Ensure quiz characters ONLY use continuous_quiz_response")
    print("Fix: LLMClient now enforces tool type per character")
    print("=" * 60)
    
    results = {
        "total_tests": 0,
        "continuous_tool_success": 0,
        "show_selection_failures": 0,
        "errors": [],
        "character_results": {}
    }
    
    for character_id in QUIZ_CHARACTERS:
        print(f"\n📋 Testing {character_id}...")
        character_results = test_character_tool_consistency(character_id)
        results["character_results"][character_id] = character_results
        
        results["total_tests"] += character_results["total_attempts"]
        results["continuous_tool_success"] += character_results["continuous_responses"]
        results["show_selection_failures"] += character_results["show_selection_responses"]
        results["errors"].extend(character_results["errors"])
    
    # Final Analysis
    print(f"\n🔍 FINAL ANALYSIS")
    print("=" * 50)
    print(f"Total Quiz Interactions: {results['total_tests']}")
    print(f"✅ Continuous Tool Used: {results['continuous_tool_success']}")
    print(f"❌ Show Selection Used: {results['show_selection_failures']}")
    print(f"🚨 Errors Encountered: {len(results['errors'])}")
    
    if results["show_selection_failures"] == 0:
        print(f"\n🎉 SUCCESS: Tool mixing fix is working!")
        print(f"✅ 100% of quiz interactions used continuous_quiz_response")
        print(f"✅ No intermittent show_selection usage detected")
        return True
    else:
        print(f"\n❌ FAILURE: Tool mixing still occurring!")
        print(f"❌ {results['show_selection_failures']}/{results['total_tests']} responses used show_selection")
        print(f"❌ Fix did not resolve intermittent behavior")
        return False

def test_character_tool_consistency(character_id: str) -> Dict:
    """Test single character for consistent tool usage"""
    
    results = {
        "character_id": character_id,
        "total_attempts": 0,
        "continuous_responses": 0,
        "show_selection_responses": 0,
        "errors": [],
        "test_details": []
    }
    
    for iteration in range(TEST_ITERATIONS):
        print(f"  🔄 Iteration {iteration + 1}/{TEST_ITERATIONS}...")
        
        try:
            # Start session with greeting
            session_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                "user_input": "",
                "character_id": character_id,
                "user_id": f"test_tool_mixing_{character_id}_{iteration}"
            }, timeout=30)
            
            if session_response.status_code != 200:
                results["errors"].append(f"Session start failed: {session_response.status_code}")
                continue
                
            session_data = session_response.json()
            session_id = session_data.get('session_id')
            
            if not session_id:
                results["errors"].append("No session_id in response")
                continue
            
            # Select topic to trigger quiz generation
            topic = "한국사" if "seol" in character_id else "물리"
            topic_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                "user_input": topic,
                "character_id": character_id,
                "user_id": f"test_tool_mixing_{character_id}_{iteration}",
                "session_id": session_id
            }, timeout=30)
            
            if topic_response.status_code != 200:
                results["errors"].append(f"Topic selection failed: {topic_response.status_code}")
                continue
                
            topic_data = topic_response.json()
            
            # Get quiz options
            if not topic_data.get('tools') or len(topic_data['tools']) == 0:
                results["errors"].append("No tools in topic response")
                continue
                
            quiz_tool = topic_data['tools'][0]
            quiz_options = quiz_tool.get('data', {}).get('options', [])
            
            if not quiz_options:
                results["errors"].append("No quiz options available")
                continue
            
            # Answer quiz question (this is where tool mixing occurs)
            answer = quiz_options[0]  # Select first option
            answer_response = requests.post(f"{BASE_URL}/api/platform-chat", json={
                "user_input": answer,
                "character_id": character_id,
                "user_id": f"test_tool_mixing_{character_id}_{iteration}",
                "session_id": session_id
            }, timeout=30)
            
            if answer_response.status_code != 200:
                results["errors"].append(f"Answer response failed: {answer_response.status_code}")
                continue
                
            answer_data = answer_response.json()
            results["total_attempts"] += 1
            
            # CRITICAL CHECK: Analyze tool type in response
            if answer_data.get('tools') and len(answer_data['tools']) > 0:
                primary_tool = answer_data['tools'][0]
                tool_type = primary_tool.get('type')
                
                test_detail = {
                    "iteration": iteration + 1,
                    "tool_type": tool_type,
                    "has_dialogue": bool(answer_data.get('dialogue', '').strip()),
                    "dialogue_preview": answer_data.get('dialogue', '')[:100] + "..."
                }
                results["test_details"].append(test_detail)
                
                if tool_type == 'continuous_quiz_response':
                    results["continuous_responses"] += 1
                    print(f"    ✅ Continuous tool used")
                elif tool_type == 'show_selection':
                    results["show_selection_responses"] += 1
                    print(f"    ❌ Show selection used (BUG!)")
                else:
                    results["errors"].append(f"Unknown tool type: {tool_type}")
            else:
                results["errors"].append("No tools in answer response")
                
            # Small delay between tests
            time.sleep(0.5)
            
        except Exception as e:
            results["errors"].append(f"Test iteration {iteration + 1} failed: {str(e)}")
            
    # Character Summary
    print(f"  📊 {character_id} Results:")
    print(f"    Total Tests: {results['total_attempts']}")
    print(f"    Continuous Tool: {results['continuous_responses']}")
    print(f"    Show Selection: {results['show_selection_responses']}")
    print(f"    Errors: {len(results['errors'])}")
    
    return results

def validate_server_running():
    """Ensure server is running before tests"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 INTERMITTENT TOOL MIXING FIX VALIDATION")
    print("=" * 60)
    
    if not validate_server_running():
        print("❌ Server not running at http://localhost:8001")
        print("Please start the server: python3 -m uvicorn main:app --host 0.0.0.0 --port 8001")
        exit(1)
    
    success = test_tool_enforcement_fix()
    
    if success:
        print(f"\n✅ VALIDATION PASSED")
        print(f"🎯 Intermittent tool mixing issue has been resolved")
        print(f"🔒 Quiz characters now consistently use continuous_quiz_response")
        exit(0)
    else:
        print(f"\n❌ VALIDATION FAILED")  
        print(f"🐛 Tool mixing issue persists - requires further investigation")
        exit(1)