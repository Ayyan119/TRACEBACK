import os
import sys
import json
import asyncio
import logging

# Ensure root directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.workflow import build_investigation_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

async def run_scenario(scenario_path: str):
    print("\n============================================================")
    print(f"RUNNING SCENARIO: {os.path.basename(scenario_path)}")
    print("============================================================")
    
    with open(scenario_path, "r") as f:
        scenario_data = json.load(f)
        
    graph = build_investigation_graph()
    
    # Execute full LangGraph investigation graph asynchronously
    final_state = await graph.ainvoke(scenario_data)
    
    print("\n--- EXECUTION TRACE ---")
    for trace in final_state.get("execution_trace", []):
        print(f"[{trace['timestamp']}] Node '{trace['node']}' ({trace['duration_ms']}ms) -> {trace['details']}")
        
    print("\n--- ACCEPTED EVIDENCE ITEMS ---")
    for ev in final_state.get("accepted_evidence", []):
        print(f"- [{ev['evidence_id']}] ({ev['source_type']}) {ev['source_name']}: {ev['content'][:100]}...")

    print("\n--- RETRIEVED LOGS SUMMARY ---")
    logs = final_state.get("retrieved_logs", [])
    print(f"Total Log Records Retrieved: {len(logs)}")
    for log in logs[:3]:
        print(f"  [{log.get('level')}] {log.get('service')} - {log.get('message')}")

    print("\n--- RETRIEVAL DECISION ---")
    print(f"Retrieval Required: {final_state.get('retrieval_required')}")
    print(f"Retrieval Reason: {final_state.get('retrieval_reason')}")

    print("\n--- GENERATED RANKED HYPOTHESES ---")
    hypotheses = final_state.get("hypotheses", [])
    for idx, hyp in enumerate(hypotheses, 1):
        print(f"{idx}. {hyp['title']} (Confidence: {hyp['confidence']}%)")
        print(f"   Root Cause: {hyp['likely_root_cause']}")
        print(f"   Recommended Check: {hyp['recommended_next_check']}\n")

    return final_state

async def main():
    examples_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples"))
    scenarios = [
        os.path.join(examples_dir, "scenario_no_optional_evidence.json"),
        os.path.join(examples_dir, "scenario_with_documents.json"),
        os.path.join(examples_dir, "scenario_with_images.json"),
        os.path.join(examples_dir, "scenario_with_previous_incident.json"),
        os.path.join(examples_dir, "scenario_full_investigation.json"),
    ]
    
    for scenario in scenarios:
        if os.path.exists(scenario):
            await run_scenario(scenario)

if __name__ == "__main__":
    asyncio.run(main())
