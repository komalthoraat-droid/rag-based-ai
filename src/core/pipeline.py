import time
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import requests

from src.core.generator import generator
from src.core.memory import memory
from src.utils.cache import semantic_cache
from src.monitoring.logger import monitor, logger

def create_embedding(text_list):
    r = requests.post("http://localhost:11434/api/embed", json={
        "model": "mxbai-embed-large",
        "input": text_list
    })
    embedding = r.json()['embeddings']
    return embedding

def build_context_prompt(query, session_id="default"):
    # Load the real video subtitle embeddings!
    try:
        df = joblib.load('embeddings.joblib')
    except Exception as e:
        return f"Error loading embeddings: {e}"

    # Generate an embedding for the user's query
    question_embedding = create_embedding([query])[0]
    
    # Calculate similarity with all subtitle chunks
    similarities = cosine_similarity(np.vstack(df['embedding']), [question_embedding]).flatten()
    
    # Extract the top 5 most relevant results
    top_results = 5
    max_indx = similarities.argsort()[::-1][0:top_results]
    new_df = df.loc[max_indx]
    
    # Bring in previous context from the session if necessary
    history_context = memory.format_history(session_id)

    # Recreate the exact prompt logic desired by the user
    prompt = f'''I am teaching web development in my sigma web development course.here are video subtitle chunks containing video title,video number,start time in seconds,end time in seconds,the text at that time:

{new_df[["title","number","start","end","text"]].to_json(orient="records")}
-------------------------------------
Conversation History:
{history_context}
-------------------------------------
"{query}"
user asked this question related to the video chunks,you have to answer in a human way(dont mention the above format it just for you) where and how much content is tought in which video(in which video and at what timestamp)and guide the user to go to that particular video.if user asks unrelated questions,tell him that you can only answer questions related to the course
'''
    return prompt

class AgenticRAGPipeline:
    def __init__(self):
        pass

    def run(self, query, session_id="default"):
        start_time = time.time()
        
        # 1. Semantic Cache Check
        cached_answer = semantic_cache.get(query)
        if cached_answer:
            latency = time.time() - start_time
            return {"answer": cached_answer, "source": "cache", "latency": latency}
        
        # 2. Build our real context prompt using embeddings.joblib
        prompt = build_context_prompt(query, session_id)
        
        if prompt.startswith("Error"):
            return {
                "answer": f"System Error: {prompt}",
                "source": "error",
                "hops": 0,
                "latency": 0
            }

        # 3. Generate Answer against Llama 3.2
        answer = generator.generate(prompt)
        
        # 4. Update Memory
        memory.add_message(session_id, "user", query)
        memory.add_message(session_id, "assistant", answer)
        
        # 5. Cache result
        semantic_cache.set(query, answer)
        
        latency = time.time() - start_time
        monitor.log_query(query, "TRUE_RAG", 1, answer, latency)
        
        return {
            "answer": answer,
            "source": "embeddings_joblib",
            "hops": 1,
            "latency": latency
        }

    def run_stream(self, query, session_id="default"):
        prompt = build_context_prompt(query, session_id)
        
        if prompt.startswith("Error"):
            yield prompt
            return

        # Immediate update
        memory.add_message(session_id, "user", query)
        
        full_answer = ""
        for token in generator.generate(prompt, stream=True):
            full_answer += token
            yield token
            
        memory.add_message(session_id, "assistant", full_answer)

rag_pipeline = AgenticRAGPipeline()
