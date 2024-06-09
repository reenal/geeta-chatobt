from src.helper import *
import streamlit as st
from dotenv import load_dotenv
import os
import warnings
warnings.filterwarnings('ignore')


from datasets import Dataset
import time
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    context_utilization
)
from langchain_openai import ChatOpenAI




load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key


def user_input(user_question):

    # Load the vector store
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # Perform a similarity search and retrieve relevant documents as context
    docs = new_db.similarity_search(user_question)
    
    # Get the conversational chain
    chain = get_conversational_chain()
    
    # Run the chain with the retrieved context and the user's question
    response = chain.invoke({"context": docs, "question": user_question})
    
    return response


def start_engine():
    text = get_file_text()
    text_chunks = get_text_chunks(text)
    db = get_vector_store(text_chunks=text_chunks)
    time.sleep(120)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    retriever = db.as_retriever(search_kwargs={"k": 3})
    return retriever

def question_ask(retriever, questions):
    
    answers = []
    contexts = []
    
    for query in questions:
        print(query)
        answers.append(user_input(query))
        contexts.append([docs.page_content for docs in retriever.get_relevant_documents(query)])
        time.sleep(15)
        
        
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
    }
    dataset = Dataset.from_dict(data)
    
    return dataset


def load_llm():
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.3)
    return llm

def start_evaluation(dataset,llm):
    result = evaluate(
        dataset = dataset, 
        metrics=[
            context_utilization,
            faithfulness,
            answer_relevancy,
        ],
        llm=llm,   ## replace here your llm model for evaluation answer
        embeddings=embeddings,
        raise_exceptions=False
    )

    result_df = result.to_pandas()
    result_df.to_csv('evaluation_result_openai_10.csv')
    
    return result_df


def app(questions):
    print("Application Started Working")
    print('Starting....')
    retriever = start_engine()
    print('Retriver Created Successfully')
    print('Stage 2 Ongoing....')
    dataset = question_ask(retriever, questions=questions)
    print('Dataset Created Successfully')
    print('Stage 3 Ongoing....')
    llm = load_llm() # you can change here llm which we want to use for evaluation
    print('LLM Created Successfully')
    print('Stage 4 Ongoing....')
    result_df = start_evaluation(dataset=dataset, llm=llm)
    print('CSV file Created Successfully')
    print('Stage 5 Done Successfully....')
    return result_df

### start running application from here

questions = [
    'what is the meaning of true happiness?',
    'how can I find inner peace in a chaotic world?',
    'what is the essence of love?',
    'how can I balance my personal and professional life?',
    'what is the significance of meditation in daily life?',
    'how can I cultivate gratitude and contentment?',
    'what is the purpose of human existence?',
    'how can I overcome the fear of failure?',
    'what is the impact of positive thinking on success?',
    'how can I achieve self-actualization and fulfill my potential?'
]

print(app(questions=questions))




