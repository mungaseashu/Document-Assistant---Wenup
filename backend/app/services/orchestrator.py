from pydantic import BaseModel, Field
from typing import Optional, List, Any
from app.domain.state import PersonalWishesState, FieldStatus
from app.domain.engine import StateUpdateResult
from app.domain.llm import LLMExtractionResponse
from app.services.session_store import SessionStore, SessionData
from app.services.llm_provider import LLMProvider
from app.services.state_engine import process_changes
from app.services.document_generator import generate_document

class OrchestrationResponse(BaseModel):
    reply: str
    document: str
    state: PersonalWishesState
    recent_audit: List[Any] = Field(default_factory=list)
    conflicts: List[Any] = Field(default_factory=list)

class ConversationOrchestrator:
    def __init__(self, store: SessionStore, llm_provider: LLMProvider):
        self.store = store
        self.llm_provider = llm_provider

    async def process_message(self, session_id: str, message: str) -> OrchestrationResponse:
        session = self.store.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
            
        session.history.append({"role": "user", "content": message})
        
        # 1. Ask untrusted LLM for proposed changes
        llm_result = await self.llm_provider.extract_state_changes(session.history, session.state)
        
        if not llm_result.success or not llm_result.data:
            reply = f"I'm sorry, I had trouble processing that ({llm_result.error}). Could you rephrase?"
            session.history.append({"role": "assistant", "content": reply})
            self.store.save_session(session)
            return OrchestrationResponse(reply=reply, document=generate_document(session.state), state=session.state)
            
        # 2. Feed proposed changes to Trust-Aware State Engine
        update_result = process_changes(session.state, llm_result.data.changes)
        
        # 3. Commit accepted changes safely and update activity log
        session.state = update_result.new_state
        session.activity_log.extend(update_result.audit_log)
        
        # 4. Determine next question deterministically
        reply = self._select_next_question(session.state, update_result, llm_result.data)
        
        session.history.append({"role": "assistant", "content": reply})
        self.store.save_session(session)
        
        return OrchestrationResponse(
            reply=reply, 
            document=generate_document(session.state), 
            state=session.state,
            recent_audit=update_result.audit_log,
            conflicts=update_result.conflicts
        )

    def _select_next_question(self, state: PersonalWishesState, update_result: StateUpdateResult, llm_data: LLMExtractionResponse) -> str:
        # Priority 1: Unresolved Conflicts
        if update_result.conflicts:
            c = update_result.conflicts[0]
            # Ask for explicit correction
            return f"There's a conflict regarding your {c.field}. You previously provided a different answer. Could you clarify what it should be? (If you want to change it, please say 'Actually, ...')"
            
        # Priority 2: Unresolved Confirmations
        if update_result.confirmation_required:
            c = update_result.confirmation_required[0]
            return f"I want to make sure I got this right: should your {c.field} be recorded as '{c.proposed_value}'?"
            
        # Priority 3: Semantic Conflicts identified by the LLM
        if llm_data.potential_conflicts and len(llm_data.potential_conflicts) > 0:
            return f"I noticed a potential contradiction: {llm_data.potential_conflicts[0]} Could you please clarify so I can update the correct field?"
            
        # Priority 4: LLM explicitly requested clarification due to severe ambiguity
        if llm_data.needs_clarification and llm_data.suggested_question:
            return llm_data.suggested_question
            
        # Priority 5: Missing Information (Deterministic traversal)
        prompts = {
            "full_name": "What is your full name?",
            "home_address": "What is your home address?",
            "covers_worldwide_assets": "Does this document cover worldwide assets?",
            "has_children": "Do you have any children?",
            "children_names": "What are the names of your children?",
            "executor_name": "Who would you like to appoint as your executor?",
            "executor_relationship": "What is your relationship to the executor?",
            "specific_gifts": "Do you have any specific gifts you'd like to leave?",
            "additional_wishes": "Do you have any additional wishes?"
        }
        
        def needs_asking(field_name: str) -> bool:
            f = getattr(state, field_name)
            # We need to ask if it has no value AND hasn't been explicitly sourced as UNKNOWN
            return f.value is None and f.source is None

        if needs_asking("full_name"): return prompts["full_name"]
        if needs_asking("home_address"): return prompts["home_address"]
        if needs_asking("covers_worldwide_assets"): return prompts["covers_worldwide_assets"]
        if needs_asking("has_children"): return prompts["has_children"]
        if state.has_children.value is True and needs_asking("children_names"): return prompts["children_names"]
        if needs_asking("executor_name"): return prompts["executor_name"]
        if state.executor_name.value and needs_asking("executor_relationship"): return prompts["executor_relationship"]
        if needs_asking("specific_gifts"): return prompts["specific_gifts"]
        if needs_asking("additional_wishes"): return prompts["additional_wishes"]
        
        return "Thank you. I have collected all the necessary information to draft your Personal Wishes Document."
