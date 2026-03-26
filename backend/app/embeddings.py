"""
Vector embeddings service for semantic similarity and search.
Uses Sentence-BERT (HuggingFace) for efficient embeddings.
"""
import numpy as np
from typing import List, Dict, Tuple
import os
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer, util
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    logger.warning("sentence_transformers not installed; embeddings will be disabled")


class EmbeddingService:
    """
    Manages text embeddings for semantic search and similarity.
    Uses cached model for efficiency.
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: HuggingFace model identifier
                - "all-MiniLM-L6-v2" (fast, 384d)
                - "all-mpnet-base-v2" (slower, 768d)
                - "multi-qa-mpnet-base-dot-v1" (specialized for similarity)
        """
        self.model_name = model_name
        self.model = None
        self.dimension = None
        
        if EMBEDDING_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name)
                self.dimension = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded embedding model: {model_name} ({self.dimension}d)")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                EMBEDDING_AVAILABLE = False
    
    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector (list of floats)
        """
        if not EMBEDDING_AVAILABLE or self.model is None:
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return None
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embedding vectors
        """
        if not EMBEDDING_AVAILABLE or self.model is None:
            return [None] * len(texts)
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [None] * len(texts)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1, text2: Input texts
            
        Returns:
            Similarity score (0-1)
        """
        if not EMBEDDING_AVAILABLE or self.model is None:
            return 0.0
        
        try:
            emb1 = self.model.encode(text1, convert_to_numpy=True)
            emb2 = self.model.encode(text2, convert_to_numpy=True)
            return float(util.cos_sim(emb1, emb2)[0][0])
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            return 0.0
    
    def semantic_search(
        self,
        query: str,
        corpus: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, float]]:
        """
        Find most similar texts in corpus to query.
        
        Args:
            query: Search query
            corpus: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples
        """
        if not EMBEDDING_AVAILABLE or self.model is None:
            return []
        
        try:
            query_emb = self.model.encode(query, convert_to_numpy=True)
            corpus_embs = self.model.encode(corpus, convert_to_numpy=True)
            
            hits = util.semantic_search(query_emb, corpus_embs, top_k=min(top_k, len(corpus)))
            return [(hit['corpus_id'], hit['score']) for hit in hits[0]]
        except Exception as e:
            logger.error(f"Semantic search failed: {e}")
            return []


# Global instance
embedding_service = EmbeddingService()
