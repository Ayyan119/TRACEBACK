import os
import sys
import time
import asyncio
import json
import logging

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.nodes import (
    initialize_state_node,
    process_images_node,
    process_documents_node,
    collect_evidence_node,
    reason_with_tools_node,
    execute_log_tools_node,
    incident_analyzer_node,
    retrieve_knowledge_node,
    retrieve_previous_incidents_node,
    rerank_retrieved_information_node,
    analyze_evidence_node,
    generate_hypotheses_node,
    evaluate_hypotheses_node,
    generate_final_report_node,
)
from app.graph.state import InvestigationState

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


async def run_individual_node_tests():
    print("============================================================")
    print("EMPIRICAL INDIVIDUAL NODE TEST SUITE — 14 NODES ISOLATED")
    print("============================================================")

    results = []

    # 1. initialize_state_node
    start = time.time()
    state1: InvestigationState = {
        "incident_id": "INC-1001",
        "project_id": "art-gallary",
        "incident_description": "Checkout service returning 504 gateway timeout",
    }
    res1 = await initialize_state_node(state1)
    dur1 = (time.time() - start) * 1000
    pass1 = (res1.get("project_id") == "art-gallary" and res1.get("incident_id") == "INC-1001" and "investigation_id" in res1)
    results.append(("1. initialize_state_node", pass1, dur1, f"InvID={res1.get('investigation_id')}"))

    # 2. process_images_node
    start = time.time()
    state2: InvestigationState = {
        "incident_images": [
            {"title": "Grafana Latency Error Screenshot", "file_url": "/tmp/grafana_504_error.png"},
            {"title": "Company Wallpaper Logo", "file_url": "/tmp/logo.jpg"},
        ]
    }
    res2 = await process_images_node(state2)
    dur2 = (time.time() - start) * 1000
    imgs = res2.get("processed_image_evidence", [])
    pass2 = (len(imgs) == 2 and imgs[0]["relevant"] is True and imgs[1]["relevant"] is False)
    results.append(("2. process_images_node", pass2, dur2, f"Processed={len(imgs)}, Relevant={sum(1 for i in imgs if i['relevant'])}"))

    # 3. process_documents_node
    start = time.time()
    state3: InvestigationState = {
        "incident_description": "PostgreSQL database connection pool timeout",
        "incident_documents": [
            {"name": "Database Lock Diagnostic.pdf", "content": "Connection pool timeout waiting for connection from pool limit."},
            {"name": "Friday Pizza Party Menu.pdf", "content": "Pizza choices and drinks list."},
        ]
    }
    res3 = await process_documents_node(state3)
    dur3 = (time.time() - start) * 1000
    docs = res3.get("processed_document_evidence", [])
    pass3 = (len(docs) == 2 and docs[0]["relevant"] is True and docs[1]["relevant"] is False)
    results.append(("3. process_documents_node", pass3, dur3, f"Processed={len(docs)}, Relevant={sum(1 for d in docs if d['relevant'])}"))

    # 4. collect_evidence_node
    start = time.time()
    state4: InvestigationState = {
        "incident_description": "Checkout service returning HTTP 504",
        "incident_log_reference": {"file_name": "app.log", "file_size_bytes": 1048576},
        "processed_image_evidence": imgs,
        "processed_document_evidence": docs,
    }
    res4 = await collect_evidence_node(state4)
    dur4 = (time.time() - start) * 1000
    accepted = res4.get("accepted_evidence", [])
    rejected = res4.get("rejected_evidence", [])
    pass4 = len(accepted) == 4 and len(rejected) == 2
    results.append(("4. collect_evidence_node", pass4, dur4, f"Accepted={len(accepted)}, Rejected={len(rejected)}"))

    # 5. reason_with_tools_node
    start = time.time()
    state5a: InvestigationState = {"tool_iterations": 0, "retrieved_logs": []}
    res5a = await reason_with_tools_node(state5a)
    state5b: InvestigationState = {"tool_iterations": 5, "retrieved_logs": [{"id": 1}]}
    res5b = await reason_with_tools_node(state5b)
    dur5 = (time.time() - start) * 1000
    pass5 = (res5a.get("tool_decision") == "query_logs" and res5b.get("tool_decision") == "no_tool")
    results.append(("5. reason_with_tools_node", pass5, dur5, f"Iter0 -> {res5a.get('tool_decision')}, Iter5 -> {res5b.get('tool_decision')}"))

    # 6. execute_log_tools_node
    start = time.time()
    state6: InvestigationState = {
        "project_id": "art-gallary",
        "incident_id": "INC-1001",
        "services": ["checkout-service"],
        "tool_iterations": 1,
        "log_query_history": [],
        "retrieved_logs": [],
    }
    res6 = await execute_log_tools_node(state6)
    dur6 = (time.time() - start) * 1000
    logs = res6.get("retrieved_logs", [])
    pass6 = len(logs) > 0
    results.append(("6. execute_log_tools_node", pass6, dur6, f"LogsRetrieved={len(logs)}"))

    # 7. incident_analyzer_node
    start = time.time()
    state7: InvestigationState = {
        "incident_description": "PostgreSQL connection pool max_connections lock contention outage",
        "accepted_evidence": accepted,
        "retrieved_logs": logs,
    }
    res7 = await incident_analyzer_node(state7)
    dur7 = (time.time() - start) * 1000
    ret_req = res7.get("retrieval_required")
    queries = res7.get("search_queries", [])
    pass7 = isinstance(ret_req, bool) and len(queries) > 0
    results.append(("7. incident_analyzer_node", pass7, dur7, f"RetrievalRequired={ret_req}, Queries={len(queries)}"))

    # 8. retrieve_knowledge_node
    start = time.time()
    state8: InvestigationState = {
        "project_id": "art-gallary",
        "search_queries": ["PostgreSQL database connection pool troubleshooting runbook"],
    }
    res8 = await retrieve_knowledge_node(state8)
    dur8 = (time.time() - start) * 1000
    chunks = res8.get("retrieved_knowledge_documents", [])
    pass8 = len(chunks) > 0 and chunks[0]["source_type"] == "knowledge_document"
    results.append(("8. retrieve_knowledge_node", pass8, dur8, f"ChunksRetrieved={len(chunks)}"))

    # 9. retrieve_previous_incidents_node
    start = time.time()
    state9: InvestigationState = {
        "project_id": "art-gallary",
        "search_queries": ["lock contention outage"],
        "previous_incident_search_required": True,
    }
    res9 = await retrieve_previous_incidents_node(state9)
    dur9 = (time.time() - start) * 1000
    prev_inc = res9.get("retrieved_previous_incidents", [])
    pass9 = len(prev_inc) > 0 and prev_inc[0]["source_type"] == "incident_history"
    results.append(("9. retrieve_previous_incidents_node", pass9, dur9, f"PreviousIncidentsRetrieved={len(prev_inc)}"))

    # 10. rerank_retrieved_information_node
    start = time.time()
    state10: InvestigationState = {
        "incident_description": "PostgreSQL connection pool max_connections lock contention outage",
        "retrieved_knowledge_documents": chunks,
        "retrieved_previous_incidents": prev_inc,
    }
    res10 = await rerank_retrieved_information_node(state10)
    dur10 = (time.time() - start) * 1000
    reranked = res10.get("reranked_documents", [])
    pass10 = len(reranked) > 0
    results.append(("10. rerank_retrieved_information_node", pass10, dur10, f"RerankedKept={len(reranked)}/{len(chunks)+len(prev_inc)}"))

    # 11. analyze_evidence_node
    start = time.time()
    state11: InvestigationState = {
        "incident_description": "Checkout service failing with 504 Gateway Timeouts",
        "services": ["checkout-service"],
        "retrieved_logs": logs,
        "reranked_documents": reranked,
        "accepted_evidence": accepted,
    }
    res11 = await analyze_evidence_node(state11)
    dur11 = (time.time() - start) * 1000
    ev_synth = res11.get("evidence_analysis", {})
    pass11 = isinstance(ev_synth, dict) and ev_synth.get("affected_service") == "checkout-service"
    results.append(("11. analyze_evidence_node", pass11, dur11, f"AffectedService={ev_synth.get('affected_service')}"))

    # 12. generate_hypotheses_node
    start = time.time()
    state12: InvestigationState = {
        "incident_id": "INC-1001",
        "evidence_analysis": ev_synth,
        "accepted_evidence": accepted,
    }
    res12 = await generate_hypotheses_node(state12)
    dur12 = (time.time() - start) * 1000
    hypos = res12.get("hypotheses", [])
    primary_h = res12.get("selected_hypothesis", {})
    pass12 = len(hypos) > 0 and primary_h.get("hypothesis_id") == "HYP-1"
    results.append(("12. generate_hypotheses_node", pass12, dur12, f"HypothesesCount={len(hypos)}, Primary={primary_h.get('hypothesis_id')}"))

    # 13. evaluate_hypotheses_node
    start = time.time()
    state13: InvestigationState = {
        "selected_hypothesis": primary_h,
        "confidence": 94.5,
        "accepted_evidence": accepted,
        "investigation_iterations": 0,
    }
    res13 = await evaluate_hypotheses_node(state13)
    dur13 = (time.time() - start) * 1000
    eval_dict = res13.get("hypothesis_evaluation", {})
    is_suff = res13.get("evidence_sufficient")
    inv_iter = res13.get("investigation_iterations")
    pass13 = is_suff is True and inv_iter == 1 and eval_dict.get("evidence_sufficient") is True
    results.append(("13. evaluate_hypotheses_node", pass13, dur13, f"Sufficient={is_suff}, InvIter={inv_iter}"))

    # 14. generate_final_report_node
    start = time.time()
    state14: InvestigationState = {
        "incident_id": "INC-1001",
        "incident_description": "Checkout service failing with 504 Gateway Timeouts",
        "services": ["checkout-service"],
        "selected_hypothesis": primary_h,
        "confidence": 94.5,
        "evidence_analysis": ev_synth,
        "accepted_evidence": accepted,
        "reranked_documents": reranked,
    }
    res14 = await generate_final_report_node(state14)
    dur14 = (time.time() - start) * 1000
    final_rep = res14.get("final_report", {})
    pass14 = isinstance(final_rep, dict) and final_rep.get("confidence") == 94.5 and "root_cause" in final_rep
    results.append(("14. generate_final_report_node", pass14, dur14, f"FinalRCAConf={final_rep.get('confidence')}%, RootCause={final_rep.get('root_cause')[:40]}..."))

    # SUMMARY TABLE
    print("\n============================================================")
    print("INDIVIDUAL NODE ISOLATED TESTING SUMMARY REPORT — 14 NODES")
    print("============================================================")
    print(f"{'Node Name':<38} | {'Status':<6} | {'Latency':<8} | {'Output Validation'}")
    print("-" * 95)
    all_passed = True
    total_time = 0.0
    for name, p, d, details in results:
        status_str = "PASS" if p else "FAIL"
        if not p:
            all_passed = False
        total_time += d
        print(f"{name:<38} | {status_str:<6} | {d:>6.2f}ms | {details}")

    print("-" * 95)
    print(f"TOTAL NODES TESTED: {len(results)} | PASSED: {sum(1 for _, p, _, _ in results if p)} / {len(results)} | TOTAL LATENCY: {total_time:.2f}ms")
    print(f"OVERALL STATUS: {'ALL 14 NODES OPERATIONAL & PASSED' if all_passed else 'SOME NODES FAILED'}")
    print("============================================================")

    return all_passed

if __name__ == "__main__":
    asyncio.run(run_individual_node_tests())
