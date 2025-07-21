from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
app.add_middleware(
    SessionMiddleware,
    secret_key="kbcwkqufg48rtfgbeifugfw875fgbuygadsgv374r837egdcb",
    same_site="lax",
    https_only=False
)

oauth = OAuth()
oauth.register(
    name='notion',
    client_id=os.getenv("NOTION_CLIENT_ID"),
    client_secret=os.getenv("NOTION_CLIENT_SECRET"),
    access_token_url='https://api.notion.com/v1/oauth/token',
    authorize_url='https://api.notion.com/v1/oauth/authorize',
    api_base_url='https://api.notion.com/v1/',
    client_kwargs={'scope': 'read:content', 'token_endpoint_auth_method': 'client_secret_post'},
)

oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/documents.readonly',
        'access_type': 'offline',
        'prompt': 'consent'
    },
)

@app.get('/auth/notion/login')
async def login(request: Request):
    redirect_uri = request.url_for('notion_callback')
    return await oauth.notion.authorize_redirect(request, redirect_uri)

@app.get('/auth/notion/callback')
async def notion_callback(request: Request):
    token = await oauth.notion.authorize_access_token(request)
    request.session['notion_token'] = token
    return RedirectResponse(url="http://localhost:8501")  # or your Streamlit app URL

@app.get('/auth/google/login')
async def google_login(request: Request):
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get('/auth/google/callback')
async def google_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
        request.session['google_token'] = token
        return RedirectResponse(url="http://localhost:8501")
    except Exception as e:
        print(f"Google OAuth error: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get('/auth/notion/token')
async def get_notion_token(request: Request):
    token = request.session.get('notion_token')
    if token:
        return JSONResponse(token)
    return JSONResponse({"error": "Not logged in"}, status_code=401)

@app.get('/auth/google/token')
async def get_google_token(request: Request):
    token = request.session.get('google_token')
    if token:
        return JSONResponse(token)
    return JSONResponse({"error": "Not logged in"}, status_code=401)