import logging
from typing import List, Dict, Any

logger = logging.getLogger("langgraph_agent.tools.incident_tools")

async def get_incident_summary_tool(incident_id: str) -> Dict[str, Any]:
    """Helper tool for incident summary metadata."""
    return {
        "incident_id": incident_id,
        "status": "Active",
        "severity": "High",
        "summary": "Application checkout latency is 10x slower than normal due to lock contention."
    }
