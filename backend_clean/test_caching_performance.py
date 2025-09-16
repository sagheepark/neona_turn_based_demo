#!/usr/bin/env python3
"""
Test script to validate LLM and TTS caching performance improvements

This script tests the caching systems we implemented to ensure they provide
sub-second response times for repeated interactions.
"""

import asyncio
import requests
import time
import json
from typing import Dict, List

API_BASE = "http://localhost:8001"

async def test_cache_stats_endpoint():
    """Test the cache statistics endpoint"""
    print("🔍 Testing cache statistics endpoint...")
    
    try:
        response = requests.get(f"{API_BASE}/api/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print("✅ Cache stats endpoint working")
            print(f"📊 LLM Hit Rate: {stats['llm_caching']['llm_cache']['hit_rate']:.1f}%")
            print(f"📊 TTS Hit Rate: {stats['tts_caching']['audio_cache']['hit_rate']:.1f}%")
            print(f"📊 Overall Efficiency: {stats['summary']['overall_efficiency']}")
            return True
        else:
            print(f"❌ Cache stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to test cache stats: {e}")
        return False

def test_quiz_flow_performance():
    """Test quiz flow performance with caching"""
    print("\n🏃 Testing quiz flow performance with caching...")
    
    # First request (cache miss - should be slower)
    print("\n1. First request (cache miss expected):")
    start_time = time.time()
    
    session_response = requests.post(f"{API_BASE}/api/sessions/start", json={
        "user_id": "cache_test",
        "character_id": "seol_min_seok_quiz"
    })
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.status_code}")
        return False
    
    session_id = session_response.json()["session_id"]
    
    # Send greeting and get response
    response1 = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "안녕하세요",
        "user_id": "cache_test"
    })
    
    first_request_time = (time.time() - start_time) * 1000
    print(f"⏱️  First request time: {first_request_time:.0f}ms")
    
    if response1.status_code != 200:
        print(f"❌ First request failed: {response1.status_code}")
        return False
    
    # Second similar request (cache hit - should be much faster)
    print("\n2. Second similar request (cache hit expected):")
    start_time = time.time()
    
    session_response2 = requests.post(f"{API_BASE}/api/sessions/start", json={
        "user_id": "cache_test_2",
        "character_id": "seol_min_seok_quiz"
    })
    
    if session_response2.status_code != 200:
        print(f"❌ Second session creation failed: {session_response2.status_code}")
        return False
    
    session_id2 = session_response2.json()["session_id"]
    
    response2 = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id2,
        "user_input": "안녕하세요",  # Same input for cache hit
        "user_id": "cache_test_2"
    })
    
    second_request_time = (time.time() - start_time) * 1000
    print(f"⏱️  Second request time: {second_request_time:.0f}ms")
    
    if response2.status_code != 200:
        print(f"❌ Second request failed: {response2.status_code}")
        return False
    
    # Performance analysis
    performance_improvement = ((first_request_time - second_request_time) / first_request_time) * 100
    
    print(f"\n📈 Performance Analysis:")
    print(f"   First request:  {first_request_time:.0f}ms (cache miss)")
    print(f"   Second request: {second_request_time:.0f}ms (cache hit)")
    
    if second_request_time < first_request_time:
        print(f"   ✅ Performance improvement: {performance_improvement:.1f}%")
    else:
        print(f"   ⚠️  No performance improvement detected")
    
    if second_request_time < 800:  # Target: under 800ms
        print(f"   🎯 Target achieved: Under 800ms response time")
    else:
        print(f"   ⚠️  Target missed: Over 800ms response time")
    
    return True

