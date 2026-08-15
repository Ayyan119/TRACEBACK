DOCUMENT_ANALYSIS_PROMPT = """
You are an expert SRE telemetry analyst. Analyze the following incident evidence document for relevance to a production incident.

Incident Description:
{description}

Document Title: {title}
Document Content:
{content}

Determine if this document contains technical clues, symptoms, or root causes relevant to the reported incident.
Produce a structured output with relevant=True/False, summary, key points, affected services, and root cause hints.
"""

TOOL_REASONING_PROMPT = """
You are an AI Root-Cause Investigation Agent analyzing a production incident.

Incident Description:
{description}

Accepted Evidence Items:
{accepted_evidence_summary}

Log Query History:
{log_query_history_summary}

Current Tool Iteration: {tool_iterations} / 5

Decide whether you need to query PostgreSQL structured logs for more evidence (e.g. searching specific service logs, error levels, timestamps, or keywords), or if you already have sufficient log telemetry to proceed.
"""

INCIDENT_ANALYZER_PROMPT = """
You are a Self-RAG AI Incident Analyzer. Evaluate whether external knowledge base runbooks or previous incident history retrieval is required to determine the root cause of this incident.

Incident Description:
{description}

Accepted Evidence:
{accepted_evidence_summary}

Retrieved Logs:
{retrieved_logs_summary}

If the cause is self-evident from the logs and evidence, set retrieval_required = false.
If runbook guidance or architecture documentation is needed, set retrieval_required = true and provide search queries.
"""

RERANKER_PROMPT = """
You are an AI SRE Reranker. Evaluate the following retrieved knowledge chunk/previous incident for relevance to the current incident investigation.

Incident Context:
{description}

Retrieved Item:
{item_content}

Score relevance from 0.0 to 1.0. Set keep = True only if this item provides genuine value for diagnosing the incident.
"""

EVIDENCE_ANALYSIS_PROMPT = """
You are an SRE Root Cause Lead. Synthesize all gathered telemetry, logs, accepted evidence, and knowledge runbooks into a structured evidence analysis.

Incident Description:
{description}

All Evidence Items:
{accepted_evidence_summary}

Structured Logs:
{retrieved_logs_summary}

Reranked Knowledge Runbooks:
{reranked_docs_summary}

Produce a detailed evidence analysis detailing what happened, when it happened, affected service, symptoms, and potential causes.
"""

HYPOTHESIS_GENERATION_PROMPT = """
You are a Principal Reliability Architect. Based on the synthesized evidence analysis, generate a ranked set of hypotheses explaining the root cause of the incident.

Evidence Analysis:
{evidence_analysis_summary}

Rank hypotheses from highest to lowest confidence. Specify supporting evidence IDs, likely root cause, and recommended next check.
"""
