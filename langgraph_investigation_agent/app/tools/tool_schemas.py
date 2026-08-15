from langchain_core.tools import StructuredTool
from app.models.structured_models import LogQueryInput
from app.tools.log_tools import query_incident_logs

log_query_tool = StructuredTool.from_function(
    coroutine=query_incident_logs,
    name="query_incident_logs",
    description="Queries PostgreSQL structured log records for an incident/project using filters like service, level, keyword, or timestamps.",
    args_schema=LogQueryInput,
)

ALL_AGENT_TOOLS = [log_query_tool]
