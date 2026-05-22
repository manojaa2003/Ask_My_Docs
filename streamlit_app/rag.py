from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

COLLECTION_NAME = "Pdf_store"

VECTOR_STORE_DIR = (
    Path(__file__).parent / "resources/vector_store"
)

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

llm = None
vector_store = None


def initialize_components():

    global llm, vector_store

    if llm is None:

        llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=500
        )

    if vector_store is None:

        embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=str(VECTOR_STORE_DIR),
        )


def process_pdfs(pdfs):

    initialize_components()

    vector_store.reset_collection()

    all_docs = []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    for pdf in pdfs:

        print(f"Loading PDF: {pdf}")

        loader = PyPDFLoader(pdf)

        data = loader.load()

        docs = text_splitter.split_documents(data)

        all_docs.extend(docs)

    print("Adding docs to vector DB")

    uuids = [
        str(uuid4())
        for _ in range(len(all_docs))
    ]

    vector_store.add_documents(
        all_docs,
        ids=uuids
    )


def generate_answers(query):

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "lambda_mult": 0.5
        }
    )

    retrieved_docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in retrieved_docs]
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are a professional Question Answering system.
        
        Your task is to answer the user's question
        using ONLY the provided context.
        
        Do NOT use external knowledge.
        
        If the answer is not found in context,
        say:
        "I don't know based on the provided PDFs."
        
        Context:
        {context}
        
        Question:
        {query}
        
        Guidelines:
        - Be concise
        - Be factual
        - Do not hallucinate
        """
    )
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    answer = chain.invoke({
        "context": context,
        "query": query
    })

    chunks = []

    seen = set()

    for doc in retrieved_docs:

        source = doc.metadata.get("source")
        page = doc.metadata.get("page_label")

        key = (source, page)

        if key not in seen:

            seen.add(key)

            chunks.append({
                "source": source,
                "page": page,
                "content": doc.page_content
            })

    return answer, chunks