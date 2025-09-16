"""
TTS Latency Unit Test for SeolMinSeok TTS Service

Tests TTS generation latency with specific Korean history texts
to measure performance improvements from caching optimizations.
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime

async def test_seol_tts_latency():
    """
    Comprehensive TTS latency testing with SeolMinSeok service
    Tests multiple runs to get reliable performance data
    """
    
    # Import the TTS service
    try:
        from services.seolminseok_tts_service import SeolMinSeokTTSService
        print("✅ SeolMinSeok TTS service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import SeolMinSeok TTS service: {e}")
        return
    
    # Test texts provided by user
    test_texts = {
        "text_1_question": "고구려의 수도였던 국내성은 지금의 어느 지역에 위치해 있었을까요?",
        "text_2_intro_question": "아주 흥미로운 선택이에요! 고구려는 삼국 중에서도 특히 강력하고 독립적인 국가였죠. 그럼 고구려 역사와 인물에 관한 문제를 시작해볼까요? 고구려를 건국한 왕은 누구일까요?"
    }
    
    # Initialize TTS service
    tts_service = SeolMinSeokTTSService()
    
    # Test configuration
    num_runs = 5  # Multiple runs for statistical accuracy
    results = {
        "text_1_question": [],
        "text_2_intro_question": [],
        "service_initialization": 0
    }
    
    print(f"🧪 Starting TTS Latency Test")
    print(f"   Test runs per text: {num_runs}")
    print(f"   TTS Service: SeolMinSeok (dev.icepeak.ai)")
    print(f"   Character: seol_min_seok_quiz")
    print("=" * 80)
    
    # Test each text multiple times
    for text_key, text_content in test_texts.items():
        print(f"\n📝 Testing: {text_key}")
        print(f"   Text: {text_content[:50]}...")
        print(f"   Length: {len(text_content)} characters")
        
        latencies = []
        
        for run in range(num_runs):
            try:
                # Measure TTS generation latency
                start_time = time.time()
                
                audio_result = await tts_service.generate_speech(
                    text=text_content,
                    character_id="seol_min_seok_quiz",
                    use_hd=True,
                    language="auto",
                    timeout_seconds=10.0  # Generous timeout for testing
                )
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                
                # Validate result
                success = bool(audio_result and len(str(audio_result)) > 100)
                
                latencies.append(latency_ms)
                
                print(f"   Run {run + 1}: {latency_ms:.1f}ms {'✅' if success else '❌'}")
                
                # Small delay between runs to avoid rate limiting
                if run < num_runs - 1:
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                print(f"   Run {run + 1}: ERROR - {e}")
                # Don't include failed runs in statistics
        
        results[text_key] = latencies
    
    # Calculate and display statistics
    print("\n" + "=" * 80)
    print("📊 TTS LATENCY ANALYSIS RESULTS")
    print("=" * 80)
    
    overall_latencies = []
    
    for text_key, latencies in results.items():
        if text_key == "service_initialization" or not latencies:
            continue
            
        # Calculate statistics
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        median_latency = statistics.median(latencies)
        std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0
        
        overall_latencies.extend(latencies)
        
        print(f"\n🎯 {text_key.upper()}:")
        print(f"   Character count: {len(test_texts[text_key])}")
        print(f"   Successful runs: {len(latencies)}/{num_runs}")
        print(f"   Average latency: {avg_latency:.1f}ms")
        print(f"   Median latency:  {median_latency:.1f}ms")
        print(f"   Min latency:     {min_latency:.1f}ms")
        print(f"   Max latency:     {max_latency:.1f}ms")
        print(f"   Std deviation:   {std_dev:.1f}ms")
        print(f"   Latency range:   {max_latency - min_latency:.1f}ms")
        
        # Performance rating
        if avg_latency < 1000:
            rating = "🚀 EXCELLENT"
        elif avg_latency < 2000:
            rating = "✅ GOOD"
        elif avg_latency < 3000:
            rating = "⚠️ ACCEPTABLE"
        else:
            rating = "❌ SLOW"
        
        print(f"   Performance:     {rating}")
    
    # Overall statistics
    if overall_latencies:
        overall_avg = statistics.mean(overall_latencies)
        overall_median = statistics.median(overall_latencies)
        overall_min = min(overall_latencies)
        overall_max = max(overall_latencies)
        
        print(f"\n🌟 OVERALL TTS PERFORMANCE:")
        print(f"   Total tests run: {len(overall_latencies)}")
        print(f"   Average latency: {overall_avg:.1f}ms")
        print(f"   Median latency:  {overall_median:.1f}ms")
        print(f"   Best case:       {overall_min:.1f}ms")
        print(f"   Worst case:      {overall_max:.1f}ms")
        print(f"   Consistency:     {overall_max - overall_min:.1f}ms range")
        
        # Throughput calculation
        total_chars = sum(len(test_texts[key]) for key in test_texts.keys())
        chars_per_second = (total_chars * len(overall_latencies)) / (sum(overall_latencies) / 1000)
        
        print(f"\n⚡ THROUGHPUT ANALYSIS:")
        print(f"   Characters/second: {chars_per_second:.1f}")
        print(f"   Estimated time for 100-char text: {(100 / chars_per_second) * 1000:.1f}ms")
        
        # Performance recommendations
        print(f"\n💡 PERFORMANCE INSIGHTS:")
        if overall_avg < 1500:
            print("   🎯 TTS performance is excellent for real-time chat")
            print("   🚀 Users will experience responsive audio feedback")
        elif overall_avg < 2500:
            print("   ✅ TTS performance is good for educational content")
            print("   💡 Consider caching for frequently used phrases")
        else:
            print("   ⚠️ TTS latency may impact user experience")
            print("   🔧 Recommend implementing response caching")
        
        # Compare with target latencies
        print(f"\n🎯 TARGET COMPARISON:")
        print(f"   Target for quiz feedback: <1500ms")
        print(f"   Current average: {overall_avg:.1f}ms")
        if overall_avg < 1500:
            print("   ✅ Meeting performance targets")
        else:
            print(f"   ⚠️ {overall_avg - 1500:.1f}ms over target")
    
    print("\n" + "=" * 80)
    print("✅ TTS LATENCY TEST COMPLETED")
    print("=" * 80)
    
    return {
        "test_results": results,
        "overall_stats": {
            "average_latency": overall_avg if overall_latencies else 0,
            "median_latency": overall_median if overall_latencies else 0,
            "min_latency": overall_min if overall_latencies else 0,
            "max_latency": overall_max if overall_latencies else 0,
            "total_tests": len(overall_latencies),
            "chars_per_second": chars_per_second if overall_latencies else 0
        },
        "test_config": {
            "num_runs": num_runs,
            "service": "SeolMinSeokTTSService",
            "endpoint": "dev.icepeak.ai",
            "character_id": "seol_min_seok_quiz"
        }
    }

async def main():
    """Run the TTS latency test"""
    print("🚀 SeolMinSeok TTS Latency Unit Test")
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Purpose: Measure TTS generation performance for Korean history quiz texts")
    print()
    
    try:
        results = await test_seol_tts_latency()
        
        # Save results to file for analysis
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_latency_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
