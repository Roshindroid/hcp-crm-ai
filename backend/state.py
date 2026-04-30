from typing import TypedDict, Optional, Dict, Any


class InteractionState(TypedDict, total=False):
    input: str
    hcp_name: Optional[str]
    date: Optional[str]
    interaction_type: Optional[str]
    attendees: Optional[str]
    topics: Optional[str]
    sentiment: Optional[str]
    materials_shared: Optional[bool]
    summary: Optional[str]
    validation: Dict[str, Any]
