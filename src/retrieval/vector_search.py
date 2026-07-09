import pandas as pd
import numpy as np
import joblib
import requests
from sklearn.metrics.pairwise import cosine_similarity
from src.monitoring.logger import logger

class VectorRetriever:
    def __init__(self, index_path='embeddings.joblib'):
        self.index_path = index_path
        self.df = self._load_index()

    def _load_index(self):
        try:
            return joblib.load(self.index_path)
        except Exception as e:
            logger.error(f"Failed to load vector index: {e}")
            return None

    def _create_embedding(self, text):
        try:
            r = requests.post("http://localhost:11434/api/embed", json={
                "model": "mxbai-embed-large",
                "input": [text]
            })
            return r.json()['embeddings'][0]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def retrieve(self, query, top_k=5):
        if self.df is None:
            return []
            
        query_embedding = self._create_embedding(query)
        if query_embedding is None:
            return []
            
        similarities = cosine_similarity(
            np.vstack(self.df['embedding']), 
            [query_embedding]
        ).flatten()
        
        top_indices = similarities.argsort()[::-1][:top_k]
        results = self.df.iloc[top_indices].to_dict(orient='records')
        
        # Add score to results
        for i, idx in enumerate(top_indices):
            results[i]['score'] = float(similarities[idx])
            
        return results

vector_retriever = VectorRetriever()
