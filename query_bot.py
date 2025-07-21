# query_bot.py

from dotenv import load_dotenv
import os

load_dotenv()

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.cohere import Cohere

# Load the index
storage_context = StorageContext.from_defaults(persist_dir="./storage")

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Cohere(api_key=os.getenv("COHERE_API_KEY"))

# Use OpenAI LLM
index = load_index_from_storage(storage_context, embed_model=embed_model, llm=llm)

query_engine = index.as_query_engine(llm=llm)

while True:
    question = input("❓ Ask your docs: ")
    if question.lower() in ['exit', 'quit']:
        break
    response = query_engine.query(question)
    print("💡", response, "\n")
