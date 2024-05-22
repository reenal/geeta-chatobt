from pypdf import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from src.prompt import *
from langchain.chains import LLMChain



def get_file_text():
    text = ""
    pdf_reader = PdfReader('data/Bhagavad-Gita As It Is.pdf')
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to split text into chunks
def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

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
    return LLMChain(llm=model, prompt=prompt)

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
    chain = LLMChain(llm=model, prompt=prompt)
    
    # Use the chain to predict the next question
    next_question = chain.run(user_question)
    
    return next_question
