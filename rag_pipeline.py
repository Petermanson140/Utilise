import shutil
import os
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

# UPDATED: Replaced the broken community import with the modern dedicated package
from langchain_chroma import Chroma

# UPDATED: Correct wrapper for HuggingFace embeddings
from langchain_huggingface import HuggingFaceEmbeddings


# ── Step 1: Load all documents from rag_docs folder ──────────────
def load_documents(folder="rag_docs"):
    documents = []
    
    if not os.path.exists(folder):
        os.makedirs(folder)
        print(f"Created missing folder: '{folder}'. Please drop your .txt files there.")
        return documents

    for filename in os.listdir(folder):
        if filename.endswith(".txt"):
            filepath = os.path.join(folder, filename)
            
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Create a Document object with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": filename,
                    "filepath": filepath
                }
            )
            documents.append(doc)
            print(f"✅ Loaded: {filename} ({len(content)} characters)")
    
    return documents

#Step 2: Split documents into chunks 
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks

#Step 3: Creating embeddings and storing in ChromaDB
def create_vector_store(chunks, persist_directory="chroma_db"):
    print("Loading embedding model...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    print("Creating vector store")
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print("Vector store created successfully")
    return vectorstore

#Step 4: Load existing vector store
def load_vector_store(persist_directory="chroma_db"):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    
    print("Loaded vector store successfully")
    return vectorstore

#Step 5: Retrieving the relevant chunks for a query
def retrieve_context(query, vectorstore, k=4):
    results = vectorstore.similarity_search(query, k=k)
    
    context = "\n\n".join([
        f"Source: {doc.metadata['source']}\n{doc.page_content}"
        for doc in results
    ])
    
    return context

# ── Main: Build the RAG pipeline ─────────────────────────────────
if __name__ == "__main__":
    print("Building Utilize RAG Pipeline")
    print("=" * 50)
    
    # Load documents
    documents = load_documents("rag_docs")
    
    if not documents:
        print("No documents were found in rag_docs folder")
        exit()
    
    # Split into chunks
    chunks = split_documents(documents)
    
    # Create vector store
    vectorstore = create_vector_store(chunks)
    
    print("\n" + "=" * 50)
    print("RAG Pipeline built successfully")
    print("Testing retrieval")
    
    #Testing with a sample query
    test_query = "How can I save money on my electricity, gas and water bills?"
    context = retrieve_context(test_query, vectorstore)
    
    print(f"Query: {test_query}")
    print("-" * 50)
    print(f"Retrieved context:\n{context[:500]}...")
    print("-" * 50)
    print("The RAG pipeline is working successfully")

