"""
TTS Performance Analysis - Detailed breakdown of latency patterns
"""

import asyncio
import time
import statistics
from datetime import datetime

async def test_tts_by_length():
    """Test TTS performance across different text lengths"""
    
    from services.seolminseok_tts_service import SeolMinSeokTTSService
    
    # Test texts of varying lengths
    test_cases = [
        {"name": "very_short", "text": "정답입니다!", "length": 6},
        {"name": "short", "text": "훌륭해요! 이성계가 맞습니다.", "length": 17},
        {"name": "medium", "text": "고구려의 수도였던 국내성은 지금의 어느 지역에 위치해 있었을까요?", "length": 36},
        {"name": "long", "text": "아주 흥미로운 선택이에요! 고구려는 삼국 중에서도 특히 강력하고 독립적인 국가였죠. 그럼 고구려 역사와 인물에 관한 문제를 시작해볼까요? 고구려를 건국한 왕은 누구일까요?", "length": 95}
    ]
    
    tts_service = SeolMinSeokTTSService()
    
    print("🔍 TTS PERFORMANCE BY TEXT LENGTH")
    print("=" * 60)
    
    results = {}
    
    for test_case in test_cases:
        name = test_case["name"]
        text = test_case["text"]
        length = test_case["length"]
        
        print(f"\n📝 Testing {name.upper()} text ({length} chars)")
        print(f"   Text: {text}")
        
        # Run 3 times for this analysis
        latencies = []
        
        for run in range(3):
            try:
                start_time = time.time()
                
                audio_result = await tts_service.generate_speech(
                    text=text,
                    character_id="seol_min_seok_quiz",
                    use_hd=True,
                    language="auto",
                    timeout_seconds=10.0
                )
                
                end_time = time.time()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)
                
                success = bool(audio_result and len(str(audio_result)) > 100)
                print(f"   Run {run + 1}: {latency_ms:.1f}ms {'✅' if success else '❌'}")
                
                await asyncio.sleep(0.3)  # Brief pause
                
            except Exception as e:
                print(f"   Run {run + 1}: ERROR - {e}")
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            
            # Calculate characters per millisecond
            chars_per_ms = length / avg_latency
            
            results[name] = {
                "length": length,
                "avg_latency": avg_latency,
                "min_latency": min_latency,
                "max_latency": max_latency,
                "chars_per_ms": chars_per_ms,
                "latencies": latencies
            }
            
            print(f"   📊 Average: {avg_latency:.1f}ms")
            print(f"   📊 Efficiency: {chars_per_ms:.4f} chars/ms")
    
    # Analysis
    print("\n" + "=" * 60)
    print("📈 PERFORMANCE ANALYSIS")
    print("=" * 60)
    
    print(f"\n{'Text Type':<12} {'Length':<8} {'Avg Latency':<12} {'Efficiency':<12} {'Rating'}")
    print("-" * 60)
    
    for name, data in results.items():
        length = data["length"]
        avg_latency = data["avg_latency"]
        efficiency = data["chars_per_ms"]
        
        # Rating based on latency
        if avg_latency < 1500:
            rating = "🚀 FAST"
        elif avg_latency < 2500:
            rating = "✅ GOOD"
        elif avg_latency < 4000:
            rating = "⚠️ SLOW"
        else:
            rating = "❌ VERY SLOW"
        
        print(f"{name:<12} {length:<8} {avg_latency:<12.1f} {efficiency:<12.4f} {rating}")
    
    # Look for patterns
    print(f"\n🔍 PATTERN ANALYSIS:")
    
    # Linear relationship analysis
    lengths = [data["length"] for data in results.values()]
    latencies = [data["avg_latency"] for data in results.values()]
    
    if len(lengths) >= 2:
        # Simple linear regression
        n = len(lengths)
        sum_x = sum(lengths)
        sum_y = sum(latencies)
        sum_xy = sum(x * y for x, y in zip(lengths, latencies))
        sum_x2 = sum(x * x for x in lengths)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n
        
        print(f"   📊 Base latency (intercept): {intercept:.1f}ms")
        print(f"   📊 Additional latency per character: {slope:.1f}ms")
        
        # Predict latency for common text lengths
        for pred_length in [10, 25, 50, 75, 100]:
            predicted = intercept + slope * pred_length
            print(f"   🎯 Predicted latency for {pred_length} chars: {predicted:.1f}ms")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    very_short_avg = results.get("very_short", {}).get("avg_latency", 0)
    long_avg = results.get("long", {}).get("avg_latency", 0)
    
    if very_short_avg > 1500:
        print("   ⚠️ Even short texts are slow - consider TTS service optimization")
    
    if long_avg > 4000:
        print("   🔧 Long texts are very slow - implement text chunking")
        print("   💡 Consider breaking long responses into multiple TTS calls")
    
    # Quiz-specific recommendations
    print(f"\n🎯 QUIZ PERFORMANCE RECOMMENDATIONS:")
    medium_avg = results.get("medium", {}).get("avg_latency", 0)
    
    if medium_avg < 2000:
        print("   ✅ Quiz questions will have acceptable response times")
    else:
        print("   ⚠️ Quiz questions may feel slow to users")
        print("   💡 Consider pre-generating TTS for common questions")
    
    return results

async def main():
    print("🚀 TTS Performance Analysis")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        results = await test_tts_by_length()
        
        # Save detailed results
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_performance_analysis_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Detailed results saved to: {filename}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
