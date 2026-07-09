from src.core.generator import generator
from src.monitoring.logger import logger

class EnhancedRewriter:
    def rewrite(self, query, history=""):
        """Generate multiple query variations for better retrieval coverage."""
        logger.info(f"Performing enhanced multi-query rewrite for: {query}")
        
        prompt = f"""
        {history}
        User Query: "{query}"
        
        Generate 3 distinct search queries that capture different aspects of the user's intent. 
        Focus on technical keywords and variations. 
        Output each query on a new line. Do not include numbers or bullet points.
        """
        
        result = generator.generate(prompt).strip()
        queries = [q.strip() for q in result.split('\n') if q.strip()]
        
        # Always include the original query
        if query not in queries:
            queries.insert(0, query)
            
        logger.info(f"Generated {len(queries)} search variations")
        return queries[:4]

query_rewriter = EnhancedRewriter()
