#!/usr/bin/env python3
"""
Simple Performance Logging Test

Test if the performance logging system is working correctly
"""

import asyncio
import requests
import time
import json
from datetime import datetime

async def test_performance_logging():
    """Test basic performance logging functionality"""
    
    print("🧪 PERFORMANCE LOGGING TEST")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    base_url = "http://localhost:8001"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code != 200:
            print("❌ Server not responding")
            return
        print("✅ Server is running")
    except:
        print("❌ Server is not running")
        return
    
    print()
    
    # Test simple API call
    print("📝 Testing simple API call with performance tracking...")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{base_url}/api/platform-chat",
            headers={"Content-Type": "application/json"},
            json={
                "user_input": "안녕하세요",
                "character_id": "seol_min_seok_quiz",
                "user_id": "test_user"
            },
            timeout=30
        )
        
        end_time = time.time()
        total_duration = (end_time - start_time) * 1000
        
        print(f"⏱️  API call completed in {total_duration:.1f}ms")
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📝 Response dialogue length: {len(data.get('dialogue', ''))}")
            print(f"🔧 Tools returned: {len(data.get('tools', []))}")
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return
    
    print()
    
    # Wait a moment for logging to process
    print("⏳ Waiting 2 seconds for performance logging...")
    await asyncio.sleep(2)
    
    # Check performance stats
    print("📊 Checking performance statistics...")
    
    try:
        stats_response = requests.get(f"{base_url}/api/performance/stats", timeout=10)
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"✅ Performance stats retrieved")
            print(f"📊 Status: {stats_data.get('status', 'unknown')}")
            
            if stats_data.get("status") == "success":
                perf_stats = stats_data.get("performance_stats", {})
                
                print()
                print("🎯 PERFORMANCE BREAKDOWN:")
                print(f"   📈 Total requests tracked: {perf_stats.get('total_requests_tracked', 0)}")
                print(f"   📋 Recent requests: {perf_stats.get('recent_requests_analyzed', 0)}")
                print(f"   🔄 Active requests: {perf_stats.get('active_requests', 0)}")
                print()
                print("⏱️  AVERAGE LATENCIES:")
                print(f"   🎯 Total duration: {perf_stats.get('avg_total_duration_ms', 0):.1f}ms")
                print(f"   🧠 LLM operations: {perf_stats.get('avg_llm_duration_ms', 0):.1f}ms")
                print(f"   🎵 TTS operations: {perf_stats.get('avg_tts_duration_ms', 0):.1f}ms")
                print(f"   🌐 Network operations: {perf_stats.get('avg_network_duration_ms', 0):.1f}ms")
                print()
                print("📊 OPERATION COUNTS:")
                print(f"   🧠 LLM calls: {perf_stats.get('llm_operations_count', 0)}")
                print(f"   🎵 TTS calls: {perf_stats.get('tts_operations_count', 0)}")
                print(f"   🌐 Network calls: {perf_stats.get('network_operations_count', 0)}")
                
                # Analysis
                print()
                print("🔍 ANALYSIS:")
                
                llm_avg = perf_stats.get('avg_llm_duration_ms', 0)
                tts_avg = perf_stats.get('avg_tts_duration_ms', 0)
                network_avg = perf_stats.get('avg_network_duration_ms', 0)
                total_avg = perf_stats.get('avg_total_duration_ms', 0)
                
                if llm_avg > 0:
                    print(f"   ✅ LLM tracking is working: {llm_avg:.1f}ms average")
                else:
                    print(f"   ❌ LLM tracking not capturing data")
                
                if tts_avg > 0:
                    print(f"   ✅ TTS tracking is working: {tts_avg:.1f}ms average")
                else:
                    print(f"   ❌ TTS tracking not capturing data")
                
                if network_avg > 0:
                    print(f"   ✅ Network tracking is working: {network_avg:.1f}ms average")
                else:
                    print(f"   ❌ Network tracking not capturing data")
                
                if total_avg > 0:
                    print(f"   ✅ Total request tracking is working: {total_avg:.1f}ms average")
                else:
                    print(f"   ❌ Total request tracking not capturing data")
                
            else:
                print("⚠️ Performance stats not available or empty")
                
        else:
            print(f"❌ Failed to get performance stats: HTTP {stats_response.status_code}")
            print(f"Response: {stats_response.text}")
            
    except Exception as e:
        print(f"❌ Error getting performance stats: {e}")
    
    print()
    
    # Check recent requests
    print("📋 Checking recent requests...")
    
    try:
        recent_response = requests.get(f"{base_url}/api/performance/recent-requests?limit=3", timeout=10)
        
        if recent_response.status_code == 200:
            recent_data = recent_response.json()
            
            if recent_data.get("status") == "success":
                requests_list = recent_data.get("recent_requests", [])
                print(f"✅ Found {len(requests_list)} recent requests")
                
                for i, req in enumerate(requests_list[:2], 1):  # Show top 2
                    print(f"   📋 Request {i}:")
                    print(f"      🆔 ID: {req.get('request_id', 'N/A')}")
                    print(f"      👤 Character: {req.get('character_id', 'N/A')}")
                    print(f"      ⏱️  Duration: {req.get('total_duration_ms', 0):.1f}ms")
                    print(f"      📊 Operations: {len(req.get('operations', []))}")
                    
                    # Show operation breakdown
                    operations = req.get('operations', [])
                    llm_ops = [op for op in operations if 'llm' in op.get('operation', '').lower()]
                    tts_ops = [op for op in operations if 'tts' in op.get('operation', '').lower()]
                    
                    if llm_ops:
                        llm_total = sum(op.get('duration_ms', 0) for op in llm_ops)
                        print(f"         🧠 LLM: {llm_total:.1f}ms ({len(llm_ops)} operations)")
                    
                    if tts_ops:
                        tts_total = sum(op.get('duration_ms', 0) for op in tts_ops)
                        print(f"         🎵 TTS: {tts_total:.1f}ms ({len(tts_ops)} operations)")
                    
            else:
                print("⚠️ No recent requests available")
                
        else:
            print(f"❌ Failed to get recent requests: HTTP {recent_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting recent requests: {e}")
    
    print()
    print("=" * 60)
    print("✅ PERFORMANCE LOGGING TEST COMPLETED")
    print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    print("   1. If LLM/TTS averages are 0, the tracking is not properly integrated")
    print("   2. Check that track_async_operation is used in LLM and TTS services")
    print("   3. Verify request_id is passed through the call chain")
    print("   4. Look for performance_logger.start_request/end_request calls")
    print("=" * 60)

async def main():
    """Run the performance logging test"""
    await test_performance_logging()

if __name__ == "__main__":
    asyncio.run(main())

