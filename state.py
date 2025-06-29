# state.py

def initialize_state(topic):
    return {
        "topic": topic,
        "current_round": 1,
        "last_speaker": None,
        "dialogue_history": [],
        "memory": [],
        "judge_summary": None,
        "winner": None
    }
