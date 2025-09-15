#!/usr/bin/env python3
"""
Complete Character Comparison Test
Validates both seol_min_seok_quiz and dr_genie_science_quiz end-to-end
"""

import requests
import json
import time

def test_character_complete_flow(character_id: str, topic: str) -> dict:
    """Test complete flow for a character"""
    BASE_URL = "http://localhost:8001"
    
    results = {
        "character_id": character_id,
        "topic": topic,
        "greeting": {"status": "unknown", "details": {}},
        "topic_selection": {"status": "unknown", "details": {}},
        "quiz_answer": {"status": "unknown", "details": {}}
    }
    
    print(f"\n🧪 Testing {character_id} with topic '{topic}'")
    print("=" * 60)
    
    try:
        # Step 1: Greeting
        print("📋 Step 1: Testing greeting...")
        response1 = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": "",
            "character_id": character_id,
            "user_id": f"test_{character_id}"
        }, timeout=30)
        
        if response1.status_code == 200:
            data1 = response1.json()
            session_id = data1.get('session_id')
            
            results["greeting"] = {
                "status": "success",
                "details": {
                    "has_dialogue": bool(data1.get('dialogue', '').strip()),
                    "has_audio": bool(data1.get('audio_url')),
                    "has_tools": len(data1.get('tools', [])),
                    "tool_type": data1.get('tools', [{}])[0].get('type') if data1.get('tools') else None,
                    "session_id": session_id,
                    "dialogue_preview": data1.get('dialogue', '')[:100] + "..."
                }
            }
            print(f"✅ Greeting: dialogue={results['greeting']['details']['has_dialogue']}, "
                  f"audio={results['greeting']['details']['has_audio']}, "
                  f"tools={results['greeting']['details']['has_tools']}")
        else:
            results["greeting"] = {
                "status": "failed",
                "details": {"error": f"HTTP {response1.status_code}: {response1.text}"}
            }
            print(f"❌ Greeting failed: {response1.status_code}")
            return results
            
        # Step 2: Topic Selection
        print("📋 Step 2: Testing topic selection...")
        response2 = requests.post(f"{BASE_URL}/api/platform-chat", json={
            "user_input": topic,
            "character_id": character_id,
            "user_id": f"test_{character_id}",
            "session_id": session_id
        }, timeout=30)
        
        if response2.status_code == 200:
            data2 = response2.json()
            tool_data = data2.get('tools', [{}])[0].get('data', {}) if data2.get('tools') else {}
            
            results["topic_selection"] = {
                "status": "success",
                "details": {
                    "has_dialogue": bool(data2.get('dialogue', '').strip()),
                    "has_audio": bool(data2.get('audio_url')),
                    "has_tools": len(data2.get('tools', [])),
                    "tool_type": data2.get('tools', [{}])[0].get('type') if data2.get('tools') else None,
                    "has_question": bool(tool_data.get('question', '')),
                    "has_options": len(tool_data.get('options', [])),
                    "question_preview": tool_data.get('question', '')[:100] + "...",
                    "dialogue_preview": data2.get('dialogue', '')[:100] + "..."
                }
            }
            print(f"✅ Topic selection: dialogue={results['topic_selection']['details']['has_dialogue']}, "
                  f"audio={results['topic_selection']['details']['has_audio']}, "
                  f"question={results['topic_selection']['details']['has_question']}, "
                  f"options={results['topic_selection']['details']['has_options']}")
                  
            # Step 3: Answer a quiz question (if available)
            if tool_data.get('options') and len(tool_data['options']) > 0:
                print("📋 Step 3: Testing quiz answer...")
                first_option = tool_data['options'][0]
                
                response3 = requests.post(f"{BASE_URL}/api/platform-chat", json={
                    "user_input": first_option,
                    "character_id": character_id,
                    "user_id": f"test_{character_id}",
                    "session_id": session_id
                }, timeout=30)
                
                if response3.status_code == 200:
                    data3 = response3.json()
                    results["quiz_answer"] = {
                        "status": "success",
                        "details": {
                            "has_dialogue": bool(data3.get('dialogue', '').strip()),
                            "has_audio": bool(data3.get('audio_url')),
                            "has_tools": len(data3.get('tools', [])),
                            "tool_type": data3.get('tools', [{}])[0].get('type') if data3.get('tools') else None,
                            "answered_option": first_option,
                            "dialogue_preview": data3.get('dialogue', '')[:100] + "..."
                        }
                    }
                    print(f"✅ Quiz answer: dialogue={results['quiz_answer']['details']['has_dialogue']}, "
                          f"audio={results['quiz_answer']['details']['has_audio']}, "
                          f"tools={results['quiz_answer']['details']['has_tools']}")
                else:
                    results["quiz_answer"] = {
                        "status": "failed",
                        "details": {"error": f"HTTP {response3.status_code}: {response3.text}"}
                    }
                    print(f"❌ Quiz answer failed: {response3.status_code}")
            else:
                results["quiz_answer"] = {
                    "status": "skipped",
                    "details": {"reason": "No quiz options available"}
                }
                print("⚠️ Quiz answer skipped: No options available")
        else:
            results["topic_selection"] = {
                "status": "failed", 
                "details": {"error": f"HTTP {response2.status_code}: {response2.text}"}
            }
            print(f"❌ Topic selection failed: {response2.status_code}")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        results["error"] = str(e)
        
    return results

