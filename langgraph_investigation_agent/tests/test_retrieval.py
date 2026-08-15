import pytest
from app.retrieval.qdrant_retriever import retrieve_knowledge_chunks
from app.retrieval.previous_incidents import retrieve_previous_incidents
from app.retrieval.reranker import rerank_retrieved_items

@pytest.mark.asyncio
async def test_retrieve_knowledge_chunks():
    chunks = await retrieve_knowledge_chunks("art-gallary", ["postgres connection pool"], top_k=8)
    assert isinstance(chunks, list)
    assert len(chunks) <= 8

@pytest.mark.asyncio
async def test_retrieve_previous_incidents():
    incidents = await retrieve_previous_incidents("art-gallary", ["database lock contention"], top_k=2)
    assert isinstance(incidents, list)
    assert len(incidents) <= 2

@pytest.mark.asyncio
async def test_reranker():
    chunks = [{"id": "c1", "title": "Runbook", "content": "PostgreSQL connection pool max_connections", "score": 0.85}]
    prev = [{"id": "p1", "title": "Lock Outage", "score": 0.90, "historical_payload": {"title": "Lock Outage", "root_cause_summary": "Unindexed row lock"}}]
    
    reranked = await rerank_retrieved_items("PostgreSQL database lock contention", chunks, prev)
    assert len(reranked) == 2
    assert reranked[0]["keep"] is True
