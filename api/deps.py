"""FastAPI dependency-injection helpers."""
from fastapi import Request

async def get_session(request: Request):
    """Yield a short-lived Neo4j session from the process-scoped driver."""
    driver = request.app.state.neo4j_driver
    with driver.session() as session:
        yield session

def get_weaviate(request: Request):
    """Return the process-scoped Weaviate client."""
    return request.app.state.weaviate_client

def get_generator(request: Request):
    """Return the process-scoped flan-t5-base generator."""
    return request.app.state.generator

def get_nlp(request: Request):
    """Return the process-scoped spaCy pipeline."""
    return request.app.state.nlp

def get_embedder(request: Request):
    """Return the process-scoped sentence-transformers embedder."""
    return request.app.state.embedder