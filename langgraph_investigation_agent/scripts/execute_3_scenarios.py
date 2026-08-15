import os
import sys
import time
import json
import asyncio
import logging

# Ensure root folder is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.graph.workflow import build_investigation_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


SCENARIO_1_INPUT = {
    "investigation_id": "inv-scenario-1-db-lock",
    "project_id": "art-gallary",
    "incident_id": "INC-2001",
    "incident_description": "Checkout service returning HTTP 504 Gateway Timeouts during flash sale launch. PostgreSQL active connections reached 100/100 limit due to unindexed row locks on the orders table.",
    "incident_log_reference": {
        "file_name": "checkout_app.log",
        "file_size_bytes": 1258291,
        "log_type": "telemetry"
    },
    "services": ["checkout-service", "postgresql_db"],
    "service_metadata": {
        "checkout-service": {"environment": "production", "framework": "FastAPI", "db": "postgresql_db"},
        "postgresql_db": {"max_connections": 100, "active_connections": 100}
    },
    "incident_documents": [
        {
            "name": "PostgreSQL_Pool_Diagnostics.pdf",
            "content": "Diagnostics report showing connection pool max_connections=100 limit reached. Long transactions on orders table holding exclusive row locks."
        },
        {
            "name": "Employee_Onboarding_Guide.pdf",
            "content": "Welcome to art-gallary engineering workspace onboarding notes."
        }
    ],
    "incident_images": [
        {
            "title": "Grafana_504_Latency_Spike.png",
            "file_url": "/tmp/grafana_504_error.png"
        },
        {
            "title": "Company_Logo.jpg",
            "file_url": "/tmp/logo.jpg"
        }
    ]
}


SCENARIO_2_INPUT = {
    "investigation_id": "inv-scenario-2-redis-eviction",
    "project_id": "art-gallary",
    "incident_id": "INC-2002",
    "incident_description": "User authentication and session verification service returning HTTP 500 Internal Server Errors. Redis cluster memory hit 100% maxmemory limit causing blocking key evictions and 2000ms latency spikes.",
    "incident_log_reference": {
        "file_name": "auth_session.log",
        "file_size_bytes": 870400,
        "log_type": "telemetry"
    },
    "services": ["auth-service", "redis_cache"],
    "service_metadata": {
        "auth-service": {"environment": "production", "cache": "redis_cache"},
        "redis_cache": {"maxmemory": "2GB", "eviction_policy": "allkeys-lru"}
    },
    "incident_documents": [
        {
            "name": "Redis_Eviction_SOP.docx",
            "content": "Standard operating procedure for Redis memory eviction. When memory usage hits 100%, blocking sync evictions introduce P95 latency spikes."
        }
    ],
    "incident_images": [
        {
            "title": "Redis_Memory_Grafana.png",
            "file_url": "/tmp/redis_grafana_error.png"
        }
    ]
}


SCENARIO_3_INPUT = {
    "investigation_id": "inv-scenario-3-k8s-oom",
    "project_id": "art-gallary",
    "incident_id": "INC-2003",
    "incident_description": "Payment gateway microservice pods continuously restarting in CrashLoopBackOff state. Worker memory limit of 512MB exceeded due to unclosed HTTP client connection leak in payment processor.",
    "incident_log_reference": {
        "file_name": "payment_gateway_k8s.log",
        "file_size_bytes": 2202010,
        "log_type": "telemetry"
    },
    "services": ["payment-service", "k8s_cluster"],
    "service_metadata": {
        "payment-service": {"environment": "production", "container_memory_limit": "512Mi"},
        "k8s_cluster": {"namespace": "payments", "restart_policy": "Always"}
    },
    "incident_documents": [
        {
            "name": "Kubernetes_OOMKilled_Policy.pdf",
            "content": "Kubernetes pod memory limits policy. Exit code 137 indicates OOMKilled state triggered by cgroup memory limit overflow."
        }
    ],
    "incident_images": [
        {
            "title": "K8s_Pod_Status_Console.png",
            "file_url": "/tmp/k8s_crashloop_error.png"
        }
    ]
}


async def run_all_scenarios():
    graph = build_investigation_graph()
    scenarios = [
        ("SCENARIO 1: PostgreSQL Connection Pool & Lock Contention", SCENARIO_1_INPUT),
        ("SCENARIO 2: Redis Cache Memory Eviction & Latency Spike", SCENARIO_2_INPUT),
        ("SCENARIO 3: Kubernetes Pod OOMKilled & Container CrashLoop", SCENARIO_3_INPUT),
    ]

    all_reports = []

    print("============================================================")
    print("EMPIRICAL EXECUTION OF 3 COMPLETE SYNTHETIC SCENARIOS")
    print("============================================================")

    for title, input_payload in scenarios:
        print(f"\n▶ Executing {title}...")
        start_time = time.time()
        
        final_state = await graph.ainvoke(input_payload)
        duration_ms = (time.time() - start_time) * 1000

        report = {
            "title": title,
            "investigation_id": final_state.get("investigation_id"),
            "incident_id": final_state.get("incident_id"),
            "duration_ms": round(duration_ms, 2),
            "inputs": {
                "description": input_payload.get("incident_description"),
                "log_file": input_payload.get("incident_log_reference"),
                "documents_count": len(input_payload.get("incident_documents", [])),
                "images_count": len(input_payload.get("incident_images", [])),
                "services": input_payload.get("services"),
            },
            "execution_trace": final_state.get("execution_trace", []),
            "accepted_evidence": final_state.get("accepted_evidence", []),
            "rejected_evidence": final_state.get("rejected_evidence", []),
            "retrieved_logs_count": len(final_state.get("retrieved_logs", [])),
            "retrieval_decision": {
                "required": final_state.get("retrieval_required"),
                "reason": final_state.get("retrieval_reason"),
                "search_queries": final_state.get("search_queries", []),
            },
            "reranked_documents_count": len(final_state.get("reranked_documents", [])),
            "evidence_analysis": final_state.get("evidence_analysis"),
            "hypotheses": final_state.get("hypotheses", []),
            "selected_hypothesis": final_state.get("selected_hypothesis"),
            "confidence": final_state.get("confidence"),
        }
        all_reports.append(report)

        print(f"✔ Completed in {duration_ms:.2f}ms")
        print(f"  Primary Hypothesis: {final_state.get('selected_hypothesis', {}).get('title')}")
        print(f"  Confidence Score:   {final_state.get('confidence')}%")

    # Save JSON results
    reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "reports"))
    os.makedirs(reports_dir, exist_ok=True)
    json_path = os.path.join(reports_dir, "scenario_test_results.json")
    with open(json_path, "w") as f:
        json.dump(all_reports, f, indent=2)
    print(f"\nSaved raw JSON scenario execution results to {json_path}")

    return all_reports

if __name__ == "__main__":
    asyncio.run(run_all_scenarios())
