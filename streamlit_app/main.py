import streamlit as st
from pathlib import Path

from rag import process_pdfs, generate_answers

st.set_page_config(
    page_title="PDF Chat",
    page_icon="📄",
    layout="centered"
)

st.title("📄 PDF Chat Assistant")

st.write(
    "Upload PDFs and ask questions from them."
)

uploaded_files = st.file_uploader(
    "Upload PDF Files",
    type=["pdf"],
    accept_multiple_files=True
)

if st.button("Process PDFs"):
    if not uploaded_files:
        st.warning(
            "Please upload at least one PDF."
        )
    else:
        pdf_paths = []
        upload_dir = Path("uploaded_pdfs")
        upload_dir.mkdir(exist_ok=True)

        for file in uploaded_files:
            file_path = upload_dir / file.name

            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            pdf_paths.append(str(file_path))

        with st.spinner(
            "Processing PDFs..."
        ):
            process_pdfs(pdf_paths)
        st.success(
            "PDFs processed successfully!"
        )

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["answer"])
        if msg["role"] == "assistant":
            st.markdown("---")
            st.markdown("### 📌 Citations")

            for chunk in msg["chunks"]:

                st.markdown(
                    f"- **Source:** "
                    f"{chunk['source']}"
                )
                st.markdown(
                    f"- **Page:** "
                    f"{chunk['page']}"
                )
            with st.expander(
                "📎 Source Chunks"
            ):
                for i, chunk in enumerate(
                    msg["chunks"],
                    start=1
                ):
                    st.markdown(
                        f"### Chunk {i}"
                    )
                    st.code(
                        chunk["content"]
                    )
query = st.chat_input(
    "Ask a question about the PDFs..."
)

if query:
    with st.chat_message("user"):

        st.markdown(query)
    st.session_state.messages.append({
        "role": "user",
        "answer": query
    })

    try:
        with st.spinner(
            "Generating answer..."
        ):
            answer, chunks = generate_answers(query)

        with st.chat_message("assistant"):
            st.markdown(answer)
            st.markdown("---")
            st.markdown(
                "### 📌 Citations"
            )

            for chunk in chunks:
                st.markdown(
                    f"- **Source:** "
                    f"{chunk['source']}"
                )
                st.markdown(
                    f"- **Page:** "
                    f"{chunk['page']}"
                )
            with st.expander(
                "📎 Source Chunks"
            ):
                for i, chunk in enumerate(
                    chunks,
                    start=1
                ):
                    st.markdown(
                        f"### Chunk {i}"
                    )
                    st.code(
                        chunk["content"]
                    )
        st.session_state.messages.append({
            "role": "assistant",
            "answer": answer,
            "chunks": chunks
        })

    except Exception as e:

        st.error(f"Error: {e}")