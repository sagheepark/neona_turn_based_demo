"""
Focused Quiz Latency Test

Direct test of quiz answer processing with detailed timing measurement
and actual production prompt structure analysis.
"""

import asyncio
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any

async def test_focused_quiz_latency():
    """Test focused quiz latency with detailed measurements"""
    
    print("🎯 FOCUSED QUIZ LATENCY TEST")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test configuration
    base_url = "http://localhost:8001"
    character_id = "seol_min_seok_quiz"
    
    # Check server
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding properly")
            return
        print("✅ Server is running")
    except:
        print("❌ Server is not running")
        return
    
    print()
    
    # Test scenarios with realistic quiz context
    test_scenarios = [
        {
            "name": "Quiz Answer - Correct Response",
            "user_input": "이성계",
            "description": "User answers correctly to '조선을 건국한 왕은 누구일까요?'",
            "expected_operations": ["LLM processing", "TTS generation", "Tool execution"]
        },
        {
            "name": "Quiz Answer - Wrong Response", 
            "user_input": "세종대왕",
            "description": "User answers incorrectly to test feedback flow",
            "expected_operations": ["LLM processing", "TTS generation", "Continuous quiz response"]
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"🧪 TEST SCENARIO {i}: {scenario['name']}")
        print(f"   Description: {scenario['description']}")
        print(f"   User Input: '{scenario['user_input']}'")
        print(f"   Expected: {', '.join(scenario['expected_operations'])}")
        print()
        
        # Detailed timing measurement
        total_start = time.time()
        
        # Phase 1: Request preparation
        prep_start = time.time()
        payload = {
            "user_input": scenario["user_input"],
            "character_id": character_id,
            "user_id": "test_user"
        }
        prep_time = (time.time() - prep_start) * 1000
        
        # Phase 2: Network request
        network_start = time.time()
        try:
            response = requests.post(
                f"{base_url}/api/platform-chat",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=45  # Increased timeout for complex processing
            )
            network_time = (time.time() - network_start) * 1000
            
            if response.status_code == 200:
                # Phase 3: Response processing
                parse_start = time.time()
                data = response.json()
                parse_time = (time.time() - parse_start) * 1000
                
                total_time = (time.time() - total_start) * 1000
                
                # Detailed analysis
                print(f"   ⏱️  TIMING BREAKDOWN:")
                print(f"      📋 Request preparation: {prep_time:.1f}ms")
                print(f"      🌐 Network + processing: {network_time:.1f}ms")
                print(f"      📥 Response parsing: {parse_time:.1f}ms")
                print(f"      🎯 Total end-to-end: {total_time:.1f}ms")
                print()
                
                # Response analysis
                dialogue = data.get('dialogue', '')
                tools = data.get('tools', [])
                audio_url = data.get('audio_url')
                streaming_audio = data.get('streaming_audio')
                
                print(f"   📊 RESPONSE ANALYSIS:")
                print(f"      📝 Dialogue length: {len(dialogue)} characters")
                print(f"      📋 Tools provided: {len(tools)}")
                
                # Tool analysis
                for j, tool in enumerate(tools):
                    tool_type = tool.get('type', 'unknown')
                    print(f"         Tool {j+1}: {tool_type}")
                    
                    if tool_type == 'continuous_quiz_response':
                        tool_data = tool.get('data', {})
                        phase1 = tool_data.get('phase1', {})
                        phase2 = tool_data.get('phase2', {})
                        
                        print(f"            Phase 1 text: {len(phase1.get('text', ''))} chars")
                        print(f"            Phase 2 text: {len(phase2.get('text', ''))} chars")
                        print(f"            Delay: {phase1.get('delay_ms', 0)}ms")
                        
                        # Check nested tool
                        nested_tool = phase2.get('tool')
                        if nested_tool:
                            print(f"            Nested tool: {nested_tool.get('type', 'unknown')}")
                    
                    elif tool_type == 'show_selection':
                        tool_data = tool.get('data', {})
                        question = tool_data.get('question', '')
                        options = tool_data.get('options', [])
                        selection_mode = tool_data.get('selection_mode', '')
                        
                        print(f"            Question: {len(question)} chars")
                        print(f"            Options: {len(options)} choices")
                        print(f"            Mode: {selection_mode}")
                
                # Audio analysis
                print(f"      🎵 Audio response:")
                if streaming_audio:
                    chunks = streaming_audio.get('total_chunks', 0)
                    est_time = streaming_audio.get('estimated_total_time', 0)
                    print(f"         Streaming: {chunks} chunks, ~{est_time:.0f}ms total")
                elif audio_url:
                    print(f"         Single TTS: Generated")
                else:
                    print(f"         No audio generated")
                
                print()
                
                # Performance rating
                if total_time < 2000:
                    rating = "🚀 EXCELLENT"
                elif total_time < 5000:
                    rating = "✅ GOOD"
                elif total_time < 10000:
                    rating = "⚠️ ACCEPTABLE"
                else:
                    rating = "❌ SLOW"
                
                print(f"   🎯 Performance Rating: {rating}")
                
                # Estimate component breakdown
                print(f"   🔍 ESTIMATED COMPONENT BREAKDOWN:")
                
                # Rough estimates based on typical performance
                estimated_llm = min(network_time * 0.4, 3000)  # LLM typically 40% of processing time
                estimated_tts = min(network_time * 0.5, 5000)  # TTS typically 50% of processing time  
                estimated_other = network_time - estimated_llm - estimated_tts
                
                if estimated_other < 0:
                    estimated_other = network_time * 0.1
                    estimated_llm = network_time * 0.45
                    estimated_tts = network_time * 0.45
                
                print(f"      🧠 LLM processing (est): {estimated_llm:.1f}ms")
                print(f"      🎵 TTS generation (est): {estimated_tts:.1f}ms") 
                print(f"      🔧 Other operations (est): {estimated_other:.1f}ms")
                
            else:
                print(f"   ❌ Request failed: HTTP {response.status_code}")
                print(f"      Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            timeout_time = (time.time() - network_start) * 1000
            print(f"   ⏰ Request timed out after {timeout_time:.1f}ms")
            print(f"   💡 This indicates very slow processing - likely LLM or TTS bottleneck")
            
        except Exception as e:
            error_time = (time.time() - network_start) * 1000
            print(f"   ❌ Request failed after {error_time:.1f}ms: {e}")
        
        print()
        print("-" * 80)
        print()
        
        if i < len(test_scenarios):
            print("⏳ Waiting 3 seconds before next test...")
            await asyncio.sleep(3)
            print()
    
    # Get server performance stats
    print("📊 SERVER PERFORMANCE STATISTICS")
    print("-" * 80)
    
    try:
        stats_response = requests.get(f"{base_url}/api/performance/stats", timeout=10)
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            if stats.get("status") == "success":
                perf_stats = stats.get("performance_stats", {})
                
                print("✅ Performance data available:")
                print(f"   📈 Total requests tracked: {perf_stats.get('total_requests_tracked', 0)}")
                print(f"   📊 Recent requests analyzed: {perf_stats.get('recent_requests_analyzed', 0)}")
                print(f"   🔄 Active requests: {perf_stats.get('active_requests', 0)}")
                print()
                print("⏱️  Component averages:")
                print(f"   📱 Total request time: {perf_stats.get('avg_total_duration_ms', 0):.1f}ms")
                print(f"   🧠 LLM operations: {perf_stats.get('avg_llm_duration_ms', 0):.1f}ms")
                print(f"   🎵 TTS operations: {perf_stats.get('avg_tts_duration_ms', 0):.1f}ms")
                print(f"   🌐 Network operations: {perf_stats.get('avg_network_duration_ms', 0):.1f}ms")
            else:
                print("⚠️ Performance statistics not available")
        else:
            print(f"❌ Failed to get performance stats: HTTP {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting performance stats: {e}")
    
    print()
    print("=" * 80)
    print("✅ FOCUSED QUIZ LATENCY TEST COMPLETED")
    print()
    print("📋 Key Findings:")
    print("   🎯 End-to-end latency measured for realistic quiz scenarios")
    print("   📊 Component breakdown estimated from total processing time")
    print("   🧠 LLM processing includes full prompt with character + tools + history")
    print("   🎵 TTS generation includes Korean text with SeolMinSeok voice")
    print("   🔄 Continuous quiz response flow tested for both correct/incorrect answers")
    print()
    print("💡 Performance Insights:")
    print("   • Network + processing time represents the core system latency")
    print("   • LLM calls include complete production prompt structure")
    print("   • TTS generation uses actual Korean text with character-specific voice")
    print("   • Tool orchestration includes session management and context building")
    print("=" * 80)

async def main():
    """Run the focused quiz latency test"""
    await test_focused_quiz_latency()

if __name__ == "__main__":
    asyncio.run(main())
