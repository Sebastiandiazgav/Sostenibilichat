from pinecone import Pinecone, ServerlessSpec
from langchain_aws import BedrockEmbeddings
from core.config import settings
import logging
import uuid

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self):
        try:
            # Initialize Pinecone
            self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)

            # Initialize Bedrock embeddings
            self.embeddings = BedrockEmbeddings(
                model_id="amazon.titan-embed-text-v1",
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )

            # Check if index exists, create if not
            if settings.PINECONE_INDEX_NAME not in self.pc.list_indexes().names():
                logger.info(f"Creating Pinecone index: {settings.PINECONE_INDEX_NAME}")
                self.pc.create_index(
                    name=settings.PINECONE_INDEX_NAME,
                    dimension=1536,  # Titan embeddings dimension
                    metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region="us-east-1")
                )

            # Get index
            self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
            logger.info("Vector store initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents."""
        try:
            # Generate embedding for query
            query_embedding = self.embeddings.embed_query(query)

            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True
            )

            docs = []
            for match in results['matches']:
                docs.append({
                    "page_content": match['metadata'].get('text', ''),
                    "metadata": {
                        "source": match['metadata'].get('source', 'Unknown'),
                        "score": match['score']
                    }
                })

            logger.info(f"Found {len(docs)} similar documents")
            return docs

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []

    def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        """Add texts to the vector store."""
        try:
            if metadatas is None:
                metadatas = [{}] * len(texts)

            # Generate embeddings for all texts
            embeddings = self.embeddings.embed_documents(texts)

            # Prepare vectors for Pinecone
            vectors = []
            for i, (text, metadata, embedding) in enumerate(zip(texts, metadatas, embeddings)):
                vector_id = str(uuid.uuid4())
                metadata_combined = {
                    "text": text,
                    "source": metadata.get("source", "Unknown"),
                    **metadata
                }
                vectors.append({
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata_combined
                })

            # Upsert to Pinecone in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Added {len(texts)} texts to vector store")
            return f"Added {len(texts)} texts"

        except Exception as e:
            logger.error(f"Error adding texts: {e}")
            raise

# Global instance
vector_store = VectorStore()