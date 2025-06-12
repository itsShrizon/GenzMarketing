import os
import json
import hashlib
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

def compute_file_hash(file_path):
    """Compute a hash for the contents of a file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def create_vector_database(json_file_path):
    """Create a vector database using ChromaDB with OpenAI embeddings."""
    persist_directory = "db"

    # Initialize OpenAI embeddings
    openai_embeddings = OpenAIEmbeddings()

    # Check if the database already exists and if the data has changed
    if os.path.exists(persist_directory) and os.path.exists(json_file_path):
        new_hash = compute_file_hash(json_file_path)
        hash_file = os.path.join(persist_directory, "data_hash.txt")
        if os.path.exists(hash_file):
            with open(hash_file, 'r') as f:
                existing_hash = f.read()
            if existing_hash == new_hash:
                print("No changes detected in data. Using existing embeddings.")
                return Chroma(persist_directory=persist_directory, embedding_function=openai_embeddings)

    # Load data from the JSON file
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Create Document objects from the data
    documents = [
        Document(page_content=item["content"], metadata={"title": item["title"], "url": item["url"]})
        for item in data
    ]

    # Split documents into manageable chunks
    text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=40)
    docs = text_splitter.split_documents(documents)    # Create and persist the Chroma vector database
    vectordb = Chroma.from_documents(documents=docs, embedding=openai_embeddings, persist_directory=persist_directory)
    vectordb.persist()

    # Save the new hash of the data
    new_hash = compute_file_hash(json_file_path)
    with open(os.path.join(persist_directory, "data_hash.txt"), 'w') as f:
        f.write(new_hash)

    return vectordb

def setup_retriever(vector_database):
    """Setup a retriever using the vector database."""
    return vector_database.as_retriever(search_kwargs={"k": 3})

def build_chatbot(retriever):
    """Build a chatbot using OpenAI's GPT-4o model."""
    # Ensure the OPENAI_API_KEY is set in the environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OpenAI API key not found. Please set it in your environment variables.")

    # Initialize the ChatOpenAI model
    llm = ChatOpenAI(
        model="gpt-4o", 
        temperature=0
    )

    # Create a RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

    def answer_with_sources(query):
        # Define a dynamic prompt
        dynamic_prompt = (
            "You are an intelligent assistant that adjusts responses dynamically based on the user's query intent. "
            "If the query is about general information, respond with a paragraph. "
            "If the query is about listing items, respond with a clear and formatted list. "
            "Use a professional and user-friendly tone."
        )
        full_query = f"{dynamic_prompt}\n\nQuery: {query}"

        # Get the response from the QA chain
        response = qa_chain.run(full_query)
        documents = retriever.get_relevant_documents(query)

        # Extract source URLs from the retrieved documents
        all_urls = [doc.metadata.get("url", "No URL provided") for doc in documents]
        unique_url = next(iter(all_urls), "No URL provided")

        return {
            "result": response,
            "sources": [unique_url],
        }

    return answer_with_sources
