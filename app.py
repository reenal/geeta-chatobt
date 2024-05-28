from src.helper import *
import streamlit as st
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

# text = get_file_text()
# text_chunks = get_text_chunks(text)
# db = get_vector_store(text_chunks=text_chunks)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

def inject_css():
    custom_css = """
    <style>
    :root {
        --background-light: #ffffff;
        --background-dark: #1e1e1e;
        --text-light: #000000;
        --text-dark: #ffffff;
        --highlight-light: #f1f1f1;
        --highlight-dark: #333333;
    }

    @media (prefers-color-scheme: light) {
        .reply-box, .shlok-box, .meaning-box, .example-box {
            background-color: var(--background-light);
            color: var(--text-light);
            border: 1px solid var(--highlight-light);
        }
    }

    @media (prefers-color-scheme: dark) {
        .reply-box, .shlok-box, .meaning-box, .example-box {
            background-color: var(--background-dark);
            color: var(--text-dark);
            border: 1px solid var(--highlight-dark);
        }
    }

    .box {
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def user_input(user_question):
    print(user_question)

    # Load the vector store
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    
    # Perform a similarity search and retrieve relevant documents as context
    docs = new_db.similarity_search(user_question)
    
    # Get the conversational chain
    chain = get_conversational_chain()
    
    # Run the chain with the retrieved context and the user's question
    response = chain.invoke({"context": docs, "question": user_question})
    
    parts = response.strip().split("\n\n")
    reply = parts[0]
    shlok = parts[1].replace("Shlok:  ", "")
    meaning = parts[2].replace("Meaning: ", "")
    example = parts[3].replace("Example: ", "")
    

    # Create a container to display the response
    with st.container():
        st.markdown(f'<div class="box reply-box">{reply}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box shlok-box">{shlok}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box meaning-box">{meaning}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="box example-box">{example}</div>', unsafe_allow_html=True)
  
        
        st.write("Generationg img for you Arjun...")
        
        # img_prompt = text_to_img_prompt(response=response)
        
        image = img_generator(img_prompt=example)
        
        st.image(image)

    # Predict the next question
    next_question = predict_next_question(user_question)
    
    # Display the predicted next question in the sidebar
    st.sidebar.header("Predicted Next Question")
    st.sidebar.write(next_question)
    
    
def main():
    inject_css()
    # st.set_page_config("Chat Lord Krishna")
    st.header("Chat with Bhagwan Shri Krishna 🌟")
    st.subheader("Seeking Guidance for Life's Questions")

    # User input
    import random
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
    
    user_question = st.text_input("Ask a Question to Bhagwan Krishna")
    if st.button("Submit"):
        with st.spinner('Wait for it...'):
            if user_question:
                user_input(user_question)

if __name__ == "__main__":
    main()