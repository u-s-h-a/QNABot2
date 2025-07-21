# file: slack_bot.py
from fastapi import FastAPI, Request
from llama_index import load_index_from_storage, StorageContext
from llama_index.llms import OpenAI
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
import os

app = FastAPI()
client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

storage_context = StorageContext.from_defaults(persist_dir="./storage")
index = load_index_from_storage(storage_context)
query_engine = index.as_query_engine()

@app.post("/slack/ask")
async def ask_slack(request: Request):
    data = await request.form()
    question = data.get("text", "")
    channel_id = data.get("channel_id")

    answer = query_engine.query(question)
    client.chat_postMessage(channel=channel_id, text=str(answer))
    return {"text": "Answer sent!"}
