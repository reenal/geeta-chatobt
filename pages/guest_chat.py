import streamlit as st
import random

from src.helper import *
from src.registration import *
from src.mongo import *

    
st.header("Chat with Shri Krishna 🌟")
  
st.subheader(f"Hi, Guest! Seeking Guidance for Life's Questions")
col1, col3 = st.columns(2)

with col1:
    ques = [
        'Am I good enough to achieve my goals?',
        'Am I capable of building and maintaining meaningful relationships?',   
        'Do I have what it takes to succeed in life?'
    ]

    selected_ques = random.choice(ques)
    if st.button('Generate Random Question'):
        st.write(selected_ques)
        user_question = selected_ques

        with st.spinner('Wait for it...'):
            if user_question:
                response = user_input(user_question)
                store_in_mongodb(user_question, response)

with col3:
    if st.button('Create New Embeddings'):
        st.write('Creating new embeddings...')
        embeddings = create_embedding()
        st.write('Embeddings created successfully!')

user_question = st.text_input("Ask a Question to Shri Krishna")
if st.button("Submit"):
    with st.spinner('Wait for it...'):
        if user_question:
            response = user_input(user_question)
            store_in_mongodb(user_question, response)
