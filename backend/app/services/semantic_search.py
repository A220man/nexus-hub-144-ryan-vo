import json
import numpy as np
from typing import List, Optional, Tuple, Dict, Any
from sentence_transformers import SentenceTransformer
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SemanticSearchService:
    _model: Optional[SentenceTransformer] = None

    @classmethod
    def get_model(cls) -> SentenceTransformer:
        if cls._model is None:
            logger.info(f"Loading embedding model: {settings.embedding_model}")
            cls._model = SentenceTransformer(settings.embedding_model)
        return cls._model

    @classmethod
    def encode(cls, texts: List[str]) -> np.ndarray:
        model = cls.get_model()
        return model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    @classmethod
    def encode_single(cls, text: str) -> np.ndarray:
        return cls.encode([text])[0]

    @classmethod
    def cosine_similarity(cls, a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    @classmethod
    def compute_match_score(cls, query_embedding: np.ndarray, job_embedding: List[float]) -> float:
        if not job_embedding:
            return 0.0
        job_emb = np.array(job_embedding, dtype=np.float32)
        if np.linalg.norm(job_emb) == 0:
            return 0.0
        return cls.cosine_similarity(query_embedding, job_emb)

    @classmethod
    def generate_match_explanation(cls, query: str, job: Dict[str, Any], score: float) -> str:
        """Generate a human-readable explanation for why this job matches the query."""
        if score >= 0.75:
            strength = "strong"
        elif score >= 0.5:
            strength = "moderate"
        elif score >= 0.3:
            strength = "weak"
        else:
            strength = "minimal"

        skills = job.get("skills", [])
        skill_match = ""
        if skills:
            skill_list = ", ".join(skills[:5])
            skill_match = f" Relevant skills: {skill_list}."

        location = job.get("location", "")
        location_str = f" Location: {location}." if location else ""

        return (
            f"This job has a {strength} semantic match ({score:.0%}) to your search '{query}'."
            f"{skill_match}{location_str}"
        )


class DictionaryService:
    """Service for dictionary coverage checking (skills, roles, industries)."""

    SKILL_ALIASES = {
        "k8s": "kubernetes",
        "kubernetes": "kubernetes",
        "reactjs": "react",
        "react.js": "react",
        "vuejs": "vue",
        "vue.js": "vue",
        "nodejs": "node.js",
        "node.js": "node.js",
        "python": "python",
        "py": "python",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "dl": "deep learning",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "aws": "amazon web services",
        "gcp": "google cloud platform",
        "ci/cd": "continuous integration",
        "cicd": "continuous integration",
    }

    ROLE_ALIASES = {
        "swe": "software engineer",
        "software engineer": "software engineer",
        "backend engineer": "backend engineer",
        "frontend engineer": "frontend engineer",
        "fullstack": "full stack engineer",
        "full stack": "full stack engineer",
        "ml engineer": "machine learning engineer",
        "data scientist": "data scientist",
        "devops": "devops engineer",
        "sre": "site reliability engineer",
    }

    INDUSTRY_ALIASES = {
        "fintech": "financial technology",
        "edtech": "education technology",
        "healthtech": "health technology",
        "saas": "software as a service",
        "ecommerce": "electronic commerce",
        "crypto": "cryptocurrency",
        "web3": "web3",
        "ai": "artificial intelligence",
    }

    CANONICAL_SKILLS = set(SKILL_ALIASES.values()) | {
        "typescript", "javascript", "go", "rust", "java", "c++", "c#",
        "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
        "docker", "kubernetes", "terraform", "ansible", "github actions",
        "gitlab ci", "jenkins", "aws", "gcp", "azure",
        "machine learning", "deep learning", "nlp", "computer vision",
        "pytorch", "tensorflow", "jax", "scikit-learn", "pandas", "numpy",
        "transformers", "hugging face", "langchain", "llamaindex",
        "rest api", "graphql", "grpc", "microservices", "distributed systems",
    }

    CANONICAL_ROLES = set(ROLE_ALIASES.values()) | {
        "software engineer", "backend engineer", "frontend engineer",
        "full stack engineer", "machine learning engineer", "data scientist",
        "devops engineer", "site reliability engineer", "engineering manager",
        "tech lead", "principal engineer", "staff engineer",
        "product manager", "designer", "data engineer",
    }

    CANONICAL_INDUSTRIES = set(INDUSTRY_ALIASES.values()) | {
        "financial technology", "education technology", "health technology",
        "software as a service", "electronic commerce", "cryptocurrency",
        "web3", "artificial intelligence", "biotechnology", "cybersecurity",
        "autonomous vehicles", "robotics", "gaming", "media streaming",
    }

    @classmethod
    def normalize_term(cls, term: str, kind: str) -> str:
        term = term.strip().lower()
        aliases = {
            "skill": cls.SKILL_ALIASES,
            "role": cls.ROLE_ALIASES,
            "industry": cls.INDUSTRY_ALIASES,
        }.get(kind, {})
        return aliases.get(term, term)

    @classmethod
    def check_coverage(cls, term: str, kind: str) -> Dict[str, Any]:
        """Check if a term exists in the dictionary.
        Returns: {"type": "canonical"|"alias"|"miss", "canonical": str, "display": str}
        """
        normalized = cls.normalize_term(term, kind)

        canonicals = {
            "skill": cls.CANONICAL_SKILLS,
            "role": cls.CANONICAL_ROLES,
            "industry": cls.CANONICAL_INDUSTRIES,
        }.get(kind, set())

        # Check if original term is canonical
        if term.lower().strip() in canonicals:
            return {
                "type": "canonical",
                "canonical": term.lower().strip(),
                "display": term.strip(),
            }

        # Check if normalized term is canonical (alias hit)
        if normalized in canonicals and normalized != term.lower().strip():
            return {
                "type": "alias",
                "canonical": normalized,
                "display": normalized,
            }

        # Miss
        return {
            "type": "miss",
            "canonical": None,
            "display": None,
        }