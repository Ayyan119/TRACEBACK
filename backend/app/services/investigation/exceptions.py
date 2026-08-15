class InvestigationAdapterError(Exception):
    """Base exception for all Investigation Adapter errors."""
    def __init__(self, message: str, details: str = ""):
        super().__init__(message)
        self.message = message
        self.details = details


class MissingLogReferenceError(InvestigationAdapterError):
    """Raised when mandatory incident log reference is absent or invalid."""
    pass


class InvalidInputError(InvestigationAdapterError):
    """Raised when adapter input payload validation fails."""
    pass


class GraphExecutionError(InvestigationAdapterError):
    """Raised when LangGraph graph execution fails or returns malformed state."""
    pass
