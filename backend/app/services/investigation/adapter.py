import os
import sys
import logging
import asyncio
from typing import Optional, Callable, Any, Dict

agent_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "langgraph_investigation_agent"))

from app.services.investigation.schemas import InvestigationInput, InvestigationResult
from app.services.investigation.input_adapter import InputAdapter
from app.services.investigation.output_adapter import OutputAdapter
from app.services.investigation.exceptions import (
    InvestigationAdapterError,
    GraphExecutionError,
)

logger = logging.getLogger("traceback.services.investigation.adapter")


def _load_agent_graph():
    """Safely loads and compiles the LangGraph investigation workflow."""
    if agent_root not in sys.path:
        sys.path.insert(0, agent_root)

    # Evict cached backend 'app' module entries so agent 'app' imports correctly
    for k in list(sys.modules.keys()):
        if k == "app" or k.startswith("app."):
            del sys.modules[k]

    import app.graph.workflow as agent_workflow
    return agent_workflow.build_investigation_graph()


class InvestigationAdapter:
    """TRACEBACK Investigation Adapter bridging backend APIs and LangGraph Agent workflow."""

    def __init__(self, graph_runner: Optional[Callable[[Dict[str, Any]], Any]] = None):
        """
        Initializes the adapter.
        :param graph_runner: Optional custom graph runner or mock graph for testing dependency injection.
        """
        self._graph_runner = graph_runner

    def _get_graph_runner(self) -> Callable[[Dict[str, Any]], Any]:
        """Lazy loads and compiles the real LangGraph workflow if no mock graph runner was injected."""
        if self._graph_runner is not None:
            return self._graph_runner

        try:
            graph = _load_agent_graph()

            async def default_runner(state: Dict[str, Any]) -> Dict[str, Any]:
                return await graph.ainvoke(state)

            self._graph_runner = default_runner
            return default_runner
        except Exception as e:
            logger.error(f"Failed to load LangGraph investigation graph: {e}", exc_info=True)
            raise GraphExecutionError(f"Failed to initialize LangGraph investigation workflow engine: {e}") from e

    async def arun(self, input_data: InvestigationInput) -> InvestigationResult:
        """Asynchronously executes the investigation workflow for the given API input."""
        logger.info(f"InvestigationAdapter.arun starting for incident '{input_data.incident_id}'")
        
        # 1. Translate API Input -> InvestigationState
        initial_state = InputAdapter.to_investigation_state(input_data)
        
        # 2. Retrieve Graph Runner
        runner = self._get_graph_runner()
        
        # 3. Invoke LangGraph Engine
        try:
            if asyncio.iscoroutinefunction(runner):
                final_state = await runner(initial_state)
            else:
                res = runner(initial_state)
                if asyncio.iscoroutine(res):
                    final_state = await res
                else:
                    final_state = res
        except InvestigationAdapterError:
            raise
        except Exception as e:
            logger.error(f"Graph execution failed during invocation: {e}", exc_info=True)
            raise GraphExecutionError(f"LangGraph investigation engine failed for incident '{input_data.incident_id}'.") from e

        # 4. Translate Final State -> InvestigationResult
        result = OutputAdapter.to_investigation_result(final_state)
        logger.info(f"InvestigationAdapter.arun completed successfully for incident '{input_data.incident_id}'")
        return result

    def run(self, input_data: InvestigationInput) -> InvestigationResult:
        """Synchronously executes the investigation workflow for the given API input."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            return loop.run_until_complete(self.arun(input_data))
        else:
            return loop.run_until_complete(self.arun(input_data))
