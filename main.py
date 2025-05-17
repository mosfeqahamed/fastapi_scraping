from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import textwrap
from pymongo import MongoClient
from fastapi import Request
import traceback
import time

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MONGODB_URI = os.getenv('MONGODB_URI')


genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-pro')


client = MongoClient(MONGODB_URI)
db = client["fastapi_web_scraping"]
collection = db["fastapi_scraping"]

app = FastAPI()

class QueryRequest(BaseModel):
    username: str
    question: str

def fetch_github_user(username):
    headers = {'Accept': 'application/vnd.github.v3+json'}
    user_url = f"https://api.github.com/users/{username}"
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"

    user_response = requests.get(user_url, headers=headers)
    user_response.raise_for_status()
    user_data = user_response.json()

    repos_response = requests.get(repos_url, headers=headers)
    repos_response.raise_for_status()
    repos_data = repos_response.json()

    user_info = f"Name: {user_data.get('name')}\n" \
                f"Bio: {user_data.get('bio')}\n" \
                f"Location: {user_data.get('location')}\n" \
                f"Public Repos: {user_data.get('public_repos')}\n" \
                f"Followers: {user_data.get('followers')}\n" \
                f"Following: {user_data.get('following')}\n"

    repos_info = "Repositories:\n"
    for repo in repos_data:
        repos_info += f"- {repo.get('name')} (⭐ {repo.get('stargazers_count')}): {repo.get('description')}\n"

    full_info = user_info + "\n" + repos_info
    return textwrap.wrap(full_info, 8000)

def ask_question(content_chunks, query):
    prompt_template = """Context: {}

Question: {}

Based on the context provided, please answer the question. If the information is not available in the context, please say so."""

    for chunk in content_chunks:
        prompt = prompt_template.format(chunk, query)
        response = model.generate_content(prompt)

        if response.text and not response.text.lower().startswith(("i don't", "i cannot", "no information")):
            return response.text

    return "I couldn't find relevant information to answer your question."

@app.post("/ask")
def ask_about_user(data: QueryRequest, request: Request):
    try:
        chunks = fetch_github_user(data.username)
        answer = ask_question(chunks, data.question)

        # Save to MongoDB
        record = {
            "username": data.username,
            "question": data.question,
            "answer": answer
        }
        collection.insert_one(record)

        return {"username": data.username, "question": data.question, "answer": answer}
    except Exception as e:
        print("----- ERROR OCCURRED -----")
        traceback.print_exc()  # This prints the detailed error in terminal
        raise HTTPException(status_code=500, detail=str(e))