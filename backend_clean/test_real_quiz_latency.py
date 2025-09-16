"""
Real Quiz Latency Test

Tests actual production latency with complete prompt structure including:
- System prompt
- Character prompt  
- Tool definitions
- Chat history
- Quiz context
- User answer

Simulates a real quiz answer scenario to measure end-to-end performance.
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

class RealQuizLatencyTester:
    """Test real quiz latency with production-like conditions"""
    
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.session_id = None
        self.character_id = "seol_min_seok_quiz"
        
    async def test_complete_quiz_flow(self):
        """Test complete quiz flow with real prompts and measure latencies"""
        
        print("🧪 REAL QUIZ LATENCY TEST")
        print("=" * 80)
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 Character: {self.character_id}")
        print()
        
        # Check server availability
        if not await self._check_server():
            return
        
        try:
            # Step 1: Initial greeting (establishes session)
            print("📋 STEP 1: Initial Greeting & Topic Selection")
            print("-" * 60)
            
            greeting_start = time.time()
            greeting_response = await self._make_request("", "Initial greeting")
            greeting_time = (time.time() - greeting_start) * 1000
            
            if greeting_response:
                self.session_id = greeting_response.get('session_id')
                print(f"✅ Greeting completed: {greeting_time:.1f}ms")
                print(f"   Session ID: {self.session_id}")
                print(f"   Response: {greeting_response.get('dialogue', '')[:100]}...")
                print(f"   Tools: {len(greeting_response.get('tools', []))} tools provided")
            else:
                print("❌ Greeting failed")
                return
            
            print()
            await asyncio.sleep(1)  # Brief pause
            
            # Step 2: Topic selection
            print("📋 STEP 2: Topic Selection")
            print("-" * 60)
            
            topic_start = time.time()
            topic_response = await self._make_request("조선시대", "Topic selection")
            topic_time = (time.time() - topic_start) * 1000
            
            if topic_response:
                print(f"✅ Topic selection completed: {topic_time:.1f}ms")
                print(f"   Response: {topic_response.get('dialogue', '')[:100]}...")
                print(f"   Tools: {len(topic_response.get('tools', []))} tools provided")
                
                # Extract quiz question if available
                tools = topic_response.get('tools', [])
                quiz_question = None
                quiz_options = []
                
                for tool in tools:
                    if tool.get('type') == 'show_selection':
                        data = tool.get('data', {})
                        if data.get('selection_mode') == 'quiz_question':
                            quiz_question = data.get('question')
                            quiz_options = data.get('options', [])
                            break
                
                if quiz_question:
                    print(f"   📝 Quiz Question: {quiz_question}")
                    print(f"   📋 Options: {quiz_options}")
            else:
                print("❌ Topic selection failed")
                return
            
            print()
            await asyncio.sleep(1)  # Brief pause
            
            # Step 3: Quiz answer (MAIN TEST - with complete prompt structure)
            print("📋 STEP 3: Quiz Answer with Complete Prompt Structure")
            print("-" * 60)
            
            # Test both correct and incorrect answers
            test_answers = [
                {"answer": "이성계", "type": "correct", "description": "Correct answer for 조선 건국자"},
                {"answer": "박정희", "type": "incorrect", "description": "Incorrect answer to test feedback flow"}
            ]
            
            for i, test_case in enumerate(test_answers, 1):
                print(f"🎯 Test Case {i}: {test_case['description']}")
                print(f"   Answer: '{test_case['answer']}'")
                
                # Measure detailed latency
                answer_start = time.time()
                
                # Make the quiz answer request
                answer_response = await self._make_detailed_request(
                    test_case['answer'], 
                    f"Quiz answer ({test_case['type']})"
                )
                
                answer_time = (time.time() - answer_start) * 1000
                
                if answer_response:
                    print(f"   ✅ Answer processed: {answer_time:.1f}ms total")
                    print(f"   📝 Response: {answer_response.get('dialogue', '')[:100]}...")
                    
                    # Check for continuous quiz response
                    tools = answer_response.get('tools', [])
                    has_continuous = any(t.get('type') == 'continuous_quiz_response' for t in tools)
                    has_show_selection = any(t.get('type') == 'show_selection' for t in tools)
                    
                    print(f"   🔧 Tools: {len(tools)} tools")
                    print(f"   🔄 Continuous flow: {'Yes' if has_continuous else 'No'}")
                    print(f"   📋 Show selection: {'Yes' if has_show_selection else 'No'}")
                    
                    # Analyze audio response
                    audio_url = answer_response.get('audio_url')
                    streaming_audio = answer_response.get('streaming_audio')
                    
                    if streaming_audio:
                        print(f"   🎵 Audio: Streaming ({streaming_audio.get('total_chunks', 0)} chunks)")
                        print(f"   ⏱️  Estimated total: {streaming_audio.get('estimated_total_time', 0):.0f}ms")
                    elif audio_url:
                        print(f"   🎵 Audio: Single TTS generated")
                    else:
                        print(f"   🎵 Audio: None")
                    
                else:
                    print(f"   ❌ Answer processing failed")
                
                print()
                
                if i < len(test_answers):
                    await asyncio.sleep(2)  # Pause between test cases
            
            # Step 4: Get performance statistics
            print("📊 PERFORMANCE ANALYSIS")
            print("-" * 60)
            
            await self._analyze_performance()
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    async def _check_server(self) -> bool:
        """Check if server is running and responsive"""
        try:
            response = requests.get(f"{self.base_url}/api/models", timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and responsive")
                return True
            else:
                print(f"❌ Server responded with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Server is not running. Please start the server first:")
            print("   cd backend_clean && python3 main.py")
            return False
        except Exception as e:
            print(f"❌ Server check failed: {e}")
            return False
    
    async def _make_request(self, user_input: str, description: str) -> Dict[Any, Any]:
        """Make a basic API request"""
        try:
            payload = {
                "user_input": user_input,
                "character_id": self.character_id,
                "user_id": "test_user"
            }
            
            if self.session_id:
                payload["session_id"] = self.session_id
            
            response = requests.post(
                f"{self.base_url}/api/platform-chat",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ API call failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    async def _make_detailed_request(self, user_input: str, description: str) -> Dict[Any, Any]:
        """Make a detailed request with performance tracking"""
        
        print(f"   🚀 Making request: {description}")
        
        # Track individual components
        request_start = time.time()
        
        try:
            payload = {
                "user_input": user_input,
                "character_id": self.character_id,
                "user_id": "test_user"
            }
            
            if self.session_id:
                payload["session_id"] = self.session_id
            
            print(f"   📤 Payload prepared: {json.dumps(payload, separators=(',', ':'))}")
            
            # Make request
            network_start = time.time()
            response = requests.post(
                f"{self.base_url}/api/platform-chat",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            network_time = (time.time() - network_start) * 1000
            
            print(f"   🌐 Network request: {network_time:.1f}ms")
            
            if response.status_code == 200:
                # Parse response
                parse_start = time.time()
                data = response.json()
                parse_time = (time.time() - parse_start) * 1000
                
                print(f"   📥 Response parsing: {parse_time:.1f}ms")
                
                total_time = (time.time() - request_start) * 1000
                print(f"   ⏱️  Total request time: {total_time:.1f}ms")
                
                return data
            else:
                print(f"   ❌ API call failed: HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"   ❌ Detailed request failed: {e}")
            return None
    
    async def _analyze_performance(self):
        """Analyze performance statistics from the server"""
        
        try:
            # Get overall performance stats
            stats_response = requests.get(f"{self.base_url}/api/performance/stats", timeout=10)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                
                if stats_data.get("status") == "success":
                    perf_stats = stats_data.get("performance_stats", {})
                    
                    print("📊 PERFORMANCE STATISTICS:")
                    print(f"   📈 Total Requests: {perf_stats.get('total_requests_tracked', 0)}")
                    print(f"   🔄 Active Requests: {perf_stats.get('active_requests', 0)}")
                    print()
                    print("⏱️  AVERAGE LATENCIES:")
                    print(f"   📱 Total Request: {perf_stats.get('avg_total_duration_ms', 0):.1f}ms")
                    print(f"   🧠 LLM Operations: {perf_stats.get('avg_llm_duration_ms', 0):.1f}ms")
                    print(f"   🎵 TTS Operations: {perf_stats.get('avg_tts_duration_ms', 0):.1f}ms")
                    print(f"   🌐 Network Operations: {perf_stats.get('avg_network_duration_ms', 0):.1f}ms")
                    print()
                    print("📊 OPERATION COUNTS:")
                    print(f"   🧠 LLM Calls: {perf_stats.get('llm_operations_count', 0)}")
                    print(f"   🎵 TTS Generations: {perf_stats.get('tts_operations_count', 0)}")
                    print(f"   🌐 Network Requests: {perf_stats.get('network_operations_count', 0)}")
                    
                    # Calculate performance rating
                    avg_total = perf_stats.get('avg_total_duration_ms', 0)
                    if avg_total < 2000:
                        rating = "🚀 EXCELLENT"
                    elif avg_total < 3000:
                        rating = "✅ GOOD"
                    elif avg_total < 5000:
                        rating = "⚠️ ACCEPTABLE"
                    else:
                        rating = "❌ SLOW"
                    
                    print(f"   🎯 Overall Performance: {rating}")
                    
                else:
                    print("⚠️ Performance statistics not available")
            else:
                print(f"❌ Failed to get performance stats: HTTP {stats_response.status_code}")
        
        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")
        
        print()
        
        # Get detailed recent requests
        try:
            recent_response = requests.get(f"{self.base_url}/api/performance/recent-requests?limit=3", timeout=10)
            
            if recent_response.status_code == 200:
                recent_data = recent_response.json()
                
                if recent_data.get("status") == "success":
                    requests_data = recent_data.get("recent_requests", [])
                    
                    print("🔍 RECENT REQUEST BREAKDOWN:")
                    
                    for idx, req in enumerate(requests_data[-3:], 1):  # Last 3 requests
                        print(f"   📋 Request {idx}: {req['user_input'][:30]}...")
                        print(f"      Total: {req['total_duration_ms']:.1f}ms")
                        print(f"      Character: {req['character_id']}")
                        
                        # Show operation breakdown
                        for op in req.get('breakdown', [])[:5]:  # Top 5 operations
                            status = "✅" if op['success'] else "❌"
                            print(f"         {status} {op['operation']}: {op['duration_ms']:.1f}ms")
                        
                        print()
                
            else:
                print(f"❌ Failed to get recent requests: HTTP {recent_response.status_code}")
        
        except Exception as e:
            print(f"❌ Recent requests analysis failed: {e}")

async def main():
    """Run the real quiz latency test"""
    
    tester = RealQuizLatencyTester()
    await tester.test_complete_quiz_flow()
    
    print("=" * 80)
    print("✅ REAL QUIZ LATENCY TEST COMPLETED")
    print()
    print("📋 Test Summary:")
    print("   🎯 Tested complete quiz flow with production prompts")
    print("   📊 Measured end-to-end latencies for all operations")
    print("   🧠 Included LLM calls with full context and tools")
    print("   🎵 Tracked TTS generation for Korean text")
    print("   🔄 Tested both correct and incorrect answer flows")
    print("   📈 Analyzed performance statistics and trends")
    print()
    print("🔗 Key Metrics Available:")
    print("   • Total request latency (user input → response)")
    print("   • LLM processing time (prompt → JSON response)")
    print("   • TTS generation time (text → audio)")
    print("   • Network operation latency (API calls)")
    print("   • Tool orchestration overhead")
    print()
    print("📊 Use /api/performance/* endpoints for detailed analysis")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
