import os
import logging
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DeepSeek API setup
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY") or "your-api-key-here"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

def call_deepseek(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()


# === Nodes ===

def user_input_node(state):
    topic = input("Enter topic for debate: ").strip()
    logger.info(f"[UserInputNode] Topic entered: {topic}")
    return {
        "topic": topic,
        "current_round": 0,
        "last_speaker": "",
        "memory": [],
        "dialogue_history": [],
        "judge_summary": "",
        "winner": ""
    }


def agent_node(state, agent_type):
    logger.info(f"[AgentNode] Starting {agent_type}, Round {state['current_round']}")
    
    round_num = state["current_round"]  # ✅ Define this first
    prompt = f"As a {agent_type}, argue round {round_num} on {state['topic']}"
    logger.info(f"[AgentNode] Prompt: {prompt}")

    try:
        response = call_deepseek(prompt)
        logger.info("[AgentNode] API response received")
    except Exception as e:
        logger.error(f"[AgentNode] API failed: {e}")
        response = "[Error: no response]"

    print(f"\n[Round {round_num}] {agent_type}: {response}\n")  # For live feedback

    state["dialogue_history"].append({
        "round": round_num,
        "speaker": agent_type,
        "argument": response
    })
    state["current_round"] += 1
    state["last_speaker"] = agent_type
    return state

    ...
    try:
        response = call_deepseek(prompt)
        logger.info("[AgentNode] API response received")
    except Exception as e:
        logger.error(f"[AgentNode] API failed: {e}")
        response = "[Error: no response]"

    # Add this line to display output immediately:
    print(f"\n[Round {state['current_round']}] {agent_type}: {response}\n")

    state["dialogue_history"].append({
        "round": round_num,
        "speaker": agent_type,
        "argument": response
    })
    ...

    logger.info(f"[AgentNode] Starting {agent_type}, Round {state['current_round']}")

    topic = state["topic"]
    round_num = state["current_round"]
    dialogue = state.get("dialogue_history", [])

    dialogue_str = "\n".join(
        f"{entry['speaker']}: {entry['argument']}" for entry in dialogue
    )

    prompt = f"""You are a {agent_type} participating in a structured debate.
Topic: {topic}
Round: {round_num}

Previous dialogue:
{dialogue_str if dialogue_str else '(None yet)'}

Present your argument:"""

    try:
        response = call_deepseek(prompt)
        logger.info("[AgentNode] API response received")
    except Exception as e:
        logger.error(f"[AgentNode] API failed: {e}")
        response = "[Error: no response]"

    state["dialogue_history"].append({
        "round": round_num,
        "speaker": agent_type,  # 👈 changed from 'agent' to 'speaker'
        "argument": response
    })
    state["current_round"] += 1
    state["last_speaker"] = agent_type
    return state


def memory_node(state):
    logger.info(f"[MemoryNode] Current dialogue length: {len(state.get('dialogue_history', []))}")
    memory_str = "\n".join(
        f"{entry['speaker']}: {entry['argument']}" for entry in state.get("dialogue_history", [])
    )
    state["memory"].append(memory_str)
    return state


def judge_node(state):
    dialogue = state.get("dialogue_history", [])

    summary_prompt = """You are a neutral debate judge.
Summarize the debate and decide a winner based on reasoning, evidence, and clarity.
Transcript:"""

    for entry in dialogue:
        summary_prompt += f"\n{entry['speaker']}: {entry['argument']}"

    summary_prompt += "\n\nProvide a summary of the debate and declare a winner (Scientist or Philosopher)."

    try:
        summary_response = call_deepseek(summary_prompt)
    except Exception as e:
        logger.error(f"[JudgeNode] API failed: {e}")
        summary_response = "[Error generating summary]"

    state["judge_summary"] = summary_response

    if "scientist" in summary_response.lower():
        state["winner"] = "Scientist"
    elif "philosopher" in summary_response.lower():
        state["winner"] = "Philosopher"
    else:
        state["winner"] = "None"

    return state
