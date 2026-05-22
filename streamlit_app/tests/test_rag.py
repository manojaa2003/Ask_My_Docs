import sys
from pathlib import Path

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from rag import (
    initialize_components,
    process_pdfs,
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)

def test_initialize_components():
    initialize_components()
    assert True

def test_text_chunking():
    text = (
        "This is a test document. "
        * 200
    )
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    docs = splitter.create_documents([text])
    assert len(docs) > 0


def test_process_pdfs():
    sample_pdf = (
            Path(__file__).parent / "test_document.pdf"
    )
    process_pdfs([sample_pdf])
    assert True
