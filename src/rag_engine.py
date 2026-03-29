import os
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv

load_dotenv()

# Configure APIs
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=60)

COLLECTION_NAME = "epicchain_kb"

def get_embedding(text):
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document",
        title="EpicChain Knowledge Base"
    )
    return result['embedding']

def init_collection():
    """Initializes the Qdrant collection for EpicChain KB."""
    try:
        collection_info = client.get_collection(collection_name=COLLECTION_NAME)
        current_size = collection_info.config.params.vectors.size
        if current_size != 3072:
            print(f"Dimension mismatch (expected 3072, got {current_size}). Recreating collection...")
            client.delete_collection(collection_name=COLLECTION_NAME)
            raise Exception("Recreate")
    except Exception:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=3072, distance=models.Distance.COSINE),
        )
        print(f"Collection '{COLLECTION_NAME}' created with size 3072.")

def ingest_knowledge_base(file_path):
    """Chunks the knowledge-base.md and uploads to Qdrant."""
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, 'r') as f:
        content = f.read()

    # Simple chunking by headers or paragraphs
    # For now, let's split by sections (##)
    sections = content.split("##")
    points = []
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        text = f"## {section.strip()}"
        vector = get_embedding(text)
        points.append(models.PointStruct(
            id=i,
            vector=vector,
            payload={"text": text}
        ))

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Ingested {len(points)} sections into Qdrant.")

def search_kb(query, limit=3):
    """Searches the KB for relevant context."""
    query_vector = get_embedding(query)
    
    search_result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit
    ).points
    
    context = "\n\n".join([res.payload["text"] for res in search_result])
    return context

if __name__ == "__main__":
    # Test script
    init_collection()
    kb_path = os.path.join(os.path.dirname(__file__), "../knowledge-base.md")
    ingest_knowledge_base(kb_path)
    print("Test Search: 'What is the max supply?'")
    print(search_kb("What is the max supply?"))
