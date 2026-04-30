from langgraph.graph import StateGraph, END
from state import InteractionState
from tools import (
    log_interaction,
    edit_interaction,
    validate_interaction,
    sentiment_tool,
    summary_tool,
)


# ---------------------------
# ROUTER (decides next step after log/edit)
# ---------------------------
def router(state):
    text = state.get("input", "").lower()

    # Correction case -> edit once, then continue down the validate path
    if any(w in text for w in ["sorry", "actually", "correction", "i meant"]):
        return "edit"

    return "validate"


# ---------------------------
# BUILD GRAPH
# ---------------------------
graph = StateGraph(InteractionState)

graph.add_node("log", log_interaction)
graph.add_node("edit", edit_interaction)
graph.add_node("validate", validate_interaction)
graph.add_node("sentiment", sentiment_tool)
graph.add_node("summary", summary_tool)

graph.set_entry_point("log")

graph.add_conditional_edges(
    "log",
    router,
    {
        "edit": "edit",
        "validate": "validate",
    },
)

graph.add_edge("edit", "validate")
graph.add_edge("validate", "sentiment")
graph.add_edge("sentiment", "summary")
graph.add_edge("summary", END)

app = graph.compile()
