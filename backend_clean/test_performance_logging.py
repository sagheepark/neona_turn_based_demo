"""
Performance Logging Test & Demo

Tests the comprehensive performance logging system with real API calls
to show latency tracking for LLM, TTS, and network operations.
"""

import asyncio
import json
import time
from datetime import datetime
import requests

async def test_performance_logging():
    """Test the performance logging system with actual API calls"""
    
    print("🧪 PERFORMANCE LOGGING TEST")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test 1: Check if server is running
    try:
        response = requests.get("http://localhost:8001/api/models")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server not responding properly")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the server first:")
        print("   cd backend_clean && python3 main.py")
        return
    
    print()
    print("🚀 Starting performance logging tests...")
    print()
    
    # Test 2: Simple chat interaction
    test_cases = [
        {
            "name": "Short Greeting",
            "user_input": "",
            "character_id": "seol_min_seok_quiz",
            "expected_operations": ["llm_api_call", "tts_generation"]
        },
        {
            "name": "Topic Selection", 
            "user_input": "조선시대",
            "character_id": "seol_min_seok_quiz",
            "expected_operations": ["llm_api_call", "tts_generation"]
        },
        {
            "name": "Quiz Answer",
            "user_input": "이성계",
            "character_id": "seol_min_seok_quiz", 
            "expected_operations": ["llm_api_call", "tts_generation"]
        }
    ]
    
    request_ids = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"📝 Test {i}: {test_case['name']}")
        print(f"   Input: '{test_case['user_input']}'")
        print(f"   Character: {test_case['character_id']}")
        
        start_time = time.time()
        
        try:
            # Make API call
            response = requests.post(
                "http://localhost:8001/api/platform-chat",
                headers={"Content-Type": "application/json"},
                json={
                    "user_input": test_case["user_input"],
                    "character_id": test_case["character_id"],
                    "user_id": "test_user"
                },
                timeout=30
            )
            
            end_time = time.time()
            total_time = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success: {total_time:.1f}ms total")
                print(f"   Response: {data.get('dialogue', '')[:50]}...")
                
                # Extract any request ID from logs (would need to be returned in response)
                # For now, we'll check performance stats
                
            else:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                print(f"   Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
        
        # Wait between requests
        if i < len(test_cases):
            print("   ⏳ Waiting 2 seconds before next test...")
            await asyncio.sleep(2)
            print()
    
    # Test 3: Check performance statistics
    print("📊 CHECKING PERFORMANCE STATISTICS")
    print("-" * 60)
    
    try:
        # Get overall performance stats
        stats_response = requests.get("http://localhost:8001/api/performance/stats")
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            
            if stats["status"] == "success":
                perf_stats = stats["performance_stats"]
                
                print("✅ Performance Statistics Retrieved:")
                print(f"   📈 Total Requests Tracked: {perf_stats.get('total_requests_tracked', 0)}")
                print(f"   📊 Recent Requests Analyzed: {perf_stats.get('recent_requests_analyzed', 0)}")
                print(f"   🔄 Active Requests: {perf_stats.get('active_requests', 0)}")
                print()
                print("⏱️  Average Latencies:")
                print(f"   🧠 LLM Operations: {perf_stats.get('avg_llm_duration_ms', 0):.1f}ms")
                print(f"   🎵 TTS Operations: {perf_stats.get('avg_tts_duration_ms', 0):.1f}ms")
                print(f"   🌐 Network Operations: {perf_stats.get('avg_network_duration_ms', 0):.1f}ms")
                print(f"   📱 Total Request Time: {perf_stats.get('avg_total_duration_ms', 0):.1f}ms")
                print()
                print("📊 Operation Counts:")
                print(f"   🧠 LLM Calls: {perf_stats.get('llm_operations_count', 0)}")
                print(f"   🎵 TTS Generations: {perf_stats.get('tts_operations_count', 0)}")
                print(f"   🌐 Network Requests: {perf_stats.get('network_operations_count', 0)}")
                
            else:
                print("⚠️ Performance stats not available yet")
        else:
            print(f"❌ Failed to get performance stats: HTTP {stats_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting performance stats: {e}")
    
    print()
    
    # Test 4: Get recent requests details
    print("📋 CHECKING RECENT REQUESTS")
    print("-" * 60)
    
    try:
        recent_response = requests.get("http://localhost:8001/api/performance/recent-requests?limit=5")
        
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            
            if recent_data["status"] == "success":
                requests_data = recent_data["recent_requests"]
                
                print(f"✅ Found {len(requests_data)} recent requests:")
                print()
                
                for idx, req in enumerate(requests_data, 1):
                    print(f"🔍 Request {idx}:")
                    print(f"   ID: {req['request_id']}")
                    print(f"   Character: {req['character_id']}")
                    print(f"   Input: {req['user_input']}")
                    print(f"   Total Time: {req['total_duration_ms']:.1f}ms")
                    print(f"   Timestamp: {req['timestamp']}")
                    
                    # Show operation breakdown
                    print("   📊 Operation Breakdown:")
                    for op in req.get('breakdown', []):
                        status = "✅" if op['success'] else "❌"
                        print(f"      {status} {op['operation']}: {op['duration_ms']:.1f}ms")
                        if op.get('metadata'):
                            print(f"         Metadata: {json.dumps(op['metadata'], separators=(',', ':'))}")
                    
                    print()
            else:
                print("⚠️ No recent requests available")
        else:
            print(f"❌ Failed to get recent requests: HTTP {recent_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting recent requests: {e}")
    
    print()
    print("=" * 80)
    print("✅ PERFORMANCE LOGGING TEST COMPLETED")
    print()
    print("💡 Key Features Demonstrated:")
    print("   🎯 Request-level performance tracking")
    print("   ⏱️  Individual operation latency measurement")
    print("   📊 Comprehensive statistics and analytics")
    print("   🔍 Detailed request breakdowns")
    print("   🌐 Network operation tracking")
    print("   🧠 LLM API call performance")
    print("   🎵 TTS generation latency")
    print()
    print("🔗 Available Endpoints:")
    print("   GET /api/performance/stats - Overall performance statistics")
    print("   GET /api/performance/recent-requests - Recent request summaries")
    print("   GET /api/performance/request/{id} - Detailed request analysis")
    print()
    print("📈 Use these endpoints to monitor system performance in real-time!")
    print("=" * 80)

async def main():
    """Run the performance logging test"""
    await test_performance_logging()

if __name__ == "__main__":
    asyncio.run(main())
