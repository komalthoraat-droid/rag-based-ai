import pandas as pd
import numpy as np
import joblib
from src.core.generator import generator
from src.retrieval.vector_search import vector_retriever
from src.monitoring.logger import logger

class HierarchicalIndexer:
    def __init__(self, data_path='embeddings.joblib'):
        self.data_path = data_path
        self.df = joblib.load(data_path)

    def generate_summaries(self, chunk_group_size=5):
        """Recursively summarize chunks to create a tree (RAPTOR style)."""
        logger.info(f"Generating summaries for hierarchical indexing (RAPTOR style)")
        
        summaries = []
        for i in range(0, len(self.df), chunk_group_size):
            group = self.df.iloc[i:i+chunk_group_size]
            combined_text = " ".join(group['text'].values)
            
            prompt = f"Summarize the following video transcript segment concisely into one paragraph focus on core concepts taught: {combined_text}"
            summary_text = generator.generate(prompt)
            
            # Embed the summary
            summary_embedding = vector_retriever._create_embedding(summary_text)
            
            summaries.append({
                "text": summary_text,
                "embedding": summary_embedding,
                "type": "summary",
                "source_chunks": list(group.index)
            })
            
        summary_df = pd.DataFrame(summaries)
        return summary_df

    def build_multi_view_index(self):
        """Combine raw chunks with summaries and keywords for multi-vector retrieval."""
        logger.info("Building multi-view index...")
        
        multi_view_data = []
        for idx, row in self.df.iterrows():
            # 1. Base Chunk View
            multi_view_data.append(row.to_dict())
            
            # 2. Keyword View (hypothetical extraction)
            keywords = generator.generate(f"Extract 5 technical keywords from: {row['text']}").split(',')
            keyword_text = f"Keywords: {' '.join(keywords)}"
            keyword_embedding = vector_retriever._create_embedding(keyword_text)
            
            multi_view_data.append({
                "text": keyword_text,
                "embedding": keyword_embedding,
                "type": "keyword",
                "original_chunk_id": idx
            })
            
        multi_view_df = pd.DataFrame(multi_view_data)
        # Persistence
        joblib.dump(multi_view_df, "multi_view_index.joblib")
        logger.info("Multi-view index built and saved to multi_view_index.joblib")

hierarchical_indexer = HierarchicalIndexer()
if __name__ == "__main__":
    hierarchical_indexer.build_multi_view_index()
