from dotenv import load_dotenv
import os
import nltk
nltk.data.path.append("./nltk_data")

import streamlit as st
import tempfile
import shutil
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

from llama_index.core import VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.cohere import Cohere
from llama_index.core import SimpleDirectoryReader

FASTAPI_URL = "http://localhost:8000"

def get_profile():
    try:
        resp = requests.get(f"{FASTAPI_URL}/profile")
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def get_google_token():
    try:
        resp = requests.get(f"{FASTAPI_URL}/auth/google/token", cookies=dict(st.session_state.get("cookies", {})))
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

st.set_page_config(page_title="QnA Bot", page_icon="🤖")

# Show a single title and description
st.title("📄 QnA Bot")
st.write("Welcome to the QnA bot! Upload your files and ask questions.")

# --- UI Customization ---
st.set_page_config(page_title="QnA Bot", page_icon="🤖", layout="wide")
st.markdown(
    """
    <style>
    .main {background-color: #f5f7fa;}
    .st-bb {background-color: #fff !important;}
    .st-cq {color: #2d3748;}
    .stButton>button {background-color: #4f8cff; color: white;}
    .css-1d391kg {background-color: #4f8cff;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("""
    <style>
    /* Fix for Streamlit multiselect dropdown in dark mode */
    div[data-baseweb="select"] > div {
        background-color: #22223b !important;  /* dark background */
        color: #fff !important;                /* white text */
    }
    /* Dropdown options */
    div[data-baseweb="popover"] {
        background-color: #22223b !important;
        color: #fff !important;
    }
    /* Selected option chips */
    .css-1n76uvr {
        background-color: #4f8cff !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Branding & Upload ---
st.sidebar.image("https://em-content.zobj.net/source/microsoft-teams/363/robot_1f916.png", width=80)
st.sidebar.title("QnA Bot")
st.sidebar.markdown("Ask questions about your documents. Upload new files to update the knowledge base.")

# Add Notion, Google Docs, and Confluence connect buttons to sidebar
notion_connect_url = "http://localhost:8000/auth/notion/login"
google_connect_url = "http://localhost:8000/auth/google/login"  # Now points to the real backend endpoint
confluence_connect_url = "http://localhost:8000/auth/confluence/login"  # Placeholder, update if you implement Confluence OAuth

# Button group styling for horizontal layout in sidebar
st.markdown(
    f'''
    <div style="display:flex;gap:8px;justify-content:flex-start;margin-bottom:10px;">
        <a href="{google_connect_url}" target="_blank" style="text-decoration:none;">
            <button style="background:#34a853;color:#fff;border:1px solid #34a853;padding:8px 10px;border-radius:6px;cursor:pointer;min-width:40px;"> Google Docs</button>
        </a>
        <a href="{confluence_connect_url}" target="_blank" style="text-decoration:none;">
            <button style="background:#0052cc;color:#fff;border:1px solid #0052cc;padding:8px 10px;border-radius:6px;cursor:pointer;min-width:40px;">Confluence</button>
        </a>
        <a href="{notion_connect_url}" target="_blank" style="text-decoration:none;">
            <button style="background:#4f8cff;color:#fff;border:1px solid #4f8cff;padding:8px 30px;border-radius:6px;cursor:pointer;min-width:40px;">Notion</button>
        </a>
    </div>
    ''',
    unsafe_allow_html=True
)

# --- Sidebar: Connect & Sync Sources ---
# Remove the Connect & Sync Sources section from the sidebar
# (Delete or comment out the following block)
# st.sidebar.header("Connect & Sync Sources")
# notion_token = st.sidebar.text_input("Notion Token", type="password", key="notion_token")
# notion_db_id = st.sidebar.text_input("Notion Database/Page ID", key="notion_db_id")
# google_service_file = st.sidebar.file_uploader("Google Service Account JSON", type="json", key="google_service_file")
# google_doc_ids = st.sidebar.text_input("Google Doc IDs (comma-separated)", key="google_doc_ids")
# confluence_url = st.sidebar.text_input("Confluence Base URL", key="confluence_url")
# confluence_user = st.sidebar.text_input("Confluence Username", key="confluence_user")
# confluence_token = st.sidebar.text_input("Confluence API Token", type="password", key="confluence_token")
# confluence_space = st.sidebar.text_input("Confluence Space Key", key="confluence_space")
# if st.sidebar.button("Sync Now"):
#     ... (all sync logic)


# --- File Upload ---
uploaded_files = st.sidebar.file_uploader(
    "Upload new documents (PDF, TXT, DOCX, etc.)",
    type=["pdf", "txt", "docx"],
    accept_multiple_files=True,
    key="uploaded_files"
)

# Always show the Upload button
if st.sidebar.button("Upload"):
    st.session_state['files_processed'] = False
    st.rerun()

# Only process if not already processed in this session
if uploaded_files and not st.session_state.get("files_processed", False):
    with st.spinner("Processing and indexing new documents..."):
        # Save uploaded files to a temp directory
        temp_dir = tempfile.mkdtemp()
        for uploaded_file in uploaded_files:
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        # Index new documents (only use embedding model)
        reader = SimpleDirectoryReader(input_dir=temp_dir)
        docs = reader.load_data()
        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)
        index.storage_context.persist(persist_dir="./storage")
        shutil.rmtree(temp_dir)
        st.session_state['files_processed'] = True
        st.session_state['reindex'] = True
        st.session_state["chat_history"] = []  # Clear chat history after new upload
        st.success("Documents uploaded and indexed! You can now ask questions about them.")

# --- Load index and models (after upload or on startup) ---
if 'reindex' in st.session_state and st.session_state['reindex']:
    st.session_state['reindex'] = False
    st.rerun()

# Ensure chat history is always initialized
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Try to load the index and embedding model
index = None
query_engine = None
try:
    storage_context = StorageContext.from_defaults(persist_dir="./storage")
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    cohere_api_key = os.getenv("COHERE_API_KEY") or "YOUR_COHERE_API_KEY"
    llm = Cohere(api_key=cohere_api_key)
    query_engine = index.as_query_engine(llm=llm)
except Exception as e:
    st.warning(f"Could not load index or embedding model: {e}")

# --- Display Google user info and welcome message (non-intrusive) ---
google_token = get_google_token()
if google_token and "access_token" in google_token:
    try:
        import requests
        userinfo_resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {google_token['access_token']}"}
        )
        if userinfo_resp.status_code == 200:
            userinfo = userinfo_resp.json()
            st.markdown("---")
            st.markdown(f"<div style='display:flex;align-items:center;gap:16px;'><img src='{userinfo.get('picture','')}' style='width:48px;height:48px;border-radius:50%;border:2px solid #4f8cff;'/><div><b>Welcome, {userinfo.get('name','User')}!</b><br><span style='color:#888;'>{userinfo.get('email','')}</span></div></div>", unsafe_allow_html=True)
    except Exception as e:
        st.info("Logged in with Google, but could not fetch user info.")

