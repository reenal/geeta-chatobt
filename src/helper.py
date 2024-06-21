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
from src.logger import *
import requests
import io
from PIL import Image
from langchain_community.document_loaders import PyPDFDirectoryLoader
from src.session import *

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
GoogleGenerativeAIEmbeddings.api_key = api_key
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')
HuggingFace_API_KEY = os.getenv('HuggingFace_API_KEY')

def read_documents_for_multiple_pdfs():
    logging.info('read data directory all pdfs')
    loader = PyPDFDirectoryLoader("data/")
    docs = loader.load()
    return docs


def get_text_chunks_for_multiple_pdfs(text):
    logging.info('chunking process started for the extracted text')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    logging.info('chucking process done successfully')
    split_text = text_splitter.split_documents(text)
    return split_text


def get_vector_store_for_multiple_pdfs(text_chunks):
    logging.info("start storing embeeding into vector db")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    logging.info("storing embeeding into vector db done successfully in local folder")
    return vector_store


def create_embedding_for_multiple_pdfs():
    logging.info('embedding process started')
    text = read_documents_for_multiple_pdfs()
    text_chunks = get_text_chunks_for_multiple_pdfs(text)
    db = get_vector_store_for_multiple_pdfs(text_chunks=text_chunks)
    logging.info('embedding process done successfully')
    return db


def get_file_text():
    logging.info('read the pdf dat from the data folder')
    text = ""
    pdf_reader = PdfReader('data/Bhagavad-Gita As It Is.pdf')
    for page in pdf_reader.pages:
        text += page.extract_text()
    logging.info('extract text from pdf successfully')
    return text

# Function to split text into chunks
def get_text_chunks(text):
    logging.info('chunking process started for the extracted text')
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    logging.info('chucking process done successfully')
    return text_splitter.split_text(text)


def create_embedding():
    logging.info('embedding process started')
    text = get_file_text()
    text_chunks = get_text_chunks(text)
    db = get_vector_store(text_chunks=text_chunks)
    logging.info('embedding process done successfully')
    return db

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# Function to load or create a vector store from the text chunks
def get_vector_store(text_chunks):
    logging.info("start storing embeeding into vector db")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")
    logging.info("storing embeeding into vector db done successfully in local folder")
    return vector_store


def get_conversational_chain():
    logging.info("import the base prompt from promt template")
    prompt_template = base_prompt
    
    # Define the language model
    model = ChatGoogleGenerativeAI(model="models/gemini-1.5-pro-latest", temperature=0.3)
    logging.info('import successfully the  llm model')

    # Create a prompt template
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    logging.info('prompt load successfully')
    
    # Create the conversational chain
    chain = prompt | model | StrOutputParser()
    logging.info('conversational chain load successfully')
    return chain


def user_input(user_question):
    print(user_question)
    logging.info('user input question received')
    # Load the vector store
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    logging.info('load vector database for successfully')
    # Perform a similarity search and retrieve relevant documents as context
    docs = new_db.similarity_search(user_question)
    logging.info('similarity search done successfully')
    # Get the conversational chain
    chain = get_conversational_chain()
    logging.info('conversational chain initialize')
    # Run the chain with the retrieved context and the user's question
    response = chain.invoke({"context": docs, "question": user_question})
    logging.info('llm model provide the response successfully')
    print(response)
    
    try:
        parts = response.strip().split("\n\n")
        reply = parts[0]
        shlok = parts[1].replace("Shlok:  ", "Shlok:  ")
        meaning = parts[2].replace("Meaning: ", "Meaning:")
        example = parts[3].replace("Example: ", "Example:")
        logging.info("split the response in serperate variable for css container output")
        inject_css()

    

        # Create a container to display the response
        with st.container():
            st.markdown(f'<div class="box reply-box">{reply}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box shlok-box">{shlok}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box meaning-box">{meaning}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="box example-box">{example}</div>', unsafe_allow_html=True)
            
    except Exception as e:
        logging.error(f"{e} so we print in simple format without any container")
        st.write(response)

    st.write("Generationg img for you...")
       
        # img_prompt = text_to_img_prompt(response=response)
    logging.info("image generation started using huggingface api ")
    try:
        image = img_generator(img_prompt=example)
        logging.info('Image generated successfully')
        st.image(image)
    except Exception as e:
        logging.warning('Primary image generation failed, attempting alternative method')
        logging.error(e)
        try:
            image = img_generator_2(img_prompt=example)
            logging.info('Image generated from alternative model successfully')
            st.image(image)
        except Exception as e:
            st.error("Sorry for the inconvenience, but the server is down due to heavy traffic.")
            logging.error(e)
    

    # Predict the next question
    next_question = predict_next_question(user_question)
    logging.info('next question predict successfully')
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


def query_image_generation(api_url, headers, payload):
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error during API request: {e}")
        return None

def img_generator(img_prompt):
    logging.info("Image generator function started")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": 'Bearer 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'}

    logging.info("Sending request to image generation API")
    image_bytes = query_image_generation(API_URL, headers, {"inputs": img_prompt})
    
    if image_bytes:
        logging.info("Received image response")
        try:
            image = Image.open(io.BytesIO(image_bytes))
            logging.info("Image successfully generated")
            return image
        except IOError as e:
            logging.error(f"Image generation failed: {e}")
    else:
        logging.error("No image bytes received from API")

    return None

def img_generator_2(img_prompt):
    logging.info("Image generator function started")
    
    API_URL = "https://api-inference.huggingface.co/models/Corcelio/mobius"
    headers = {"Authorization": 'Bearer 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'}

    logging.info("Sending request to image generation API")
    image_bytes = query_image_generation(API_URL, headers, {"inputs": img_prompt})
    
    if image_bytes:
        logging.info("Received image response")
        try:
            image = Image.open(io.BytesIO(image_bytes))
            logging.info("Image successfully generated")
            return image
        except IOError as e:
            logging.error(f"Image generation failed: {e}")
    else:
        logging.error("No image bytes received from API")

    return None


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


# Function to inject custom CSS and HTML for the header
def display_logout_button():
    st.markdown("""
        <style>
        .header {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            position: fixed;
            top: 50px;
            right: 20px;
            background: none;
            padding: 0;
            z-index: 1000;
        }
        .header button {
            padding: 10px 20px;
            background-color: #007BFF;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 5px;
        }
        .header button:hover {
            background-color: #0056b3;
        }
        </style>
        <div class="header">
            <form action="/?" method="get">
                <button name="logout">Logout</button>
            </form>
        </div>
    """, unsafe_allow_html=True)
