import os
import sys
import json
import asyncio
import logging

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Force LangSmith Tracing Environment Variables
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = "Tracing Project"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

from app.graph.workflow import build_investigation_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


async def run_langsmith_traced_example():
    scenario_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples", "scenario_full_investigation.json"))
    
    with open(scenario_path, "r") as f:
        input_payload = json.load(f)
        
    print("============================================================")
    print("LANGSMITH TRACED EXECUTION — TRACEBACK INVESTIGATION AGENT")
    print("============================================================")
    print(f"LangSmith Project:  '{os.environ['LANGCHAIN_PROJECT']}'")
    print(f"LangSmith Endpoint: {os.environ['LANGCHAIN_ENDPOINT']}")
    print("============================================================")
    
    print("\n📥 INPUT PAYLOAD:")
    print(json.dumps(input_payload, indent=2))
    
    print("\n▶ Executing LangGraph workflow (Sending traces to LangSmith)...")
    graph = build_investigation_graph()
    
    final_state = await graph.ainvoke(input_payload)
    
    print("\n============================================================")
    print("📤 FINAL INVESTIGATION OUTPUT:")
    print("============================================================")
    
    output_summary = {
        "investigation_id": final_state.get("investigation_id"),
        "incident_id": final_state.get("incident_id"),
        "project_id": final_state.get("project_id"),
        "confidence": final_state.get("confidence"),
        "investigation_summary": final_state.get("investigation_summary"),
        "primary_hypothesis": final_state.get("selected_hypothesis"),
        "all_hypotheses": final_state.get("hypotheses"),
        "accepted_evidence_count": len(final_state.get("accepted_evidence", [])),
        "accepted_evidence": final_state.get("accepted_evidence"),
        "retrieved_logs_count": len(final_state.get("retrieved_logs", [])),
        "self_rag_decision": {
            "retrieval_required": final_state.get("retrieval_required"),
            "reason": final_state.get("retrieval_reason"),
            "search_queries": final_state.get("search_queries"),
        },
        "reranked_documents": final_state.get("reranked_documents"),
        "evidence_synthesis": final_state.get("evidence_analysis"),
        "execution_trace": final_state.get("execution_trace"),
    }
    
    print(json.dumps(output_summary, indent=2))
    print("\n============================================================")
    print("✔ EXECUTION COMPLETE & TRACED TO LANGSMITH!")
    print(f"Analyze the trace graph on LangSmith: https://smith.langchain.com")
    print(f"Project Name: '{os.environ['LANGCHAIN_PROJECT']}'")
    print("============================================================")
    
    return final_state

if __name__ == "__main__":
    asyncio.run(run_langsmith_traced_example())
