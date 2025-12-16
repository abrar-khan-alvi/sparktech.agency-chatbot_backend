import os
import google.generativeai as genai
import faiss
import numpy as np
from django.conf import settings


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


index = None
stored_chunks = []

def load_knowledge_base():

    global index, stored_chunks
    
    file_path = os.path.join(settings.BASE_DIR, 'data', 'knowledge_base.txt')
    
    if not os.path.exists(file_path):
        print("CRITICAL: Knowledge base file not found!")
        return


    with open(file_path, 'r') as f:
        text = f.read()
        
    stored_chunks = [chunk.strip() for chunk in text.split('\n\n') if chunk.strip()]

    if not stored_chunks:
        return

    result = genai.embed_content(
        model="gemini-embedding-001",
        content=stored_chunks,
        task_type="retrieval_document"
    )
    
    embeddings = np.array(result['embedding'], dtype='float32')

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    print("Success: Knowledge Base Loaded into Memory!")

def generate_rag_response(user_query):
    global index, stored_chunks

    if index is None:
        load_knowledge_base()
    query_result = genai.embed_content(
        model="gemini-embedding-001",
        content=user_query,
        task_type="retrieval_query"
    )
    query_vector = np.array([query_result['embedding']], dtype='float32')

    D, I = index.search(query_vector, k=1) 
    match_index = I[0][0]
    
    if match_index == -1:
        context = "No specific info found."
    else:
        context = stored_chunks[match_index]

    prompt = f"""
    You are a helpful customer support assistant.
    Use the following Context to answer the User's Question.
    If the answer is not in the Context, say "I don't have that information."

    Context: {context}

    User's Question: {user_query}
    """

    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    
    return response.text