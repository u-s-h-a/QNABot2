import os
from dotenv import load_dotenv

# Load environment variables for API keys/tokens
load_dotenv()

from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms.cohere import Cohere  # Only needed if you want to use Cohere LLM

from llama_index.readers.notion import NotionPageReader
from llama_index.readers.google import GoogleDocsReader
from llama_index.readers.confluence import ConfluenceReader

# --- CONFIG ---
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
GOOGLE_DOCUMENT_IDS = [doc_id.strip() for doc_id in os.getenv("GOOGLE_DOCUMENT_IDS", "").split(",") if doc_id.strip()]
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

# --- Load from Notion ---
notion_docs = []
try:
    if NOTION_TOKEN and NOTION_DATABASE_ID:
        print("Fetching from Notion...")
        notion_reader = NotionPageReader(integration_token=NOTION_TOKEN)
        notion_docs = notion_reader.load_data(page_ids=[NOTION_DATABASE_ID])
        print(f"Loaded {len(notion_docs)} Notion docs.")
    else:
        print("Notion credentials not set. Skipping Notion.")
except Exception as e:
    print(f"Error loading Notion docs: {e}")

# --- Load from Google Docs ---
google_docs = []
try:
    if GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_DOCUMENT_IDS:
        print("Fetching from Google Docs...")
        google_reader = GoogleDocsReader(service_account_key=GOOGLE_SERVICE_ACCOUNT_FILE)
        google_docs = google_reader.load_data(document_ids=GOOGLE_DOCUMENT_IDS)
        print(f"Loaded {len(google_docs)} Google Docs.")
    else:
        print("Google Docs credentials not set. Skipping Google Docs.")
except Exception as e:
    print(f"Error loading Google Docs: {e}")

# --- Load from Confluence ---
confluence_docs = []
try:
    if CONFLUENCE_BASE_URL and CONFLUENCE_USERNAME and CONFLUENCE_API_TOKEN and CONFLUENCE_SPACE_KEY:
        print("Fetching from Confluence...")
        confluence_reader = ConfluenceReader(
            base_url=CONFLUENCE_BASE_URL,
            username=CONFLUENCE_USERNAME,
            api_token=CONFLUENCE_API_TOKEN,
        )
        confluence_docs = confluence_reader.load_data(space_key=CONFLUENCE_SPACE_KEY)
        print(f"Loaded {len(confluence_docs)} Confluence docs.")
    else:
        print("Confluence credentials not set. Skipping Confluence.")
except Exception as e:
    print(f"Error loading Confluence docs: {e}")

# --- Combine all docs ---
all_docs = notion_docs + google_docs + confluence_docs
print(f"Total docs to index: {len(all_docs)}")

if not all_docs:
    print("No documents found from any source. Exiting.")
    exit(0)

# --- Index and persist ---
print("Indexing documents...")
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
index = VectorStoreIndex.from_documents(all_docs, embed_model=embed_model)
index.storage_context.persist(persist_dir="./storage")
print("Index updated and saved to ./storage.") 