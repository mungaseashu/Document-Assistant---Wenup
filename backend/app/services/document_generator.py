from app.domain.state import PersonalWishesState, StateField, FieldStatus

def format_field(field: StateField) -> str:
    """
    Safely formats a field based on its trust status.
    Prevents unconfirmed or unknown information from being presented as confirmed facts.
    """
    if field.status in [FieldStatus.PROPOSED, FieldStatus.NEEDS_CONFIRMATION]:
        return "*[Information requires confirmation]*"
        
    if field.status == FieldStatus.UNKNOWN or field.value is None:
        return "*[Not specified]*"
        
    # The field is CONFIRMED or CORRECTED, we can safely display its value
    if isinstance(field.value, bool):
        return "Yes" if field.value else "No"
        
    if isinstance(field.value, list):
        return ", ".join(field.value) if field.value else "None"
        
    return str(field.value)

def generate_document(state: PersonalWishesState) -> str:
    """
    Deterministically maps the validated structured state into a draft Markdown document.
    """
    doc = "# Fictional Personal Wishes Document\n\n"
    doc += "**FICTIONAL – NOT LEGAL ADVICE**\n\n"
    doc += "---\n\n"
    
    doc += "## 1. Personal Information\n"
    doc += f"**Full Name:** {format_field(state.full_name)}\n\n"
    doc += f"**Home Address:** {format_field(state.home_address)}\n\n"
    
    doc += "## 2. Assets & Family\n"
    doc += f"**Covers Worldwide Assets:** {format_field(state.covers_worldwide_assets)}\n\n"
    doc += f"**Has Children:** {format_field(state.has_children)}\n\n"
    
    # Only render children names if explicitly confirmed to have children, or if it needs confirmation
    if state.has_children.value is True or state.has_children.status in [FieldStatus.PROPOSED, FieldStatus.NEEDS_CONFIRMATION]:
        doc += f"**Children Names:** {format_field(state.children_names)}\n\n"
        
    doc += "## 3. Executor Appointment\n"
    doc += f"**Executor Name:** {format_field(state.executor_name)}\n\n"
    if state.executor_name.value or state.executor_name.status in [FieldStatus.PROPOSED, FieldStatus.NEEDS_CONFIRMATION]:
        doc += f"**Executor Relationship:** {format_field(state.executor_relationship)}\n\n"
        
    doc += "## 4. Specific Gifts & Additional Wishes\n"
    doc += f"**Specific Gifts:** {format_field(state.specific_gifts)}\n\n"
    doc += f"**Additional Wishes:** {format_field(state.additional_wishes)}\n\n"
    
    return doc
