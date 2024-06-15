import streamlit as st
import random

from src.helper import *
from src.registration import *
from src.mongo import *
from src.session import *

if 'first_name' in st.session_state:
        st.write(f"Welcome, {st.session_state['first_name']}!")
        
if 'session_id' in st.session_state:
        session_id = st.session_state['session_id']
else:
    st.warning("You need to log in first.")
    st.experimental_set_query_params(page="pages/login")




# Display user info and logout button at the top
if 'first_name' in st.session_state:
    display_logout_button()
else:
    st.warning("You need to log in first.")
    st.experimental_set_query_params(page="pages/login")
    st.stop()

if 'session_id' in st.session_state:
    session_id = st.session_state['session_id']
else:
    st.warning("You need to log in first.")
    st.experimental_set_query_params(page="pages/login")

st.header("Chat with Shri Krishna 🌟")

st.subheader(f"Hi, {st.session_state['first_name']}!, Seeking Guidance for Life's Questions")
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
                # Log user question
                log_action(session_id, 'question', {'question': user_question, 'response': response})
                log_action(session_id, 'click', {'element': 'button#Generate Random Question'})
                store_in_mongodb(user_question, response)

with col3:
    if st.button('Create New Embeddings'):
        st.write('Creating new embeddings...')
        embeddings = create_embedding_for_multiple_pdfs()
        log_action(session_id, 'click', {'element': 'button#Create New Embeddings'})
        st.write('Embeddings created successfully!')

user_question = st.text_input("Ask a Question to Shri Krishna")
if st.button("Submit"):
    with st.spinner('Wait for it...'):
        if user_question:
            response = user_input(user_question)
            log_action(session_id, 'question', {'question': user_question, 'response': response})
            log_action(session_id, 'click', {'element': 'button#Submit'})
            store_in_mongodb(user_question, response)
