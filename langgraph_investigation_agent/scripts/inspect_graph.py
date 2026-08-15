import os
import sys

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.workflow import build_investigation_graph

def main():
    print("============================================================")
    print("LANGGRAPH INVESTIGATION AGENT GRAPH INSPECTION — 14 NODES")
    print("============================================================")
    
    graph = build_investigation_graph()
    
    print("\n--- GRAPH NODES ---")
    nodes = list(graph.nodes.keys())
    for idx, node in enumerate(nodes, 1):
        print(f"{idx}. {node}")
        
    print("\n--- GRAPH GENERATED MERMAID DIAGRAM ---")
    try:
        mermaid_code = graph.get_graph().draw_mermaid()
        print(mermaid_code)
    except Exception as e:
        print(f"Could not generate draw_mermaid natively: {e}")
        mermaid_code = """
graph TD
    START([START]) --> initialize_state
    initialize_state --> process_images
    initialize_state --> process_documents
    process_images --> collect_evidence
    process_documents --> collect_evidence
    collect_evidence --> reason_with_tools
    reason_with_tools -.->|query_logs| execute_log_tools
    execute_log_tools --> reason_with_tools
    reason_with_tools -.->|no_tool| incident_analyzer
    incident_analyzer -.->|retrieval_required| retrieve_knowledge
    incident_analyzer -.->|no_retrieval| analyze_evidence
    retrieve_knowledge --> retrieve_previous_incidents
    retrieve_previous_incidents --> rerank_retrieved_information
    rerank_retrieved_information --> analyze_evidence
    analyze_evidence --> generate_hypotheses
    generate_hypotheses --> evaluate_hypotheses
    evaluate_hypotheses -.->|insufficient| reason_with_tools
    evaluate_hypotheses -.->|sufficient| generate_final_report
    generate_final_report --> END([END])
"""

    # Save Mermaid Diagram
    diagrams_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "diagrams"))
    os.makedirs(diagrams_dir, exist_ok=True)
    
    mmd_path = os.path.join(diagrams_dir, "investigation_workflow.mmd")
    with open(mmd_path, "w") as f:
        f.write(mermaid_code)
    print(f"\nSaved Mermaid diagram to {mmd_path}")
    
    # Try PNG rendering natively via LangGraph or fallback generator
    try:
        png_data = graph.get_graph().draw_mermaid_png()
        png_path = os.path.join(diagrams_dir, "investigation_workflow.png")
        with open(png_path, "wb") as f:
            f.write(png_data)
        print(f"Saved PNG diagram to {png_path}")
    except Exception as e:
        print(f"Native PNG draw fallback active ({e})")
        png_path = os.path.join(diagrams_dir, "investigation_workflow.png")
        with open(png_path, "wb") as f:
            f.write(b"PNG_PLACEHOLDER_WORKFLOW")
        print(f"Saved PNG diagram placeholder to {png_path}")

    # Generate SVG file
    svg_path = os.path.join(diagrams_dir, "investigation_workflow.svg")
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="700" viewBox="0 0 900 700">
  <rect width="100%" height="100%" fill="#0D1117"/>
  <text x="450" y="35" font-family="monospace" font-size="18" fill="#58A6FF" text-anchor="middle">TRACEBACK AI Investigation Agent Full Workflow</text>
  <text x="450" y="65" font-family="sans-serif" font-size="12" fill="#8B949E" text-anchor="middle">14-Node Agentic Investigation Loop Architecture</text>
  <g transform="translate(150, 90)">
    <rect x="220" y="0" width="160" height="35" rx="8" fill="#1F6FEB" stroke="#58A6FF"/>
    <text x="300" y="22" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">START -> Init</text>
    <path d="M 300 35 L 180 65" stroke="#58A6FF" stroke-width="2"/>
    <path d="M 300 35 L 420 65" stroke="#58A6FF" stroke-width="2"/>
    <rect x="100" y="65" width="160" height="35" rx="8" fill="#238636" stroke="#3FB950"/>
    <text x="180" y="87" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Process Images</text>
    <rect x="340" y="65" width="160" height="35" rx="8" fill="#238636" stroke="#3FB950"/>
    <text x="420" y="87" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Process Docs</text>
    <path d="M 180 100 L 300 130" stroke="#58A6FF" stroke-width="2"/>
    <path d="M 420 100 L 300 130" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="130" width="160" height="35" rx="8" fill="#8957E5" stroke="#A371F7"/>
    <text x="300" y="152" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Collect Evidence</text>
    <path d="M 300 165 L 300 195" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="195" width="160" height="35" rx="8" fill="#D29922" stroke="#E3B341"/>
    <text x="300" y="217" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">LLM + Tool Loop</text>
    <path d="M 300 230 L 300 260" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="260" width="160" height="35" rx="8" fill="#F85149" stroke="#FF7B72"/>
    <text x="300" y="282" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Self-RAG Analyzer</text>
    <path d="M 300 295 L 300 325" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="325" width="160" height="35" rx="8" fill="#1F6FEB" stroke="#58A6FF"/>
    <text x="300" y="347" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Qdrant Retrieval</text>
    <path d="M 300 360 L 300 390" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="390" width="160" height="35" rx="8" fill="#238636" stroke="#3FB950"/>
    <text x="300" y="412" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Reranker & Evidence</text>
    <path d="M 300 425 L 300 455" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="455" width="160" height="35" rx="8" fill="#8957E5" stroke="#A371F7"/>
    <text x="300" y="477" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Generate Hypotheses</text>
    <path d="M 300 490 L 300 520" stroke="#58A6FF" stroke-width="2"/>
    <rect x="220" y="520" width="160" height="35" rx="8" fill="#D29922" stroke="#E3B341"/>
    <text x="300" y="542" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Evaluate Hypotheses</text>
    <path d="M 380 537 C 480 537 480 212 380 212" stroke="#F85149" stroke-width="2" stroke-dasharray="4,4" fill="none"/>
    <text x="490" y="375" fill="#F85149" font-family="monospace" font-size="10">Loop Back (Insufficient)</text>
    <path d="M 300 555 L 300 585" stroke="#3FB950" stroke-width="2"/>
    <rect x="220" y="585" width="160" height="35" rx="8" fill="#238636" stroke="#3FB950"/>
    <text x="300" y="607" fill="#FFFFFF" font-family="monospace" font-size="11" text-anchor="middle">Final Report -> END</text>
  </g>
</svg>"""
    with open(svg_path, "w") as f:
        f.write(svg_content)
    print(f"Saved SVG diagram to {svg_path}")

if __name__ == "__main__":
    main()
