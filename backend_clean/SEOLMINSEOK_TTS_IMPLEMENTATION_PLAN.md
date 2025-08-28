# 설민석 AI 튜터 전용 TTS 구현 계획

**날짜**: 2025-08-27  
**상태**: API 키 활성화 대기 중  
**목표**: 설민석 캐릭터 전용 TTS 서비스 구현

## 📋 현재 상황 요약

### ✅ 확인된 사항
1. **Actor ID 존재 확인**: `66f691e9b38df0481f09bf5e`가 시스템에 존재 (403 Forbidden 응답으로 확인)
2. **API 엔드포인트 확인**: `https://typecast.ai/api/text-to-speech` (Typecast Synchronous API)
3. **인증 방법 확인**: `Authorization: Bearer {API_KEY}` 헤더 사용
4. **페이로드 형식 확인**: Typecast 동기화 API 형식
5. **문서 검증**: https://docs.typecast.ai/guide/synchronous.html 형식 준수

### ❌ 대기 중인 사항
1. **API 키 활성화**: `__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG` (현재 401 unauthorized)
2. **권한 설정**: Actor `66f691e9b38df0481f09bf5e`에 대한 접근 권한 활성화

## 🎯 구현 계획

### 1단계: API 키 활성화 확인 (우선순위 HIGH)

API 키가 활성화되면 즉시 다음 테스트 실행:

```bash
python3 test_comprehensive_tts.py
```

예상 결과:
- ✅ HTTP 200 응답
- ✅ 오디오 파일 생성
- ✅ 설민석 음성 확인

### 2단계: 캐릭터 전용 TTS 서비스 구현

**파일 위치**: `backend_clean/services/character_specific_tts.py`

```python
class CharacterSpecificTTSService:
    def __init__(self):
        # 설민석 전용 설정
        self.seolminseok_config = {
            "api_key": "__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG",
            "actor_id": "66f691e9b38df0481f09bf5e",
            "endpoint": "https://typecast.ai/api/text-to-speech"
        }
    
    def generate_tts_for_character(self, text: str, character_id: str):
        if character_id == "seol_min_seok":
            return self._generate_seolminseok_tts(text)
        else:
            # 기존 TTS 서비스 사용
            return self._generate_default_tts(text, character_id)
```

### 3단계: 기존 TTS 서비스 통합

**수정 파일**: `backend_clean/services/tts_service.py`

기존 `generate_tts` 메서드에 캐릭터별 분기 로직 추가:

```python
def generate_tts(self, text: str, character_id: str = None, ...):
    # 설민석 캐릭터는 전용 TTS 사용
    if character_id == "seol_min_seok":
        return self.character_tts_service.generate_tts_for_character(text, character_id)
    
    # 기존 로직 유지
    return self._generate_default_tts(text, voice_id, ...)
```

### 4단계: API 엔드포인트 업데이트

**수정 파일**: `backend_clean/main.py`

기존 `/api/chat-with-session` 엔드포인트에서 캐릭터 ID 기반 TTS 분기:

```python
@app.post("/api/chat-with-session")
async def chat_with_session(request: ChatRequest):
    # ... 기존 로직 ...
    
    # 캐릭터별 TTS 처리
    if request.character_id == "seol_min_seok":
        audio_base64 = await character_tts_service.generate_tts_for_character(
            text=ai_response, 
            character_id=request.character_id
        )
    else:
        # 기존 TTS 로직
        audio_base64 = await tts_service.generate_tts(...)
```

## 🔧 상세 구현 사양

### TTS 요청 페이로드 (설민석 전용)

```json
{
    "text": "안녕하세요, 역사 여행 가이드 설민석입니다!",
    "lang": "auto",
    "actor_id": "66f691e9b38df0481f09bf5e",
    "xapi_hd": true,
    "model_version": "latest"
}
```

### 인증 헤더

```python
headers = {
    "Authorization": "Bearer __apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG",
    "Content-Type": "application/json"
}
```

### 에러 처리

1. **API 키 만료**: 기존 Duke 음성으로 폴백
2. **Actor 일시 불가**: 기존 Duke 음성으로 폴백
3. **네트워크 오류**: 재시도 3회 후 폴백
4. **응답 오류**: 로그 기록 후 폴백

### 환경 변수 설정

`.env` 파일에 추가:
```
SEOLMINSEOK_API_KEY=__apiH2kYR3VwmAvLWWi5WRoQJF7GvGmdayAoGnGM4JpG
SEOLMINSEOK_ACTOR_ID=66f691e9b38df0481f09bf5e
SEOLMINSEOK_ENDPOINT=https://typecast.ai/api/text-to-speech
```

## 🧪 테스트 계획

### 단계별 테스트

1. **API 키 활성화 테스트**:
   ```bash
   python3 test_comprehensive_tts.py
   ```

2. **캐릭터별 분기 테스트**:
   ```bash
   python3 test_character_specific_tts.py
   ```

3. **폴백 메커니즘 테스트**:
   ```bash
   python3 test_fallback_mechanism.py
   ```

4. **통합 테스트**:
   - 프론트엔드에서 설민석 캐릭터 선택
   - 실제 음성 생성 및 재생 확인
   - 다른 캐릭터와 음성 차이 확인

## 📊 성능 고려사항

### 예상 성능 지표
- **응답 시간**: Typecast Synchronous API ~2-5초
- **음질**: HD 모드로 고품질 오디오
- **캐시**: 동일 텍스트 재사용 시 캐시 활용 검토

### 모니터링
- API 응답 시간 로깅
- 성공/실패율 추적
- 폴백 발생 빈도 모니터링

## 🚀 배포 절차

### 1. API 키 활성화 확인 후
1. 테스트 스크립트로 동작 확인
2. 캐릭터 전용 TTS 서비스 구현
3. 기존 서비스와 통합
4. 통합 테스트 수행
5. 프로덕션 배포

### 2. 롤백 계획
- API 키 문제 발생 시 즉시 Duke 음성으로 복구
- 환경 변수로 설민석 전용 TTS on/off 제어

## 📝 문서 업데이트

배포 완료 후 다음 문서 업데이트:
- `README.md`: 설민석 전용 TTS 기능 추가
- `API_DOCUMENTATION.md`: 캐릭터별 TTS 엔드포인트 설명
- `DEPLOYMENT.md`: 환경 변수 설정 방법

## 🎯 예상 결과

API 키 활성화 완료 시:
- ✅ 설민석 캐릭터: 실제 설민석 음성 사용
- ✅ 다른 캐릭터: 기존 음성 계속 사용
- ✅ 완전한 폴백 메커니즘으로 안정성 보장
- ✅ 컨퍼런스 데모에서 실제 설민석 음성 시연 가능

---

**현재 상태**: API 키 활성화 대기 중  
**다음 액션**: API 제공업체에 키 활성화 요청 또는 활성화 상태 확인