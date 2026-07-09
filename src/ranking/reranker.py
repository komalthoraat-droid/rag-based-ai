from src.core.generator import generator
from src.monitoring.logger import logger

class Reranker:
    def rerank(self, query, contexts, top_n=3):
        """Use LLM to rerank retrieved contexts for relevance."""
        logger.info(f"Reranking {len(contexts)} contexts for query: {query}")
        
        if not contexts:
            return []
            
        context_text = "\n".join([f"[{i}] {c.get('text', c)}" for i, c in enumerate(contexts)])
        
        prompt = f"""
        Given the user query: "{query}"
        And the following retrieved contexts:
        {context_text}
        
        Rank these contexts from most relevant to least relevant to answering the query.
        Return ONLY a comma-separated list of indices (e.g., 2,0,1).
        """
        
        try:
            ranking_str = generator.generate(prompt).strip()
            indices = [int(idx.strip()) for idx in ranking_str.split(',') if idx.strip().isdigit()]
            
            reranked = [contexts[i] for i in indices if i < len(contexts)]
            return reranked[:top_n]
        except Exception as e:
            logger.error(f"Reranking error: {e}")
            return contexts[:top_n]

reranker = Reranker()
