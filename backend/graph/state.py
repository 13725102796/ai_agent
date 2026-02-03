from typing import TypedDict, List, Annotated
import operator

class AgentState(TypedDict):
    topic: str
    research_data: str
    strategy_prompt: str
    draft: str
    critique: str
    final_article: str
