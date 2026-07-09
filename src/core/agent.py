from src.retrieval.hybrid_retriever import hybrid_retriever
from src.core.generator import generator
from src.monitoring.logger import logger

class ReasoningAgent:
    def __init__(self, max_hops=3):
        self.max_hops = max_hops

    def run(self, original_query, memory_context=""):
        logger.info(f"Starting agentic reasoning loop for query: {original_query}")
        
        current_context = []
        conversation_state = f"Original Query: {original_query}\n{memory_context}"
        
        for hop in range(self.max_hops):
            logger.info(f"Reasoning hop {hop + 1}/{self.max_hops}")
            
            # Step 1: Decision - Do we have enough information or need more?
            prompt = f"""
            System: You are an agentic RAG assistant. Your current goal is to answer the user's query.
            {conversation_state}
            
            Current Context:
            {current_context}
            
            Based on the information above, do you need more information from the database or can you answer now?
            If you need more information, respond with "SEARCH: <new search query>".
            If you have enough information, respond with "ANSWER: <your comprehensive answer>".
            """
            
            decision = generator.generate(prompt)
            
            if decision.startswith("SEARCH:"):
                search_query = decision.replace("SEARCH:", "").strip()
                logger.info(f"Agent decided to search again: {search_query}")
                
                # Retrieve more context
                new_contexts, _ = hybrid_retriever.search(search_query)
                current_context.extend(new_contexts)
                
                # Prevent retrieval bloat - keep top N
                current_context = current_context[-10:] 
            elif decision.startswith("ANSWER:"):
                answer = decision.replace("ANSWER:", "").strip()
                logger.info("Agent found enough information to answer.")
                return answer, hop + 1
            else:
                # Fallback if LLM format is weird
                logger.warning(f"Unexpected agent decision format: {decision}")
                break
                
        # Final fallback - generate answer from what we found
        final_answer = generator.generate(f"Using this context, answer the query: {original_query}\n\nContext: {current_context}")
        return final_answer, self.max_hops

reasoning_agent = ReasoningAgent()
