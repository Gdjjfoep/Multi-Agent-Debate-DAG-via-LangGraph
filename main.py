from dag_builder import build_graph
from rich import print
from rich.prompt import Prompt

def run_debate():
    topic = Prompt.ask("Enter topic for debate")
    print(f"\n=== 🧠 Running Debate on Topic: [bold green]{topic}[/bold green] ===\n")

    state = {
        "topic": topic,
        "current_round": 0,
        "last_speaker": None,
        "memory": [],
        "dialogue_history": [],
        "judge_summary": "",
        "winner": None
    }

    graph = build_graph()  # Don't call .compile() here again

    result = graph.invoke(state)

    print("\n=== 🧠 Debate Transcript ===\n")
    for turn in result.get("dialogue_history", []):
        print(f"[{turn['round']}] {turn['speaker']}: {turn['argument']}")


    print("\n=== 📋 Debate Summary ===")
    print(result.get("judge_summary", "No summary provided."))

    print(f"\n🏆 Winner: [bold yellow]{result.get('winner', 'None')}[/bold yellow]")

if __name__ == "__main__":
    run_debate()
