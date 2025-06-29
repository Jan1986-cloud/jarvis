"""
Vector Database Service
Handles document embeddings and retrieval using ChromaDB
"""

import os
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

class VectorDatabaseService:
    """Service for managing document embeddings and retrieval"""
    
    def __init__(self, persist_directory: str = None):
        """
        Initialize vector database service
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        if not persist_directory:
            persist_directory = os.path.join(
                os.path.dirname(__file__), '..', '..', 'data', 'chroma'
            )
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            self.embedding_model = None
        
        # Initialize collections
        self.documents_collection = None
        self.conversations_collection = None
        
        try:
            self.documents_collection = self._get_or_create_collection("documents")
            self.conversations_collection = self._get_or_create_collection("conversations")
        except Exception as e:
            print(f"Warning: Could not initialize collections: {e}")
        
        # Configure Gemini API
        self._setup_gemini()
    
    def _setup_gemini(self):
        """Setup Gemini AI API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            try:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-flash-2.5')
            except Exception as e:
                print(f"Warning: Could not configure Gemini: {e}")
                self.gemini_model = None
        else:
            self.gemini_model = None
            print("Warning: GEMINI_API_KEY not set. AI features will be limited.")
    
    def _get_or_create_collection(self, name: str):
        """Get or create a ChromaDB collection"""
        try:
            # Try to get existing collection
            return self.client.get_collection(name=name)
        except Exception:
            # Create new collection if it doesn't exist
            try:
                return self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
            except Exception as e:
                print(f"Warning: Could not create collection {name}: {e}")
                return None
    
    def _ensure_collections(self):
        """Ensure collections are initialized"""
        if not self.documents_collection:
            self.documents_collection = self._get_or_create_collection("documents")
        if not self.conversations_collection:
            self.conversations_collection = self._get_or_create_collection("conversations")
    
    def _generate_document_id(self, content: str, source: str) -> str:
        """Generate unique document ID based on content and source"""
        content_hash = hashlib.md5(f"{source}:{content}".encode()).hexdigest()
        return f"doc_{content_hash}"
    
    def add_document(self, content: str, source: str, metadata: Dict = None) -> str:
        """
        Add document to vector database
        
        Args:
            content: Document content
            source: Source identifier (e.g., Google Drive file ID)
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        if not content.strip():
            raise ValueError("Document content cannot be empty")
        
        if not self.embedding_model or not self.documents_collection:
            print("Warning: Vector database not fully initialized")
            return ""
        
        # Generate document ID
        doc_id = self._generate_document_id(content, source)
        
        # Prepare metadata
        doc_metadata = {
            "source": source,
            "added_at": datetime.utcnow().isoformat(),
            "content_length": len(content),
            **(metadata or {})
        }
        
        try:
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
            # Add to collection
            self.documents_collection.add(
                documents=[content],
                metadatas=[doc_metadata],
                ids=[doc_id],
                embeddings=[embedding]
            )
            
            return doc_id
        except Exception as e:
            print(f"Error adding document: {e}")
            return ""
    
    def search_documents(self, query: str, n_results: int = 5, 
                        source_filter: str = None) -> List[Dict]:
        """
        Search for relevant documents
        
        Args:
            query: Search query
            n_results: Number of results to return
            source_filter: Filter by source (optional)
            
        Returns:
            List of relevant documents with metadata
        """
        if not query.strip() or not self.embedding_model or not self.documents_collection:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Prepare where clause for filtering
            where_clause = None
            if source_filter:
                where_clause = {"source": {"$eq": source_filter}}
            
            # Search in collection
            results = self.documents_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'similarity_score': 1 - results['distances'][0][i],  # Convert distance to similarity
                        'source': results['metadatas'][0][i].get('source', 'unknown')
                    })
            
            return formatted_results
        except Exception as e:
            print(f"Error searching documents: {e}")
            return []
    
    def add_conversation_context(self, conversation_id: str, messages: List[Dict]) -> str:
        """
        Add conversation context to vector database
        
        Args:
            conversation_id: Conversation ID
            messages: List of message dicts
            
        Returns:
            Context ID
        """
        if not messages or not self.embedding_model or not self.conversations_collection:
            return ""
        
        try:
            # Create conversation context
            context_content = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in messages
            ])
            
            context_id = f"conv_{conversation_id}_{datetime.utcnow().timestamp()}"
            
            # Prepare metadata
            metadata = {
                "conversation_id": conversation_id,
                "message_count": len(messages),
                "added_at": datetime.utcnow().isoformat(),
                "type": "conversation"
            }
            
            # Generate embedding
            embedding = self.embedding_model.encode(context_content).tolist()
            
            # Add to conversations collection
            self.conversations_collection.add(
                documents=[context_content],
                metadatas=[metadata],
                ids=[context_id],
                embeddings=[embedding]
            )
            
            return context_id
        except Exception as e:
            print(f"Error adding conversation context: {e}")
            return ""
    
    def get_relevant_context(self, query: str, conversation_id: str = None,
                           n_results: int = 3) -> Dict:
        """
        Get relevant context for a query
        
        Args:
            query: User query
            conversation_id: Current conversation ID (optional)
            n_results: Number of results per source
            
        Returns:
            Dict with document and conversation context
        """
        context = {
            'documents': [],
            'conversations': [],
            'query': query
        }
        
        if not self.embedding_model:
            return context
        
        # Search documents
        try:
            doc_results = self.search_documents(query, n_results)
            context['documents'] = doc_results
        except Exception as e:
            print(f"Error searching documents for context: {e}")
        
        # Search conversation history (excluding current conversation)
        if self.conversations_collection:
            try:
                query_embedding = self.embedding_model.encode(query).tolist()
                
                where_clause = None
                if conversation_id:
                    where_clause = {"conversation_id": {"$ne": conversation_id}}
                
                conv_results = self.conversations_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where_clause,
                    include=["documents", "metadatas", "distances"]
                )
                
                if conv_results['documents'] and conv_results['documents'][0]:
                    for i, doc in enumerate(conv_results['documents'][0]):
                        context['conversations'].append({
                            'content': doc,
                            'metadata': conv_results['metadatas'][0][i],
                            'similarity_score': 1 - conv_results['distances'][0][i]
                        })
            except Exception as e:
                print(f"Error searching conversations for context: {e}")
        
        return context
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the vector database"""
        try:
            doc_count = self.documents_collection.count() if self.documents_collection else 0
            conv_count = self.conversations_collection.count() if self.conversations_collection else 0
            
            return {
                'documents': doc_count,
                'conversations': conv_count,
                'total_items': doc_count + conv_count,
                'embedding_model': 'all-MiniLM-L6-v2' if self.embedding_model else 'not loaded',
                'gemini_configured': self.gemini_model is not None,
                'collections_initialized': bool(self.documents_collection and self.conversations_collection)
            }
        except Exception as e:
            return {
                'error': str(e),
                'documents': 0,
                'conversations': 0,
                'total_items': 0,
                'embedding_model': 'error',
                'gemini_configured': False,
                'collections_initialized': False
            }

# Global vector database service instance
try:
    vector_service = VectorDatabaseService()
except Exception as e:
    print(f"Warning: Could not initialize vector service: {e}")
    vector_service = None

