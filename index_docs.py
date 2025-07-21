# index_docs.py

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.cohere import Cohere
import os

# Load your documents
reader = SimpleDirectoryReader("data/docs")
docs = reader.load_data()

# Use free HuggingFace embeddings
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Use Cohere LLM
cohere_api_key = os.getenv("COHERE_API_KEY") or "YOUR_COHERE_API_KEY"
llm = Cohere(api_key=cohere_api_key)

# Create index with Cohere LLM
index = VectorStoreIndex.from_documents(docs, embed_model=embed_model, llm=None)

# Save the index
index.storage_context.persist(persist_dir="./storage")
print("✅ Indexing complete. Stored in ./storage")
