FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy langgraph investigation agent module and backend source code
COPY langgraph_investigation_agent/ ./langgraph_investigation_agent/
COPY backend/ .

# Set PYTHONPATH to include /app so langgraph_investigation_agent is accessible
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose FastAPI port
EXPOSE 8000

# Run FastAPI backend with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
