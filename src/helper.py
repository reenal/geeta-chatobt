from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.prompt import *
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import os
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')


def get_file_text():
    text = ""
    pdf_reader = PdfReader('data/Bhagavad-Gita As It Is.pdf')
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return text_splitter.split_text(text)


def create_embedding():
    text = get_file_text()
    text_chunks = get_text_chunks(text)
    db = get_vector_store(text_chunks=text_chunks)
    return db

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Function to load or create a vector store from the text chunks
def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    return vector_store


def get_conversational_chain():
    prompt_template = base_prompt

    # Define the language model
    model = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro-latest", temperature=0.3)

    # Create a prompt template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    
    # Create the conversational chain
    chain = prompt | model | StrOutputParser()
    return chain


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
 
       
        st.write("Generationg img for you...")
       
        # img_prompt = text_to_img_prompt(response=response)
       
        image = img_generator(img_prompt=example)
       
        st.image(image)

    # Predict the next question
    next_question = predict_next_question(user_question)
   
    # Display the predicted next question in the sidebar
    st.sidebar.header("Predicted Next Question")
    st.sidebar.write(next_question)
    
    return response

# Function to predict the next question
def predict_next_question(user_question):
    # Create a prompt template for predicting the next question
    prompt_template = """
    Based on the user's question: {user_question}, predict the next question the user might ask.
    """

    # Define the language model
    model = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro-latest", temperature=0.3)
    
    # Create the prompt and LLM chain
    prompt = PromptTemplate(template=prompt_template, input_variables=["user_question"])
    
    chain = prompt | model | StrOutputParser()
    
    # Use the chain to predict the next question
    next_question = chain.invoke(user_question)
    
    return next_question


def text_to_img_prompt(response):
    # Create a prompt template for predicting the next question
    prompt_template = """
    Based on the response extract the Example text from the: {response}, write a prompt convert text-to-image generation llm diffusion model
    """

    # Define the language model
    model = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro-latest", temperature=0.3)
    
    # Create the prompt and LLM chain
    prompt = PromptTemplate(template=prompt_template, input_variables=["response"])
    
    chain = prompt | model | StrOutputParser()
    
    # Use the chain to predict the next question
    text_to_img = chain.invoke(response)
    
    return text_to_img


def img_generator(img_prompt):
    import requests

    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.content
    image_bytes = query({
        "inputs": img_prompt,
    })
    # You can access the image with PIL.Image for example
    import io
    from PIL import Image
    image = Image.open(io.BytesIO(image_bytes))
    
    return image


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

