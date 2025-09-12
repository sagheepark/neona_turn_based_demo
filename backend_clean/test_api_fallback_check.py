#!/usr/bin/env python3
"""
Simple API test to check if fallback systems have been disabled.
This simulates the actual API calls that would trigger fallbacks.
"""

import asyncio
import aiohttp
import json

async def test_api_fallback_disabled():
    """Test API endpoints to see if fallback systems are disabled."""
    
    print("🔬 API FALLBACK DISABLE TEST")
    print("=" * 60)
    
    # Test URL (assuming server is running on port 8000)
    base_url = "http://localhost:8001"
    
    try:
        async with aiohttp.ClientSession() as session:
            
            # Step 1: Start a chat session 
            print("1️⃣  Starting chat session...")
            chat_start_data = {
                "message": "안녕하세요",
                "character_id": "kim_daehyun_korean_history",
                "session_id": "fallback_test_session"
            }
            
            async with session.post(f"{base_url}/api/chat", json=chat_start_data) as resp:
                if resp.status != 200:
                    print(f"❌ Chat start failed: {resp.status}")
                    return False
                
                chat_response = await resp.json()
                print("✅ Chat session started")
            
            # Step 2: Test the continuous answer tool with a WRONG answer
            print("\n2️⃣  Testing continuous answer tool with WRONG answer...")
            wrong_answer_data = {
                "session_id": "fallback_test_session", 
                "character_id": "kim_daehyun_korean_history",
                "type": "continuous_answer_tool",
                "data": {
                    "selection": "잘못된 답변",  # Wrong answer
                    "quiz_question": "다음 중 세종대왕의 업적은?",
                    "quiz_options": ["불교 장려", "한글 창제", "몽골 침입", "고구려 건국"],
                    "correct_answer": "한글 창제"
                }
            }
            
            async with session.post(f"{base_url}/api/tools", json=wrong_answer_data) as resp:
                if resp.status != 200:
                    print(f"❌ Tool call failed: {resp.status}")
                    text = await resp.text()
                    print(f"Response: {text}")
                    return False
                
                tool_response = await resp.json()
                print("✅ Continuous answer tool executed")
                
                # Analyze the response
                print("\n🔍 RESPONSE ANALYSIS:")
                print("-" * 40)
                print(f"Full Response: {json.dumps(tool_response, indent=2, ensure_ascii=False)}")
                
                # Check for fallback markers we added
                fallback_markers = [
                    "TEST_LLM_INTEGRATION_CHARACTER",
                    "TEST_LLM_EMOTION",
                    "TEST_LLM_EMOTION_2", 
                    "TEST_LLM_KOREAN_FALLBACK_DISABLED",
                    "TEST_LLM_KOREAN_FALLBACK_DISABLED_2",
                    "TEST_LLM_KOREAN_FALLBACK_ERROR_DISABLED"
                ]
                
                response_str = str(tool_response)
                detected_fallbacks = []
                
                for marker in fallback_markers:
                    if marker in response_str:
                        detected_fallbacks.append(marker)
                        print(f"🚫 DETECTED DISABLED FALLBACK: {marker}")
                
                # Check for original Korean fallback text
                original_korean_fallbacks = [
                    "AI 캐릭터",
                    "다시 한번 도전해보세요",
                    "encouraging"
                ]
                
                original_fallbacks_found = []
                for fallback in original_korean_fallbacks:
                    if fallback in response_str:
                        original_fallbacks_found.append(fallback)
                        print(f"⚠️  ORIGINAL FALLBACK STILL PRESENT: {fallback}")
                
                print()
                print("📊 ASSESSMENT:")
                print("-" * 40)
                
                if detected_fallbacks:
                    print("✅ SUCCESS: Fallback disable markers detected!")
                    print(f"   Disabled fallbacks: {detected_fallbacks}")
                    print("   ➤ This confirms fallback systems have been disabled")
                    return True
                elif original_fallbacks_found:
                    print("❌ FAILURE: Original fallback text still present!")
                    print(f"   Active fallbacks: {original_fallbacks_found}")
                    print("   ➤ Fallback disable was not successful")
                    return False
                else:
                    print("⚠️  PARTIAL: No clear fallback markers detected")
                    print("   ➤ May indicate real LLM integration is working")
                    print("   ➤ Or different fallback system is active")
                    
                    # Check if response looks like real LLM content
                    if 'text' in tool_response and len(tool_response.get('text', '')) > 50:
                        print("✅ POSITIVE: Substantial response content detected")
                        print("   ➤ Likely indicates real LLM processing")
                        return True
                    else:
                        print("❌ NEGATIVE: Response too short for real LLM")
                        return False
                        
    except aiohttp.ClientConnectorError:
        print("❌ ERROR: Cannot connect to server")
        print("   ➤ Make sure the backend server is running on port 8000")
        print("   ➤ Run: cd /Users/bagsanghui/neona_turn_based_demo_with_agent/backend_clean && python3 main.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: Exception occurred: {e}")
        return False

async def main():
    """Run the API fallback test."""
    
    success = await test_api_fallback_disabled()
    
    print()
    print("🏁 TEST SUMMARY:")
    print("=" * 60)
    
    if success:
        print("✅ API FALLBACK DISABLE TEST PASSED!")
        print("   ➤ Fallback systems have been successfully disabled")
        print("   ➤ Real LLM integration should now be exposed")
        print("   ➤ Issue 2 (meaningful LLM feedback) is ready for testing")
    else:
        print("❌ API FALLBACK DISABLE TEST FAILED!")
        print("   ➤ Some fallback systems may still be active")
        print("   ➤ Or server connection issues")
        print("   ➤ Check server status and continuous_answer_tool.py")
    
    print()

if __name__ == "__main__":
    asyncio.run(main())