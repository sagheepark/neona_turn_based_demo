"""
TTS Chunking System Demo & Test

Demonstrates the intelligent text chunking algorithm and streaming TTS architecture
with real Korean text examples from the quiz system.
"""

import asyncio
import time
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class TextChunk:
    """Represents a chunk of text for TTS generation"""
    text: str
    chunk_id: int
    is_sentence_end: bool
    estimated_latency: float = 0
    audio_url: Optional[str] = None
    generation_status: str = "pending"  # pending, generating, ready, playing, completed
    
    def __post_init__(self):
        # Calculate estimated latency using performance formula from test results
        self.estimated_latency = 571 + (43.4 * len(self.text))

class IntelligentTextChunker:
    """Korean-aware text chunking for optimal TTS performance"""
    
    MAX_CHUNK_SIZE = 50  # characters - optimal performance threshold
    MIN_CHUNK_SIZE = 15  # characters - avoid too many small chunks
    
    # Korean sentence boundary markers
    SENTENCE_ENDINGS = ['다.', '요.', '까요?', '나요?', '죠.', '요!', '다!', '습니다.', '어요.', '네요.']
    
    # Korean clause boundary markers  
    CLAUSE_MARKERS = [', ', '! ', '. ', '? ', ' 그럼 ', ' 자, ', ' 이제 ', ' 그리고 ', ' 하지만 ', ' 또한 ']
    
    # Protected phrases that shouldn't be broken
    PROTECTED_PHRASES = [
        '고구려', '조선시대', '세종대왕', '이성계', '박정희', '삼국시대', 
        '한국사', '역사', '건국', '대한민국', '닥터 지니', '설민석'
    ]
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        """
        Intelligently chunk Korean text for optimal TTS performance
        while preserving semantic meaning and readability.
        """
        if len(text) <= self.MAX_CHUNK_SIZE:
            # No chunking needed for short text
            return [TextChunk(
                text=text.strip(),
                chunk_id=0,
                is_sentence_end=True
            )]
        
        chunks = []
        
        # Step 1: Split by sentences first
        sentences = self._split_by_sentences(text)
        
        current_chunk = ""
        
        for sentence in sentences:
            # If sentence alone exceeds max size, split by clauses
            if len(sentence) > self.MAX_CHUNK_SIZE:
                clause_chunks = self._split_by_clauses(sentence)
                
                for clause in clause_chunks:
                    # If clause still too long, force split preserving phrases
                    if len(clause) > self.MAX_CHUNK_SIZE:
                        phrase_chunks = self._force_split_preserving_phrases(clause)
                        for phrase_chunk in phrase_chunks:
                            chunks.append(TextChunk(
                                text=phrase_chunk.strip(),
                                chunk_id=len(chunks),
                                is_sentence_end=phrase_chunk.endswith(tuple(self.SENTENCE_ENDINGS))
                            ))
                    else:
                        chunks.append(TextChunk(
                            text=clause.strip(),
                            chunk_id=len(chunks),
                            is_sentence_end=clause.endswith(tuple(self.SENTENCE_ENDINGS))
                        ))
            else:
                # Try to combine with current chunk if under limit
                if len(current_chunk + " " + sentence) <= self.MAX_CHUNK_SIZE:
                    current_chunk = (current_chunk + " " + sentence).strip()
                else:
                    # Finalize current chunk and start new one
                    if current_chunk:
                        chunks.append(TextChunk(
                            text=current_chunk.strip(),
                            chunk_id=len(chunks),
                            is_sentence_end=True
                        ))
                    current_chunk = sentence
        
        # Add final chunk
        if current_chunk:
            chunks.append(TextChunk(
                text=current_chunk.strip(),
                chunk_id=len(chunks),
                is_sentence_end=True
            ))
        
        return self._optimize_chunks(chunks)
    
    def _split_by_sentences(self, text: str) -> List[str]:
        """Split text by Korean sentence endings"""
        sentences = []
        current = ""
        
        i = 0
        while i < len(text):
            current += text[i]
            
            # Check for sentence endings
            for ending in self.SENTENCE_ENDINGS:
                if current.endswith(ending):
                    sentences.append(current.strip())
                    current = ""
                    break
            
            i += 1
        
        # Add remaining text
        if current.strip():
            sentences.append(current.strip())
        
        return [s for s in sentences if s]
    
    def _split_by_clauses(self, sentence: str) -> List[str]:
        """Split sentence by clause markers"""
        clauses = [sentence]
        
        for marker in self.CLAUSE_MARKERS:
            new_clauses = []
            for clause in clauses:
                if marker in clause:
                    parts = clause.split(marker)
                    for i, part in enumerate(parts):
                        if i < len(parts) - 1:
                            new_clauses.append((part + marker).strip())
                        else:
                            new_clauses.append(part.strip())
                else:
                    new_clauses.append(clause)
            clauses = [c for c in new_clauses if c]
        
        return clauses
    
    def _force_split_preserving_phrases(self, text: str) -> List[str]:
        """Force split long text while preserving important phrases"""
        chunks = []
        current = ""
        
        words = text.split()
        
        for word in words:
            # Check if adding this word would exceed limit
            test_chunk = (current + " " + word).strip()
            
            if len(test_chunk) > self.MAX_CHUNK_SIZE and current:
                # Check if current chunk is too small
                if len(current) < self.MIN_CHUNK_SIZE and chunks:
                    # Merge with previous chunk if possible
                    prev_chunk = chunks[-1]
                    if len(prev_chunk + " " + current) <= self.MAX_CHUNK_SIZE:
                        chunks[-1] = (prev_chunk + " " + current).strip()
                    else:
                        chunks.append(current.strip())
                else:
                    chunks.append(current.strip())
                
                current = word
            else:
                current = test_chunk
        
        # Add final chunk
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def _optimize_chunks(self, chunks: List[TextChunk]) -> List[TextChunk]:
        """Optimize chunk sizes and boundaries"""
        if len(chunks) <= 1:
            return chunks
        
        optimized = []
        i = 0
        
        while i < len(chunks):
            current_chunk = chunks[i]
            
            # If current chunk is too small, try to merge with next
            if (len(current_chunk.text) < self.MIN_CHUNK_SIZE and 
                i + 1 < len(chunks)):
                
                next_chunk = chunks[i + 1]
                combined_text = current_chunk.text + " " + next_chunk.text
                
                if len(combined_text) <= self.MAX_CHUNK_SIZE:
                    # Merge chunks
                    merged_chunk = TextChunk(
                        text=combined_text.strip(),
                        chunk_id=len(optimized),
                        is_sentence_end=next_chunk.is_sentence_end
                    )
                    optimized.append(merged_chunk)
                    i += 2  # Skip next chunk as it's merged
                else:
                    optimized.append(TextChunk(
                        text=current_chunk.text,
                        chunk_id=len(optimized),
                        is_sentence_end=current_chunk.is_sentence_end
                    ))
                    i += 1
            else:
                optimized.append(TextChunk(
                    text=current_chunk.text,
                    chunk_id=len(optimized),
                    is_sentence_end=current_chunk.is_sentence_end
                ))
                i += 1
        
        return optimized