def compare_characters():
    """Compare both characters side by side"""
    
    print("🔍 COMPREHENSIVE CHARACTER COMPARISON TEST")
    print("=" * 80)
    print("Testing both seol_min_seok_quiz and dr_genie_science_quiz")
    print("Validating greeting, topic selection, and quiz flow")
    print("=" * 80)
    
    # Test both characters
    seol_results = test_character_complete_flow("seol_min_seok_quiz", "한국사")
    science_results = test_character_complete_flow("dr_genie_science_quiz", "물리")
    
    # Compare results
    print(f"\n🔄 COMPARISON RESULTS")
    print("=" * 80)
    
    phases = ["greeting", "topic_selection", "quiz_answer"]
    
    for phase in phases:
        print(f"\n📊 {phase.upper()} COMPARISON:")
        seol_status = seol_results[phase]["status"]
        science_status = science_results[phase]["status"]
        
        print(f"  seol_min_seok_quiz: {seol_status}")
        print(f"  dr_genie_science_quiz: {science_status}")
        
        if seol_status == "success" and science_status == "success":
            # Compare details
            seol_details = seol_results[phase]["details"]
            science_details = science_results[phase]["details"]
            
            for key in ["has_dialogue", "has_audio", "has_tools"]:
                if key in seol_details and key in science_details:
                    seol_val = seol_details[key]
                    science_val = science_details[key]
                    status = "✅" if seol_val == science_val else "❌"
                    print(f"    {key}: seol={seol_val}, science={science_val} {status}")
        
    # Final verdict
    print(f"\n🏆 FINAL VERDICT:")
    print("=" * 50)
    
    all_seol_success = all(seol_results[phase]["status"] == "success" for phase in phases if seol_results[phase]["status"] != "skipped")
    all_science_success = all(science_results[phase]["status"] == "success" for phase in phases if science_results[phase]["status"] != "skipped")
    
    if all_seol_success and all_science_success:
        print("🎉 BOTH CHARACTERS WORKING CORRECTLY")
        print("✅ seol_min_seok_quiz: Fully functional")
        print("✅ dr_genie_science_quiz: Fully functional")
        print("\n💡 USER ISSUE ANALYSIS:")
        print("- Backend integration is working correctly for both characters")
        print("- Issue likely frontend-specific or user environment related")
        print("- Recommend frontend browser refresh or cache clearing")
    elif all_seol_success and not all_science_success:
        print("⚠️  SCIENCE CHARACTER HAS ISSUES")
        print("✅ seol_min_seok_quiz: Working correctly")
        print("❌ dr_genie_science_quiz: Has problems")
        print("\n🔧 RECOMMENDED FIXES:")
        print("- Check science character specific configuration")
        print("- Verify TTS service integration for science character")
        print("- Review LLM prompts for science character")
    else:
        print("❌ BOTH CHARACTERS HAVE ISSUES")
        print("🚨 Fundamental system problems detected")
        
    # Save detailed results
    with open("/Users/bagsanghui/neona_turn_based_demo_with_agent/character_comparison_results.json", "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "seol_min_seok_quiz": seol_results,
            "dr_genie_science_quiz": science_results
        }, f, indent=2, ensure_ascii=False)
        
    print(f"\n📁 Detailed results saved to: character_comparison_results.json")

if __name__ == "__main__":
    compare_characters()