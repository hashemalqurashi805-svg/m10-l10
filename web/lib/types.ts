// TypeScript interfaces — must mirror api/models.py exactly.

// Entities extracted from the NLP processing
export interface Entity {
  text: string;
  label: string;
  start: number;
  end: number;
}

// Request to /extract
export interface ExtractRequest {
  text: string;
}

// Response from /extract
export interface ExtractResponse {
  entities: Entity[];
}

// Request to /kg/query
export interface KGRequest {
  question: string;
}

// Response from /kg/query
export interface KGResponse {
  cypher: string;
  rows: any[]; // Neo4j records as JSON objects
  count: number;
}

// Citation used within RAGResponse
export interface Citation {
  chunk_id: string;
  score: number;
}

// Request to /rag/answer
export interface RAGRequest {
  question: string;
  k?: number;
}

// Response from /rag/answer
export interface RAGResponse {
  answer: string;
  citations: Citation[];
  confidence: number;
}