class StreamingTTSDemo:
    """Demo class to show streaming TTS in action"""
    
    def __init__(self):
        self.chunker = IntelligentTextChunker()
        
    async def demonstrate_chunking(self, test_texts: Dict[str, str]):
        """Demonstrate chunking with various Korean texts"""
        
        print("🧪 TTS CHUNKING DEMONSTRATION")
        print("=" * 80)
        
        for test_name, text in test_texts.items():
            print(f"\n📝 TEST: {test_name.upper()}")
            print(f"   Original text: {text}")
            print(f"   Length: {len(text)} characters")
            
            # Perform chunking
            start_time = time.time()
            chunks = self.chunker.chunk_text(text)
            chunking_time = (time.time() - start_time) * 1000
            
            print(f"   Chunking time: {chunking_time:.2f}ms")
            print(f"   Number of chunks: {len(chunks)}")
            
            # Analyze chunks
            total_estimated_time = 0
            
            for i, chunk in enumerate(chunks):
                print(f"   📦 Chunk {i + 1}: \"{chunk.text}\"")
                print(f"       Length: {len(chunk.text)} chars")
                print(f"       Estimated TTS: {chunk.estimated_latency:.0f}ms")
                print(f"       Sentence end: {chunk.is_sentence_end}")
                
                total_estimated_time += chunk.estimated_latency
            
            # Calculate performance improvement
            single_tts_time = 571 + (43.4 * len(text))
            first_chunk_time = chunks[0].estimated_latency if chunks else 0
            
            print(f"\n   📊 PERFORMANCE ANALYSIS:")
            print(f"       Single TTS time: {single_tts_time:.0f}ms")
            print(f"       First chunk ready: {first_chunk_time:.0f}ms")
            print(f"       Time to first audio: {single_tts_time - first_chunk_time:.0f}ms faster")
            print(f"       Improvement: {((single_tts_time - first_chunk_time) / single_tts_time * 100):.1f}%")
            
            # Verify text integrity
            reconstructed = " ".join(chunk.text for chunk in chunks)
            original_normalized = re.sub(r'\s+', ' ', text.strip())
            reconstructed_normalized = re.sub(r'\s+', ' ', reconstructed.strip())
            
            integrity_check = original_normalized == reconstructed_normalized
            print(f"       Text integrity: {'✅ PRESERVED' if integrity_check else '❌ CORRUPTED'}")
            
            if not integrity_check:
                print(f"       Original: {original_normalized}")
                print(f"       Reconstructed: {reconstructed_normalized}")
            
            print("-" * 60)
    
    async def simulate_streaming_playback(self, text: str):
        """Simulate how streaming playback would work"""
        
        print(f"\n🎵 STREAMING PLAYBACK SIMULATION")
        print(f"Text: {text}")
        print("=" * 80)
        
        chunks = self.chunker.chunk_text(text)
        
        print("📺 Frontend: Displaying full text immediately...")
        print(f"   \"{text}\"")
        print()
        
        print("🔄 Backend: Starting parallel TTS generation...")
        
        # Simulate parallel generation
        generation_tasks = []
        for chunk in chunks:
            print(f"   🚀 Starting generation for chunk {chunk.chunk_id + 1}: \"{chunk.text}\"")
            generation_tasks.append(self._simulate_chunk_generation(chunk))
        
        print()
        print("🎧 Frontend: Monitoring for ready chunks and playing in order...")
        
        # Simulate ordered playback
        completed_chunks = await asyncio.gather(*generation_tasks)
        
        total_playback_time = 0
        
        for chunk in completed_chunks:
            # Simulate waiting for chunk to be ready
            print(f"   ⏳ Waiting for chunk {chunk.chunk_id + 1}...")
            await asyncio.sleep(chunk.estimated_latency / 1000)  # Convert to seconds for demo
            
            print(f"   🎵 Playing chunk {chunk.chunk_id + 1}: \"{chunk.text}\"")
            
            # Simulate audio duration (roughly 3 chars per second for Korean)
            audio_duration = len(chunk.text) / 3
            total_playback_time += audio_duration
            
            await asyncio.sleep(0.5)  # Brief pause between chunks
        
        print(f"\n✅ Streaming complete!")
        print(f"   Total playback time: {total_playback_time:.1f}s")
        print(f"   First audio started at: {chunks[0].estimated_latency / 1000:.1f}s")
        print(f"   User waited: {chunks[0].estimated_latency / 1000:.1f}s vs {(571 + 43.4 * len(text)) / 1000:.1f}s")
        
    async def _simulate_chunk_generation(self, chunk: TextChunk) -> TextChunk:
        """Simulate TTS generation for a chunk"""
        chunk.generation_status = "generating"
        
        # Simulate generation time (use actual estimated latency)
        await asyncio.sleep(chunk.estimated_latency / 2000)  # Half speed for demo
        
        chunk.audio_url = f"data:audio/wav;base64,chunk_{chunk.chunk_id}_audio"
        chunk.generation_status = "ready"
        
        return chunk

