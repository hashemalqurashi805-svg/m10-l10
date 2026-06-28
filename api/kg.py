"""Wraps the vendored W9B deterministic NL→Cypher mapper."""
from .w9b_mapper.mapper import map_question
from .w9b_mapper.errors import UnsupportedQueryError  # re-export

def wrap_kg_query(question: str):
    """Map a natural-language question to (cypher, params).
    
    Inputs:
        question — natural-language question (non-empty, <= 500 chars).
    Returns:
        Tuple (cypher: str, params: dict) suitable for `session.run`.
    Raises:
        UnsupportedQueryError — if the question does not match any
        supported pattern.
    """
    # استدعاء دالة map_question من المكتبة الموردة
    cypher, params = map_question(question)
    return cypher, params