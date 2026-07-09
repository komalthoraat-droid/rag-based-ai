import logging
import os
import time
import json
from datetime import datetime

# Configure logging directory
LOG_DIR = os.path.join(os.getcwd(), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Main logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "system.log")),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RAG-Production")

class RAGMonitor:
    def __init__(self):
        self.query_log_path = os.path.join(LOG_DIR, "queries.jsonl")

    def log_query(self, query, route, context_count, answer, latency, evaluation=None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "route": route,
            "context_count": context_count,
            "answer_preview": answer[:100] + "..." if len(answer) > 100 else answer,
            "latency_ms": round(latency * 1000, 2),
            "evaluation": evaluation
        }
        
        with open(self.query_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        logger.info(f"Query processed: {query[:50]}... | Route: {route} | Latency: {log_entry['latency_ms']}ms")

monitor = RAGMonitor()