async def main():
    """Run the TTS chunking demonstration"""
    
    # Test texts from the quiz system
    test_texts = {
        "short_feedback": "정답입니다!",
        "medium_feedback": "훌륭해요! 이성계가 맞습니다.",
        "quiz_question": "고구려의 수도였던 국내성은 지금의 어느 지역에 위치해 있었을까요?",
        "long_explanation": "아주 흥미로운 선택이에요! 고구려는 삼국 중에서도 특히 강력하고 독립적인 국가였죠. 그럼 고구려 역사와 인물에 관한 문제를 시작해볼까요? 고구려를 건국한 왕은 누구일까요?",
        "complex_content": "세종대왕은 조선 제4대 왕으로 1418년부터 1450년까지 재위하였습니다. 그는 한글 창제, 과학 기술 발달, 영토 확장 등 다양한 업적을 남겼습니다. 특히 훈민정음 창제는 우리나라 문화사에 획기적인 사건이었죠. 이제 세종대왕과 관련된 문제를 풀어보시겠어요?"
    }
    
    demo = StreamingTTSDemo()
    
    # Demonstrate chunking analysis
    await demo.demonstrate_chunking(test_texts)
    
    # Simulate streaming playback for the longest text
    longest_text = test_texts["complex_content"]
    await demo.simulate_streaming_playback(longest_text)
    
    print("\n" + "=" * 80)
    print("✅ TTS CHUNKING DEMO COMPLETED")
    print("📋 Next steps: Integrate with actual TTS services and frontend")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
