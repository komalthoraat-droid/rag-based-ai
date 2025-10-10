import requests
import os
import json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib

def create_embedding(text_list):
    r=requests.post("http://localhost:11434/api/embed",json={
        "model":"mxbai-embed-large",
        "input":text_list
    })
    embedding=r.json()['embeddings']
    return embedding
   
jsons=os.listdir("newjsons")
my_dicts=[]
chunk_id=0
for json_file in jsons:
    with open(f"newjsons/{json_file}") as f:
        content = json.load(f)
    print(f"creating embedding for {json_file}")
    embeddings=create_embedding([c['text'] for c in content['chunks']])

    for i,chunk in enumerate(content['chunks']):
        chunk['chunk_id']=chunk_id
        chunk['embedding']=embeddings[i]
        chunk_id +=1
        my_dicts.append(chunk)
    

df = pd.DataFrame.from_records(my_dicts)
# print(df)
joblib.dump(df,'embeddings.joblib')
# incoming_query = input("ask a quetion:")
# question_embedding=create_embedding([incoming_query])[0]
# # print(question_embedding)
# similarities=cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
# print(similarities)
# top_results=3
# max_indx=similarities.argsort()[::-1][0:top_results]
# print(max_indx)
# new_df=df.loc[max_indx]
# print(new_df[["title","number","text"]])




  
