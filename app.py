from src.helper import *
import streamlit as st
from dotenv import load_dotenv
import os
import random
from src.registration import *
from src.mongo import *


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')



st.set_page_config(
    page_title="Chat with Gita",
    page_icon=":om:",
    layout="centered",
    initial_sidebar_state="auto",
)

def main():
    inject_css()
    menu = ["Home", "Login", "Register","Chat"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Home":
        krishna_image = "assets/krishna_image.jpg"
        st.subheader("Chat with Gita")
        st.image(krishna_image, caption="Lord Krishna", use_column_width=True)

        # Introduction and description
        st.write("""
        Welcome to "Chat with Gita" – a unique chatbot that helps you find answers to your life problems 
        through the teachings of Lord Krishna as conveyed in the Bhagavad Gita.
        
        Here, you can ask questions about various aspects of your life and receive guidance and wisdom 
        inspired by the timeless scripture.
        """)

        # Instructions
        st.header("How to Use")
        st.write("""
        1. Enter your question about any life problem or concern you have.
        2. Click on the "Get Answer" button.
        3. Receive a thoughtful and insightful response inspired by the Bhagavad Gita.
        """)

    elif choice == "Login":
        st.subheader("Login Section")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')

        if st.button("Login"):
            if login_user(username, password):
                st.success("Logged In as {}".format(username))
            else:
                st.warning("Incorrect Username/Password")

    elif choice == "Register":
        st.subheader("Create New Account")

        name = st.text_input('name')
        age = st.number_input('age', min_value=0, max_value=100, step=1)
        gender = st.selectbox('gender',('Male','Female'))
        email = st.text_input("email")
        new_password = st.text_input("Password", type='password')

        if st.button("Register"):
            registration_status = register_user(email, new_password, name, age, gender)
            if registration_status == "User registered successfully":
                st.success("You have successfully created an account")
            else:
                st.warning(registration_status)
    
    elif choice=='Chat':
        st.header("Chat with Shri Krishna 🌟")    
        st.subheader("Seeking Guidance for Life's Questions")
        col1, col3 = st.columns([1, 1])

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

        # User input
        user_question = st.text_input("Ask a Question to Shri Krishna")
        if st.button("Submit"):
            with st.spinner('Wait for it...'):
                if user_question:
                    response = user_input(user_question)
                    store_in_mongodb(user_question, response)

if __name__ == "__main__":
    main()