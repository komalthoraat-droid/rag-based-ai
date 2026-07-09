from src.retrieval.vector_search import vector_retriever
from src.retrieval.graph_retrieval import graph_retriever
from src.retrieval.sql_retrieval import sql_retriever
from src.core.router import router
from src.monitoring.logger import logger

class HybridRetriever:
    def __init__(self):
        self.retrievers = {
            "SEMANTIC": vector_retriever,
            "GRAPH_RELATION": graph_retriever,
            "STRUCTURAL": sql_retriever
        }

    def search(self, query):
        route = router.classify(query)
        logger.info(f"Routing query to: {route}")
        
        retriever = self.retrievers.get(route, vector_retriever)
        results = retriever.retrieve(query)
        
        return results, route

hybrid_retriever = HybridRetriever()
