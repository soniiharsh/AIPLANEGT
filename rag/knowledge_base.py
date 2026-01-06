from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import os

class KnowledgeBase:
    def __init__(self, kb_path, embed_model, chunk_size=500):
        self.kb_path = kb_path
        self.chunk_size = chunk_size
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embed_model
        )
        self.vector_store = None
    
    def build(self):
        """Load documents and create vector store"""
        # Load documents
        loader = DirectoryLoader(
            self.kb_path,
            glob="**/*.md",
            loader_cls=TextLoader
        )
        documents = loader.load()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(
            chunks, 
            self.embeddings
        )
        
        return len(chunks)
    
    def retrieve(self, query, top_k=3):
        """Retrieve relevant chunks"""
        if not self.vector_store:
            raise ValueError("Vector store not built")
        
        results = self.vector_store.similarity_search_with_score(
            query, 
            k=top_k
        )
        
        return [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": float(score)
            }
            for doc, score in results
        ]