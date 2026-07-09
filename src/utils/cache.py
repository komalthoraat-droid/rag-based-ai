import json
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.retrieval.vector_search import vector_retriever
from src.monitoring.logger import logger

class SemanticCache:
    def __init__(self, threshold=0.92):
        self.threshold = threshold
        self.cache_file = "cache.json"
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "r") as f:
                return json.load(f)
        return []

    def _save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.cache, f)

    def get(self, query):
        if not self.cache:
            return None
            
        query_embedding = vector_retriever._create_embedding(query)
        cache_embeddings = [np.array(item['embedding']) for item in self.cache]
        
        similarities = cosine_similarity([query_embedding], cache_embeddings).flatten()
        max_idx = similarities.argmax()
        
        if similarities[max_idx] >= self.threshold:
            logger.info(f"Semantic cache hit (score: {similarities[max_idx]})")
            return self.cache[max_idx]['answer']
            
        return None

    def set(self, query, answer):
        embedding = vector_retriever._create_embedding(query)
        self.cache.append({
            "query": query,
            "answer": answer,
            "embedding": embedding if isinstance(embedding, list) else embedding.tolist()
        })
        self._save_cache()
        logger.info("New query/answer pair cached")

semantic_cache = SemanticCache()
