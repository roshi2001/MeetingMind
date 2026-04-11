from dotenv import load_dotenv
import os

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.3-70b-versatile"
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
    You are a helpful meeting assistant.
    Use the following meeting transcript context to answer the question.
    If you don't know the answer, say "I couldn't find that in the meeting transcript."

    Context:
    {context}

    Question:
    {question}

    Answer:
    """
)

vector_store = None

def build_vector_store(transcript: str):
    global vector_store
    chunks = splitter.split_text(transcript)
    vector_store = FAISS.from_texts(chunks, embeddings)
    return f"Vector store built with {len(chunks)} chunks"

def answer_question(question: str) -> str:
    global vector_store
    if vector_store is None:
        return "Please upload a transcript first."

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    return chain.invoke(question)