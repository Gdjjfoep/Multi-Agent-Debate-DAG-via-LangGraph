from typing import TypedDict
from langgraph.graph import StateGraph
from nodes import user_input_node, agent_node, memory_node, judge_node

class DebateState(TypedDict, total=False):
    topic: str
    current_round: int
    last_speaker: str
    memory: list[str]
    dialogue_history: list[dict]
    judge_summary: str
    winner: str

def get_next_node(state: DebateState) -> str:
    if state["current_round"] >= 8:
        return "JudgeNode"
    return "AgentA" if state["current_round"] % 2 == 0 else "AgentB"

def build_graph():
    builder = StateGraph(DebateState)

    builder.add_node("UserInputNode", user_input_node)
    builder.add_node("AgentA", lambda state: agent_node(state, "Scientist"))
    builder.add_node("AgentB", lambda state: agent_node(state, "Philosopher"))
    builder.add_node("MemoryNode", memory_node)
    builder.add_node("JudgeNode", judge_node)
    builder.add_node("END", lambda state: state)

    builder.set_entry_point("UserInputNode")
    builder.add_edge("UserInputNode", "MemoryNode")
    builder.add_conditional_edges("MemoryNode", get_next_node)
    builder.add_edge("AgentA", "MemoryNode")
    builder.add_edge("AgentB", "MemoryNode")
    builder.add_edge("JudgeNode", "END")

    return builder.compile()

