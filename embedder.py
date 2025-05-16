import os
import logging
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings

# === Load API Key ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Logging Setup ===
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('app.log')
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# === Custom Google Embedding Wrapper ===
class GoogleGenAIEmbeddings(Embeddings):
    def __init__(self, model="models/embedding-001", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.api_key)
        logger.info("Google GenAI Embeddings initialized.")

    def embed_documents(self, texts):
        try:
            return [
                genai.embed_content(content=text, model=self.model, task_type="retrieval_document")["embedding"]
                for text in texts
            ]
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return []

    def embed_query(self, text):
        try:
            return genai.embed_content(content=text, model=self.model, task_type="retrieval_query")["embedding"]
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return None

# === Document Loader ===
def load_documents():
    try:
        docs = []
        knowledge_folder = "knowledge/"
        for file in os.listdir(knowledge_folder):
            path = os.path.join(knowledge_folder, file)
            if file.endswith(".pdf"):
                with open(path, "rb") as f:
                    reader = PdfReader(f)
                    text = "\n".join(
                        page.extract_text() for page in reader.pages if page.extract_text()
                    )
                    docs.append(Document(page_content=text, metadata={"source": file}))
            elif file.endswith(".txt"):
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    docs.append(Document(page_content=text, metadata={"source": file}))
        logger.info(f"Loaded {len(docs)} documents from /knowledge/")
        return docs
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        return []

# === Embedding + Indexing Pipeline ===
def load_and_index_knowledge():
    try:
        logger.info("Starting knowledge indexing process...")
        raw_docs = load_documents()
        if not raw_docs:
            logger.warning("No documents found to process.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
        chunks = splitter.split_documents(raw_docs)
        logger.info(f"Split into {len(chunks)} chunks.")

        embeddings = GoogleGenAIEmbeddings()
        vectorstore = FAISS.from_documents(chunks, embeddings)

        vectorstore.save_local("verne_vectorstore")
        logger.info("Vector store saved as 'verne_vectorstore'")
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")

# === Vector Store Loader ===
def load_vectorstore():
    try:
        logger.info("Loading vector store...")
        embeddings = GoogleGenAIEmbeddings()
        return FAISS.load_local(
            "verne_vectorstore",
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        logger.error(f"Failed to load vector store: {e}")
        return None
