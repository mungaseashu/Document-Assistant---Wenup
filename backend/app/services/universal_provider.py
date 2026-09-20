import litellm
from typing import List, Dict
from app.core.config import settings
from app.domain.state import PersonalWishesState
from app.domain.llm import LLMExtractionResult
from app.services.llm_provider import LLMProvider
from app.domain.llm import LLMExtractionResponse

PROMPT_VERSION_1 = "v1.0.0-universal-extraction"

class UniversalProvider(LLMProvider):
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL_NAME

    def _build_system_prompt(self, current_state: PersonalWishesState) -> str:
        return f"""You are a precise data extraction assistant for a Personal Wishes document.
Your task is to analyze the conversation and propose structured state updates.

CRITICAL INSTRUCTIONS:
- Extract ONLY information explicitly supplied by the user.
- NEVER invent facts or hallucinate details.
- HANDLE LISTS CORRECTLY: For list fields (like specific_gifts, additional_wishes, children_names), you MUST always output a JSON array `[]`. If the user says 'no' or 'none', output an empty list `[]`. If they provide items, output a list of strings (e.g., `["I want a car"]`). NEVER output a plain string, boolean, or null for a list field.
- ASSUME HIGH CONFIDENCE: If the user explicitly and clearly provides information, set status to CONFIRMED and confidence to 1.0.
- IDENTIFY uncertainty: ONLY if the user uses probabilistic language ("probably", "maybe"), lower confidence and use PROPOSED status.
- IDENTIFY corrections: If the user corrects previous information, use CORRECTED status.
- IMPLICIT CORRECTIONS: If the user provides an answer that contradicts a previous state (e.g., naming a 'son' when has_children is false), and says 'Actually...', you MUST explicitly extract the corrected base field (e.g., has_children: true, status: CORRECTED) alongside the new field.
- IDENTIFY contradictions: If the user contradicts known facts without a correction, output to potential_conflicts.
- RETURN STRUCTURED JSON ONLY matching the requested schema. DO NOT output conversational text.

REQUIRED JSON SCHEMA:
{LLMExtractionResponse.model_json_schema()}

Current Validated State:
{current_state.model_dump_json(exclude_none=True)}
"""

    async def extract_state_changes(
        self, 
        conversation: List[Dict[str, str]], 
        current_state: PersonalWishesState
    ) -> LLMExtractionResult:
        
        if not self.api_key:
            return LLMExtractionResult(
                success=False, 
                error="Missing LLM configuration (API Key).", 
                prompt_version=PROMPT_VERSION_1
            )
            
        messages = [{"role": "system", "content": self._build_system_prompt(current_state)}]
        messages.extend(conversation)
        
        try:
            # LiteLLM automatically maps the model_name prefix to the correct provider
            response = await litellm.acompletion(
                model=self.model_name,
                messages=messages,
                api_key=self.api_key,
                temperature=0.0
            )
            
            raw_text = response.choices[0].message.content
            return self.parse_raw_response(raw_text, prompt_version=PROMPT_VERSION_1)
            
        except Exception as e:
            return LLMExtractionResult(
                success=False, 
                error=f"LLM API Error: {str(e)}", 
                prompt_version=PROMPT_VERSION_1
            )
