import datetime
import json
import pathlib
import sys

state = json.load(sys.stdin)
keys = [
    "conversation_id", "cwd", "model", "version",
    "context_window", "transcript_path", "agent_state",
    "cycle_mode", "sandbox", "tool_confirmation_pending"
]
record = {key: state.get(key) for key in keys}
record["captured_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

destination = pathlib.Path(__file__).parent / "interactive-state.jsonl"
with destination.open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(record) + "\n")

print("Telemetry capture active")
