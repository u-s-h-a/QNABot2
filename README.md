# QnA Bot for Internal Docs

This app lets you ask questions about your internal documents using AI. You can upload files directly, or (for advanced users) automatically sync docs from Notion, Google Docs, or Confluence.

---

## 🚀 Features
- Upload PDF, DOCX, TXT files and ask questions in natural language
- Automated ingestion from Notion, Google Docs, and Confluence (optional)
- Chat interface with history, dark/light mode, and more

---

## 📁 Manual File Upload (Default)
- Just run the app and upload your files in the sidebar.
- No extra setup needed!

---

## 🔄 Automated Ingestion (Advanced)
If your team uses Notion, Google Docs, or Confluence, you can automatically sync and index your docs.

### 1. Set Up Your `.env` File
Add the following (fill in your real values):
```
# Notion
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Docs
GOOGLE_SERVICE_ACCOUNT_FILE=service_account.json
GOOGLE_DOCUMENT_IDS=docid1,docid2,docid3

# Confluence
CONFLUENCE_BASE_URL=https://yourcompany.atlassian.net/wiki
CONFLUENCE_USERNAME=your.email@company.com
CONFLUENCE_API_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
CONFLUENCE_SPACE_KEY=ENG
```

#### How to get these values?
- **NOTION_DATABASE_ID:** Open your Notion page/database, copy the 32-character ID from the URL (see app help for details).
- **GOOGLE_DOCUMENT_IDS:** Open your Google Doc, copy the ID from the URL after `/d/` and before `/edit`.
- **CONFLUENCE_BASE_URL:** The main URL of your Confluence site.
- **CONFLUENCE_SPACE_KEY:** The code after `/spaces/` in your Confluence space URL.

See the app help or ask your admin if you need more guidance!

### 2. Install Required Packages
```
pip install llama-index llama-index-readers-notion llama-index-readers-google llama-index-readers-confluence
```

### 3. Run the Sync Script
```
python sync_sources.py
```
This will fetch and index all docs from the platforms you configured.

---

## 📝 Notes
- If you don’t use Notion, Google Docs, or Confluence, you can ignore the sync script and just use file upload.
- Your uploaded files and synced docs are combined in the same index.
- You can use both features together or separately.

---

## 💬 Need Help?
- See the in-app help or contact your admin.
- For more details on credentials, see the comments in `sync_sources.py` or ask your team’s platform admin. 