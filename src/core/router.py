from src.core.generator import generator
from src.monitoring.logger import logger

class QueryRouter:
    def __init__(self):
        self.system_prompt = """
        You are a query router for a RAG system. Your goal is to classify the user's query into one of the following categories:
        1. SEMANTIC: General questions that require semantic search (e.g., "how to use react", "explain the course content").
        2. GRAPH_RELATION: Questions about relationships between entities (e.g., "what is the connection between video 1 and video 5", "how does topic X lead to topic Y").
        3. STRUCTURAL: Numerical or metadata-based questions (e.g., "how many videos are over 10 minutes long", "list videos from last month").
        
        Respond with ONLY the category name: SEMANTIC, GRAPH_RELATION, or STRUCTURAL.
        """

    def classify(self, query):
        logger.info(f"Classifying query: {query}")
        result = generator.generate(query, system_prompt=self.system_prompt).strip().upper()
        
        # Fallback and validation
        if "GRAPH" in result:
            return "GRAPH_RELATION"
        if "STRUCT" in result:
            return "STRUCTURAL"
        return "SEMANTIC"

router = QueryRouter()
