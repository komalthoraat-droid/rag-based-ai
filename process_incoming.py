import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import requests


# from openai import OpenAI
# from config import api_key
# client=OpenAI(api_key=api_key)



def create_embedding(text_list):
    r=requests.post("http://localhost:11434/api/embed",json={
        "model":"mxbai-embed-large",
        "input":text_list
    })
    embedding=r.json()['embeddings']
    return embedding

def inference(prompt):
     r= requests.post("http://localhost:11434/api/generate",json={
        "model":"llama3.2",
        "prompt":prompt,
        "stream":False
     }) 
     response = r.json()
     print(response)
     return response

# def inference_openai(prompt):
#      response=client.responses.create(
#      model="gpt-5",
#      input=prompt
#      )
#      return response.output_text


        

df=joblib.load('embeddings.joblib')

incoming_query = input("ask a quetion:")
question_embedding=create_embedding([incoming_query])[0]
# print(question_embedding)
similarities=cosine_similarity(np.vstack(df['embedding']),[question_embedding]).flatten()
# print(similarities)
top_results=5
max_indx=similarities.argsort()[::-1][0:top_results]
# print(max_indx)
new_df=df.loc[max_indx]
# print(new_df[["title","number","text"]])


prompt=f'''I am teaching web development in my sigma web development course.here are video subtitle chunks containing video title,video number,start time in seconds,end time in seconds,the text at that time:

{new_df[["title","number","start","end","text"]].to_json(orient="records")}
-------------------------------------
"{incoming_query}"
user asked this question related to the video chunks,you have to answer in a human way(dont mention the above format it just for you) where and how much content is tought in which video(in which video and at what timestamp)and guide the user to go to that particular video.if user asks unrelated questions,tell him that you  can only answer questions related to the course
'''

with open ("prompt.txt","w") as f:
     f.write(prompt)

response=inference(prompt)['response']
print(response)

# response=inference_openai(prompt)

with open("response.txt","w") as f:
     f.write(response)
# for index,item in new_df.iterrows():
#     print(index,item['title'],item['number'],item['text'],item['start'],item['end'])


