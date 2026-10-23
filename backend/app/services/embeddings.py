"""Embedding and vector search service."""
import numpy as np
from typing import List, Optional, Tuple
from sentence_transformers import SentenceTransformer
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating and managing text embeddings."""
    
    _model: Optional[SentenceTransformer] = None
    _model_name: Optional[str] = None
    
    @classmethod
    def get_model(cls, model_name: Optional[str] = None) -> SentenceTransformer:
        """Get or load the sentence transformer model."""
        model_name = model_name or settings.embedding_model
        
        if cls._model is None or cls._model_name != model_name:
            logger.info(f"Loading embedding model: {model_name}")
            cls._model = SentenceTransformer(model_name)
            cls._model_name = model_name
        
        return cls._model
    
    @classmethod
    def encode(cls, texts: List[str], model_name: Optional[str] = None) -> np.ndarray:
        """Encode texts to normalized embeddings."""
        model = cls.get_model(model_name)
        return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    
    @classmethod
    def encode_single(cls, text: str, model_name: Optional[str] = None) -> np.ndarray:
        """Encode a single text to embedding."""
        return cls.encode([text], model_name)[0]
    
    @classmethod
    def cosine_similarity(cls, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two normalized vectors."""
        return float(np.dot(a, b))
    
    @classmethod
    def batch_similarity(cls, query: np.ndarray, candidates: np.ndarray) -> np.ndarray:
        """Compute similarities between query and multiple candidates."""
        return candidates @ query
    
    @classmethod
    def top_k(cls, query: np.ndarray, candidates: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        """Get top-k most similar candidates."""
        scores = cls.batch_similarity(query, candidates)
        top_indices = np.argpartition(scores, -k)[-k:]
        top_indices = top_indices[np.argsort(scores[top_indices])][::-1]
        return top_indices, scores[top_indices]


def create_job_embedding_text(job_data: dict) -> str:
    """Create text representation of job for embedding."""
    parts = [
        job_data.get("title", ""),
        job_data.get("company", ""),
        job_data.get("description", ""),
    ]
    skills = job_data.get("skills", [])
    if skills:
        parts.append("Skills: " + ", ".join(skills))
    return " ".join(parts)


def create_query_embedding_text(query: str, filters: dict) -> str:
    """Create text representation of search query for embedding."""
    parts = [query]
    if filters.get("location"):
        parts.append(f"Location: {filters['location']}")
    if filters.get("seniority"):
        parts.append(f"Seniority: {filters['seniority']}")
    if filters.get("employment_type"):
        parts.append(f"Type: {filters['employment_type']}")
    return " ".join(parts)