from abc import ABC, abstractmethod
from typing import List, Dict
import json
from pydantic import ValidationError
from app.domain.state import PersonalWishesState
from app.domain.llm import LLMExtractionResult, LLMExtractionResponse

class LLMProvider(ABC):
    """
    Abstract base class for untrusted proposal generators.
    """
    
    @abstractmethod
    async def extract_state_changes(
        self, 
        conversation: List[Dict[str, str]], 
        current_state: PersonalWishesState
    ) -> LLMExtractionResult:
        """
        Extracts proposed changes from the conversation history.
        Must return an LLMExtractionResult, never mutating state directly.
        """
        pass

    def parse_raw_response(self, raw_text: str, prompt_version: str) -> LLMExtractionResult:
        """
        Strict parsing logic that all providers should use to validate raw LLM text
        against the Pydantic extraction schema.
        Handles missing fields, wrong types, and malformed JSON securely.
        """
        clean_text = raw_text.strip()
        
        # Robustly extract JSON block if the model included conversational padding
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            extracted_text = clean_text[start_idx:end_idx+1]
        else:
            extracted_text = clean_text
            
        try:
            data = json.loads(extracted_text)
            response = LLMExtractionResponse.model_validate(data)
            return LLMExtractionResult(
                success=True, 
                data=response, 
                prompt_version=prompt_version
            )
        except json.JSONDecodeError as e:
            return LLMExtractionResult(
                success=False, 
                error=f"Malformed JSON: {str(e)}", 
                prompt_version=prompt_version
            )
        except ValidationError as e:
            return LLMExtractionResult(
                success=False, 
                error=f"Schema Validation Error: {str(e)}", 
                prompt_version=prompt_version
            )
        except Exception as e:
            return LLMExtractionResult(
                success=False, 
                error=f"Unexpected parsing error: {str(e)}", 
                prompt_version=prompt_version
            )