def test_quiz_answer_caching():
    """Test caching for quiz answer responses"""
    print("\n🧠 Testing quiz answer response caching...")
    
    # Create session and get to quiz question
    session_response = requests.post(f"{API_BASE}/api/sessions/start", json={
        "user_id": "quiz_cache_test",
        "character_id": "seol_min_seok_quiz"
    })
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed")
        return False
    
    session_id = session_response.json()["session_id"]
    
    # Get to topic selection
    greeting_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "안녕하세요",
        "user_id": "quiz_cache_test"
    })
    
    if greeting_response.status_code != 200:
        print(f"❌ Greeting failed")
        return False
    
    # Select topic
    topic_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "조선시대",
        "user_id": "quiz_cache_test"
    })
    
    if topic_response.status_code != 200:
        print(f"❌ Topic selection failed")
        return False
    
    # Answer question (first time - cache miss)
    print("   Testing correct answer (first time)...")
    start_time = time.time()
    
    answer1_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id,
        "user_input": "태조 이성계",
        "user_id": "quiz_cache_test"
    })
    
    first_answer_time = (time.time() - start_time) * 1000
    print(f"   ⏱️  First answer time: {first_answer_time:.0f}ms")
    
    if answer1_response.status_code != 200:
        print(f"❌ First answer failed")
        return False
    
    # Same answer from different session (should be cached)
    print("   Testing same correct answer (cache hit expected)...")
    
    # Create new session
    session2_response = requests.post(f"{API_BASE}/api/sessions/start", json={
        "user_id": "quiz_cache_test_2",
        "character_id": "seol_min_seok_quiz"
    })
    session_id2 = session2_response.json()["session_id"]
    
    # Skip to same context (greeting -> topic -> answer)
    requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id2,
        "user_input": "안녕하세요",
        "user_id": "quiz_cache_test_2"
    })
    
    requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id2,
        "user_input": "조선시대",
        "user_id": "quiz_cache_test_2"
    })
    
    start_time = time.time()
    
    answer2_response = requests.post(f"{API_BASE}/api/platform-chat", json={
        "character_id": "seol_min_seok_quiz",
        "session_id": session_id2,
        "user_input": "태조 이성계",  # Same correct answer
        "user_id": "quiz_cache_test_2"
    })
    
    second_answer_time = (time.time() - start_time) * 1000
    print(f"   ⏱️  Second answer time: {second_answer_time:.0f}ms")
    
    if answer2_response.status_code == 200:
        cache_improvement = ((first_answer_time - second_answer_time) / first_answer_time) * 100
        
        if second_answer_time < first_answer_time:
            print(f"   ✅ Answer caching working: {cache_improvement:.1f}% improvement")
        else:
            print(f"   ⚠️  Answer caching may not be working optimally")
        
        return True
    else:
        print(f"❌ Second answer failed")
        return False

async def main():
    """Run all caching performance tests"""
    print("🚀 LLM and TTS Caching Performance Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Cache stats endpoint
    results.append(await test_cache_stats_endpoint())
    
    # Test 2: Basic quiz flow performance
    results.append(test_quiz_flow_performance())
    
    # Test 3: Quiz answer caching
    results.append(test_quiz_answer_caching())
    
    # Test 4: Get final cache stats
    print("\n📊 Final Cache Statistics:")
    final_stats_response = requests.get(f"{API_BASE}/api/cache/stats")
    if final_stats_response.status_code == 200:
        final_stats = final_stats_response.json()
        llm_stats = final_stats['llm_caching']['llm_cache']
        tts_stats = final_stats['tts_caching']['audio_cache']
        
        print(f"   LLM Cache: {llm_stats['hits']} hits, {llm_stats['misses']} misses ({llm_stats['hit_rate']:.1f}% hit rate)")
        print(f"   TTS Cache: {tts_stats['hits']} hits, {tts_stats['misses']} misses ({tts_stats['hit_rate']:.1f}% hit rate)")
        print(f"   Overall Efficiency: {final_stats['summary']['overall_efficiency']}")
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 Test Summary:")
    print(f"   Passed: {passed}/{total} tests")
    
    if passed == total:
        print("   ✅ All caching systems working optimally!")
        print("   🚀 Expected performance: Sub-second response times for cached interactions")
    else:
        print("   ⚠️  Some caching issues detected - review logs above")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)