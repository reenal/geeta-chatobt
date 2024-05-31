from src.helper import *
import streamlit as st
from dotenv import load_dotenv
import os
import random

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

   
def main():
    inject_css()
    # st.set_page_config("Chat Lord Krishna")
    st.header("Chat with Shri Krishna 🌟")
    st.subheader("Seeking Guidance for Life's Questions")
    col1, col3 = st.columns([1, 1])

# Add a button to the rightmost column
    with col1:
        ques =  [   'Am I good enough to achieve my goals?',
                    'Am I capable of building and maintaining meaningful relationships?',   
                    'Do I have what it takes to succeed in life?']
   
        selected_ques = random.choice(ques)
        if st.button('Generate Random Question'):
            st.write(selected_ques)
            user_question = selected_ques

            with st.spinner('Wait for it...'):
                if user_question:
                    user_input(user_question)
                
    with col3:
        if st.button('Create New Embeedings'):
            st.write('Creating new embeddings...')
            embeddings = create_embedding()
            st.write('Embeddings created successfully!')

    # User input
    user_question = st.text_input("Ask a Question to Shri Krishna")
    if st.button("Submit"):
        with st.spinner('Wait for it...'):
            if user_question:
                user_input(user_question)

if __name__ == "__main__":
    main()
