from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import researcher_node, strategist_node, writer_node, editor_node

# Define the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("researcher", researcher_node)
workflow.add_node("strategist", strategist_node)
workflow.add_node("writer", writer_node)
workflow.add_node("editor", editor_node)

# Add edges (Linear Process)
workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "strategist")
workflow.add_edge("strategist", "writer")
workflow.add_edge("writer", "editor")
workflow.add_edge("editor", END)

# Compile
app = workflow.compile()
