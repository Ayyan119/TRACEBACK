import pytest
from app.tools.log_tools import query_incident_logs
from app.tools.tool_schemas import ALL_AGENT_TOOLS

@pytest.mark.asyncio
async def test_query_incident_logs_tool():
    res = await query_incident_logs(
        project_id="art-gallary",
        service="checkout-service",
        level="ERROR",
        limit=10,
    )
    assert res["success"] is True
    assert "records" in res
    assert res["query"]["service"] == "checkout-service"
    assert res["query"]["limit"] == 10

def test_tool_schemas_registration():
    assert len(ALL_AGENT_TOOLS) > 0
    assert ALL_AGENT_TOOLS[0].name == "query_incident_logs"
