import os
import json
from datetime import date as _date
from langchain_groq import ChatGroq
from pydantic import SecretStr


_api_key = os.environ.get("GROQ_API_KEY")
if not _api_key:
    raise RuntimeError("GROQ_API_KEY environment variable is not set")

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=SecretStr(_api_key),
)


# ---------------------------
# TOOL 1: LOG INTERACTION (LLM extraction)
# ---------------------------
def _extract_fields(user_input: str) -> dict:
    """Call the LLM and return a dict of extracted CRM fields. Missing fields are None."""
    today = _date.today().isoformat()

    prompt = f"""You are a CRM data extraction specialist.
Today's date is {today}. Use this to resolve relative dates like "today", "yesterday", "last Monday".

Extract interaction details from the user's input.

RULES:
1. Return ONLY valid JSON, no markdown, no commentary.
2. Keys MUST be exactly: hcp_name, date, interaction_type, attendees, topics, sentiment, materials_shared.
3. "date" MUST be in YYYY-MM-DD format (or null if not given).
4. "interaction_type" MUST be one of: "Meeting", "Call", "Email" (or null if unclear).
5. "materials_shared" is true ONLY if brochures/slides/docs/materials are explicitly mentioned as shared, false if explicitly NOT shared, otherwise null.
6. "sentiment" should be a short word like "positive", "negative", "neutral" (or null if not stated).
7. If a piece of information is not in the input, use null. Do NOT invent values.

Input: "{user_input}"

Example Output:
{{"hcp_name": "Dr. Smith", "date": "{today}", "interaction_type": "Meeting", "attendees": "Team", "topics": "Cancer drugs", "sentiment": "positive", "materials_shared": true}}
"""

    extracted = {
        "hcp_name": None,
        "date": None,
        "interaction_type": None,
        "attendees": None,
        "topics": None,
        "sentiment": None,
        "materials_shared": None,
    }

    try:
        response = llm.invoke(prompt)
        text = str(response.content).strip()
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        for key in extracted:
            if key in parsed:
                extracted[key] = parsed[key]
    except Exception as e:
        print(f"BACKEND extraction error: {e}")

    return extracted


def log_interaction(state):
    """Extract CRM fields from the input and merge them into state (initial log)."""
    extracted = _extract_fields(state.get("input", ""))
    merged = dict(state)
    for key, value in extracted.items():
        if value is not None:
            merged[key] = value
    return merged


# ---------------------------
# TOOL 2: EDIT INTERACTION
# ---------------------------
def edit_interaction(state):
    """Apply user corrections: extract from the correction text and overwrite ONLY
    the fields the user actually mentioned. All other existing fields are preserved."""
    extracted = _extract_fields(state.get("input", ""))
    merged = dict(state)
    for key, value in extracted.items():
        if value is not None:
            merged[key] = value
    return merged


# ---------------------------
# TOOL 3: VALIDATE INTERACTION
# ---------------------------
def validate_interaction(state):
    missing = []
    required_fields = ["hcp_name", "date", "interaction_type"]

    for field in required_fields:
        if not state.get(field):
            missing.append(field)

    return {
        **state,
        "validation": {
            "is_valid": len(missing) == 0,
            "missing_fields": missing,
        },
    }


# ---------------------------
# TOOL 4: SENTIMENT TOOL
# ---------------------------
def sentiment_tool(state):
    text = state.get("input", "").lower()
    sentiment = state.get("sentiment") or "neutral"

    if any(w in text for w in ["good", "positive", "great", "excited", "happy"]):
        sentiment = "positive"
    elif any(w in text for w in ["bad", "negative", "angry", "frustrated", "upset"]):
        sentiment = "negative"

    return {**state, "sentiment": sentiment}


# ---------------------------
# TOOL 5: SUMMARY TOOL
# ---------------------------
def summary_tool(state):
    summary = (
        f"Met {state.get('hcp_name')} on {state.get('date')} "
        f"about {state.get('topics')}."
    )
    return {**state, "summary": summary}
