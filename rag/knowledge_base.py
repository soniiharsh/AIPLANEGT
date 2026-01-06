# rag/knowledge_base.py - FIXED VERSION

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitters import RecursiveCharacterTextSplitter
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
        # Check if knowledge base path exists
        if not os.path.exists(self.kb_path):
            print(f"⚠️ Knowledge base path not found: {self.kb_path}")
            os.makedirs(self.kb_path, exist_ok=True)
            # Create a dummy document
            with open(os.path.join(self.kb_path, "sample.md"), "w") as f:
                f.write("# Sample Knowledge\n\nThis is a sample document.")
        
        # Load documents
        try:
            loader = DirectoryLoader(
                self.kb_path,
                glob="**/*.md",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            if not documents:
                print("⚠️ No documents found. Using empty vector store.")
                return 0
            
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
            
            print(f"✅ Built knowledge base with {len(chunks)} chunks from {len(documents)} documents")
            return len(chunks)
            
        except Exception as e:
            print(f"❌ Error building knowledge base: {e}")
            # Create empty vector store as fallback
            from langchain.schema import Document
            dummy_doc = Document(page_content="Dummy document", metadata={})
            self.vector_store = FAISS.from_documents([dummy_doc], self.embeddings)
            return 0
    
    def retrieve(self, query, top_k=3):
        """Retrieve relevant chunks"""
        if not self.vector_store:
            print("⚠️ Vector store not initialized")
            return []
        
        try:
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
        except Exception as e:
            print(f"❌ Error retrieving documents: {e}")
            return []