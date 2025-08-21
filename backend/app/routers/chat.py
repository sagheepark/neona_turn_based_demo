from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.llm_service import LLMService
from app.services.prompt_service import PromptService

router = APIRouter()
llm_service = LLMService()
prompt_service = PromptService()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Generate prompt
        prompt = prompt_service.generate_prompt(
            character_prompt=request.character_prompt,
            conversation_history=request.history,
            user_input=request.message
        )
        
        # Call LLM
        response = await llm_service.generate_response(prompt)
        
        # Parse and validate response
        parsed_response = prompt_service.parse_response(response)
        
        return ChatResponse(**parsed_response)
        
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))