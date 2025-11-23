#!/usr/bin/env python3
"""
Create an EvalSet from a single scenarios file where each scenario entry
contains an embedded session_input. The script persists the EvalSet using
LocalEvalSetsManager so you can run the evaluation later with the CLI:

  adk eval path/to/agent/__init__.py <eval_set_id> --config_file_path <cfg>

Usage:
  python create_usersim_evalset_with_per_scenario_sessions.py \
      --agent-module-path path/to/agent/__init__.py \
      --scenarios-file eval/eval_data/returns_refunds_scenarios_with_sessions.json \
      --eval-set-id returns_refunds_evalset

Input JSON format (example):
{
  "scenarios": [
    {
      "scenario": { ... ConversationScenario JSON ... },
      "session_input": {
        "app_name": "my_agent",
        "user_id": "user_1",
        "state": {"some_key": "some_value"}
      }
    },
    {
      "scenario": { ... },
      "session_input": { ... }
    }
  ]
}

Also supported:
- Top-level can be a list (not wrapped in "scenarios").
- Each entry may use key "scenario" or "conversation_scenario" for the scenario object.
- If a scenario entry does not include session_input, a default SessionInput is created
  using the agent module basename as app_name and user_id "test_user".
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime

# ADK imports (use same modules used by the CLI)
from google.adk.evaluation.eval_case import EvalCase, SessionInput
from google.adk.evaluation.eval_set import EvalSet
from google.adk.evaluation.local_eval_sets_manager import LocalEvalSetsManager
from google.adk.evaluation.conversation_scenarios import ConversationScenario

def make_eval_id_from_scenario_dict(scenario_dict: dict) -> str:
  """Deterministic short id similar to CLI: sha256 of scenario JSON, first 8 hex chars"""
  s = json.dumps(scenario_dict, sort_keys=True, separators=(",", ":"))
  return hashlib.sha256(s.encode("utf-8")).hexdigest()[:8]

def extract_scenarios_and_sessions(raw_obj, default_app_name: str):
  """
  Normalize the input into a list of tuples: (scenario_dict, session_input_dict_or_None)
  Accepts either:
    - an object with "scenarios": [ ... ]
    - a list of entries
  Each entry can be:
    - { "scenario": {...}, "session_input": {...} }
    - { "conversation_scenario": {...}, "session_input": {...} }
    - or { ... scenario fields ..., "session_input": {...} } (we will remove session_input)
  """
  entries = []
  if isinstance(raw_obj, dict) and "scenarios" in raw_obj and isinstance(raw_obj["scenarios"], list):
    list_entries = raw_obj["scenarios"]
  elif isinstance(raw_obj, list):
    list_entries = raw_obj
  else:
    raise ValueError("Unsupported scenarios file format: top-level must be a list or an object with 'scenarios' list.")

  for item in list_entries:
    if not isinstance(item, dict):
      raise ValueError("Each scenario entry must be a JSON object/dict.")

    # session_input may be present
    session_input = item.get("session_input")
    # scenario can be under keys "scenario" or "conversation_scenario", otherwise the item itself (minus session_input)
    if "scenario" in item:
      scenario_obj = item["scenario"]
    elif "conversation_scenario" in item:
      scenario_obj = item["conversation_scenario"]
    else:
      # Make a shallow copy and remove session_input to get the scenario payload
      scenario_obj = {k: v for k, v in item.items() if k != "session_input"}

    # Ensure scenario_obj is not empty
    if not scenario_obj:
      raise ValueError("Scenario entry appears empty after extracting 'session_input'.")

    entries.append((scenario_obj, session_input))

  return entries

def build_eval_cases(entries, default_app_name: str):
  eval_cases = []
  for scenario_obj, sess_in_raw in entries:
    # Validate scenario using ConversationScenario model (will raise if invalid)
    conv_scenario = ConversationScenario.model_validate(scenario_obj)

    # Build SessionInput
    if sess_in_raw:
      # If user omitted app_name, populate it with default_app_name for convenience
      if default_app_name and "app_name" not in sess_in_raw:
        sess_in_raw["app_name"] = default_app_name
      session_input = SessionInput.model_validate(sess_in_raw)
    else:
      # create a minimal default SessionInput
      if not default_app_name:
        raise ValueError("No session_input provided and agent module basename unknown to set default app_name.")
      session_input = SessionInput.model_validate({
          "app_name": default_app_name,
          "user_id": "test_user",
          "state": {}
      })

    eval_id = make_eval_id_from_scenario_dict(scenario_obj)
    eval_case = EvalCase(
        eval_id=eval_id,
        conversation_scenario=conv_scenario,
        session_input=session_input,
        creation_timestamp=datetime.now().timestamp(),
    )
    eval_cases.append(eval_case)
  return eval_cases

def persist_eval_set(app_name: str, agents_dir: str, eval_set_id: str, eval_cases):
  """
  Persist an EvalSet using LocalEvalSetsManager. If eval set exists, we will
  skip create and add only new eval cases.
  """
  manager = LocalEvalSetsManager(agents_dir=agents_dir)

  # create eval set if not exists
  try:
    manager.create_eval_set(app_name=app_name, eval_set_id=eval_set_id)
    print(f"Created eval set '{eval_set_id}' for app '{app_name}'.")
  except ValueError:
    print(f"Eval set '{eval_set_id}' already exists for app '{app_name}', will add cases to it.")

  added = 0
  skipped = 0
  for case in eval_cases:
    existing = manager.get_eval_case(app_name=app_name, eval_set_id=eval_set_id, eval_case_id=case.eval_id)
    if existing is None:
      manager.add_eval_case(app_name=app_name, eval_set_id=eval_set_id, eval_case=case)
      print(f"Added eval case '{case.eval_id}'.")
      added += 1
    else:
      print(f"Eval case '{case.eval_id}' already exists, skipping.")
      skipped += 1

  print(f"Done. Added: {added}, Skipped: {skipped}. EvalSet persisted under agents_dir='{agents_dir}'")

def main():
  ap = argparse.ArgumentParser(description="Create/persist EvalSet with per-scenario session_input embedded in the scenarios file.")
  ap.add_argument("--agent-module-path", required=True, help="Path to agent module __init__.py (same as CLI uses).")
  ap.add_argument("--scenarios-file", required=True, help="JSON file containing scenarios with embedded session_input.")
  ap.add_argument("--eval-set-id", required=True, help="Eval set id to create/persist.")
  args = ap.parse_args()

  agent_module_path = args.agent_module_path
  scenarios_file = args.scenarios_file
  eval_set_id = args.eval_set_id

  if not os.path.exists(agent_module_path):
    print(f"Agent module path '{agent_module_path}' does not exist.", file=sys.stderr)
    sys.exit(2)

  with open(scenarios_file, "r", encoding="utf-8") as f:
    raw = json.load(f)

  default_app_name = os.path.basename(agent_module_path)
  agents_dir = os.path.dirname(agent_module_path) or "."

  entries = extract_scenarios_and_sessions(raw, default_app_name=default_app_name)
  eval_cases = build_eval_cases(entries, default_app_name=default_app_name)

  # Persist via LocalEvalSetsManager
  persist_eval_set(app_name=default_app_name, agents_dir=agents_dir, eval_set_id=eval_set_id, eval_cases=eval_cases)

  print("\nNow you can run the eval via CLI, using the same agent module path:")
  print(f"  adk eval {agent_module_path} {eval_set_id} --print_detailed_results")

if __name__ == "__main__":
  main()