#!/usr/bin/env python3
"""
Test Continuous Tool Reliability
Run multiple iterations to identify patterns in when continuous_quiz_response is ignored
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def run_single_quiz_iteration(iteration_num):
    """Run single quiz interaction and return result analysis"""
    
    print(f"\n🔄 ITERATION {iteration_num}")
    print("-" * 40)
    
    try:
        # Step 1: Create session and get greeting
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": "",
            "character_id": "seol_min_seok_quiz",
            "user_id": f"test_reliability_{iteration_num}"
        })
        
        if response.status_code != 200:
            return {"success": False, "error": f"Session creation failed: {response.status_code}"}
            
        data = response.json()
        session_id = data["session_id"]
        
        # Step 2: Select topic
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": "현대사",
            "character_id": "seol_min_seok_quiz",
            "session_id": session_id,
            "user_id": f"test_reliability_{iteration_num}"
        })
        
        if response.status_code != 200:
            return {"success": False, "error": f"Topic selection failed: {response.status_code}"}
            
        data = response.json()
        tools = data.get("tools", [])
        
        if not tools or tools[0].get('type') != 'show_selection':
            return {"success": False, "error": f"Expected show_selection, got: {tools}"}
            
        first_question = tools[0]['data']['question']
        first_options = tools[0]['data']['options']
        
        # Find correct answer (이승만 for first president question)
        correct_answer = None
        for option in first_options:
            if "이승만" in option:
                correct_answer = option
                break
        
        if not correct_answer:
            correct_answer = first_options[0]  # fallback
        
        # Step 3: Answer first question CORRECTLY
        response = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": correct_answer,
            "character_id": "seol_min_seok_quiz", 
            "session_id": session_id,
            "user_id": f"test_reliability_{iteration_num}"
        })
        
        if response.status_code != 200:
            return {"success": False, "error": f"Answer submission failed: {response.status_code}"}
            
        data = response.json()
        tools = data.get("tools", [])
        dialogue = data.get("dialogue", "")
        
        # Analyze the response
        analysis = {
            "success": True,
            "iteration": iteration_num,
            "session_id": session_id,
            "question": first_question[:50] + "...",
            "correct_answer": correct_answer,
            "dialogue_length": len(dialogue),
            "dialogue_preview": dialogue[:100] + "..." if len(dialogue) > 100 else dialogue,
            "tools_count": len(tools),
        }
        
        if not tools:
            analysis["result"] = "NO_TOOLS"
            analysis["issue"] = "No tools returned - possible system error"
            print(f"❌ NO TOOLS: {analysis['issue']}")
            
        elif tools[0].get('type') == 'continuous_quiz_response':
            analysis["result"] = "SUCCESS_CONTINUOUS"
            analysis["tool_type"] = "continuous_quiz_response"
            
            # Check phase structure
            phase1 = tools[0]['data'].get('phase1', {})
            phase2 = tools[0]['data'].get('phase2', {})
            
            analysis["phase1_text_length"] = len(phase1.get('text', ''))
            analysis["phase2_has_tool"] = 'tool' in phase2
            analysis["phase2_tool_type"] = phase2.get('tool', {}).get('type', 'none')
            
            print(f"✅ SUCCESS: Got continuous_quiz_response")
            print(f"   Phase1 length: {analysis['phase1_text_length']}")
            print(f"   Phase2 tool: {analysis['phase2_tool_type']}")
            
        elif tools[0].get('type') == 'show_selection':
            analysis["result"] = "FAILURE_MERGED"
            analysis["tool_type"] = "show_selection"
            analysis["next_question"] = tools[0]['data'].get('question', '')[:50] + "..."
            
            # Check if dialogue contains merged content
            analysis["has_celebration"] = any(word in dialogue.lower() for word in ['정답', '맞', '훌륭', '좋아'])
            analysis["has_next_question"] = any(word in dialogue for word in ['다음', '문제', '질문'])
            analysis["is_merged"] = analysis["has_celebration"] and analysis["has_next_question"]
            
            print(f"❌ FAILURE: Got show_selection instead of continuous_quiz_response")
            print(f"   Has celebration: {analysis['has_celebration']}")
            print(f"   Has next question: {analysis['has_next_question']}")
            print(f"   Is merged content: {analysis['is_merged']}")
            
        else:
            analysis["result"] = "UNKNOWN_TOOL"
            analysis["tool_type"] = tools[0].get('type', 'unknown')
            print(f"❓ UNKNOWN: Got unexpected tool type: {analysis['tool_type']}")
            
        return analysis
        
    except Exception as e:
        return {
            "success": False,
            "iteration": iteration_num,
            "error": f"Exception: {str(e)}"
        }

def test_continuous_tool_reliability(iterations=10):
    """Run multiple iterations to analyze continuous tool reliability patterns"""
    
    print("🔍 TESTING CONTINUOUS TOOL RELIABILITY")
    print(f"Running {iterations} iterations...")
    print("=" * 50)
    
    results = []
    success_count = 0
    failure_count = 0
    error_count = 0
    
    for i in range(1, iterations + 1):
        result = run_single_quiz_iteration(i)
        results.append(result)
        
        if not result.get("success"):
            error_count += 1
        elif result.get("result") == "SUCCESS_CONTINUOUS":
            success_count += 1
        elif result.get("result") == "FAILURE_MERGED":
            failure_count += 1
        
        # Small delay between iterations
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print("📊 RELIABILITY ANALYSIS")
    print("=" * 50)
    
    print(f"Total iterations: {iterations}")
    print(f"✅ Successful continuous responses: {success_count}")
    print(f"❌ Failed (merged) responses: {failure_count}")
    print(f"🔥 System errors: {error_count}")
    print(f"📈 Success rate: {success_count/iterations*100:.1f}%")
    print(f"📉 Failure rate: {failure_count/iterations*100:.1f}%")
    
    # Pattern analysis
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        if result.get("success"):
            status = "✅" if result.get("result") == "SUCCESS_CONTINUOUS" else "❌"
            print(f"{status} Iter {result['iteration']}: {result['result']} - {result.get('tool_type', 'none')}")
        else:
            print(f"🔥 Iter {result['iteration']}: ERROR - {result.get('error', 'unknown')}")
    
    # Save results to file for analysis
    with open('continuous_tool_reliability_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: continuous_tool_reliability_results.json")
    
    return {
        "total": iterations,
        "success": success_count,
        "failure": failure_count,
        "errors": error_count,
        "success_rate": success_count/iterations*100,
        "results": results
    }

if __name__ == "__main__":
    # Run reliability test
    test_continuous_tool_reliability(10)