# --- Per-user Google Docs QnA (optional, non-intrusive) ---
google_token = get_google_token()
if google_token and "access_token" in google_token:
    creds = Credentials(
        token=google_token["access_token"],
        refresh_token=google_token.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/documents.readonly"]
    )
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        results = drive_service.files().list(
            q="mimeType='application/vnd.google-apps.document'",
            pageSize=10, fields="files(id, name)").execute()
        items = results.get('files', [])
        if items:
            st.markdown("---")
            st.subheader("Your Google Docs (per-user QnA)")
            doc_options = {f"{item['name']} (ID: {item['id']})": item['id'] for item in items}
            selected_doc = st.selectbox("Select a Google Doc to index and query (session only):", list(doc_options.keys()), key="user_gdoc_select")
            if selected_doc:
                doc_id = doc_options[selected_doc]
                if st.button("Index & Query This Doc", key="user_gdoc_index_btn"):
                    docs_service = build('docs', 'v1', credentials=creds)
                    doc = docs_service.documents().get(documentId=doc_id).execute()
                    text = ""
                    for element in doc.get("body", {}).get("content", []):
                        if "paragraph" in element:
                            for p_elem in element["paragraph"].get("elements", []):
                                text += p_elem.get("textRun", {}).get("content", "")
                    if text.strip():
                        from llama_index.core import VectorStoreIndex, Document
                        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                        embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
                        user_docs = [Document(text=text)]
                        user_index = VectorStoreIndex.from_documents(user_docs, embed_model=embed_model)
                        st.session_state["user_gdoc_query_engine"] = user_index.as_query_engine()
                        st.success("Google Doc indexed for this session! Use the box below to ask questions about it.")
    except Exception as e:
        st.warning(f"Error fetching your Google Docs: {e}")

# --- Per-user Google Docs QnA input (if available) ---
if "user_gdoc_query_engine" in st.session_state:
    with st.form("user_gdoc_qna_form", clear_on_submit=True):
        user_gdoc_question = st.text_input("❓ Ask your selected Google Doc:", key="user_gdoc_qna_input")
        user_gdoc_submitted = st.form_submit_button("Get Answer (Google Doc)")
    if user_gdoc_submitted and user_gdoc_question:
        try:
            gdoc_response = st.session_state["user_gdoc_query_engine"].query(user_gdoc_question)
        except Exception as e:
            gdoc_response = f"Error during Google Doc QnA: {e}"
        st.markdown(
            f'<div style="background:#232946;color:#eebbc3;padding:10px 16px;border-radius:18px 18px 4px 18px;margin-bottom:8px;max-width:80%;margin-left:auto;margin-right:0;font-size:1rem;">You: {user_gdoc_question}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#121629;color:#fffffe;padding:10px 16px;border-radius:18px 18px 18px 4px;margin-bottom:8px;max-width:80%;margin-right:auto;margin-left:0;font-size:1rem;">Bot: {gdoc_response}</div>',
            unsafe_allow_html=True,
        )

# Always show the input box
with st.form("qna_form", clear_on_submit=True):
    user_question = st.text_input("❓ Ask your docs:")
    submitted = st.form_submit_button("Get Answer")

if submitted and user_question:
    if query_engine is not None:
        try:
            response = query_engine.query(user_question)
        except Exception as e:
            response = f"Error during QnA: {e}"
    else:
        response = "QnA engine is not available. Please upload and index documents first."
    st.session_state.chat_history.append((user_question, str(response)))

# Display chat history as chat bubbles
if st.session_state.chat_history:
    st.markdown("---")
    for q, a in reversed(st.session_state.chat_history):
        st.markdown(
            f'<div style="background:#232946;color:#eebbc3;padding:10px 16px;border-radius:18px 18px 4px 18px;margin-bottom:8px;max-width:80%;margin-left:auto;margin-right:0;font-size:1rem;">You: {q}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div style="background:#121629;color:#fffffe;padding:10px 16px;border-radius:18px 18px 18px 4px;margin-bottom:8px;max-width:80%;margin-right:auto;margin-left:0;font-size:1rem;">Bot: {a}</div>',
            unsafe_allow_html=True,
        )
