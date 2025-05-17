# FastAPI GitHub User Q&A with Google Gemini AI

This project is a FastAPI application that fetches public GitHub user profile and repository information, then uses Google Gemini generative AI to answer user questions based on that data. The Q&A pairs are saved in MongoDB for future reference.

---

## Features

- Fetch GitHub user profile data and public repositories via GitHub API
- Query Google Gemini generative AI model (`gemini-1.5-pro`) with user data as context
- Return AI-generated answers to user questions related to GitHub users
- Save username, question, and AI answer in MongoDB database for logging/history
- Handles API errors and exceptions gracefully

---

## Technologies Used

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework for building APIs  
- [Pydantic](https://pydantic.dev/) — Data validation for request bodies  
- [Google Generative AI (Gemini)](https://ai.google/technology/generative-ai/) — Large language model for question answering  
- [MongoDB](https://www.mongodb.com/) — NoSQL database for storing Q&A records  
- [Requests](https://requests.readthedocs.io/en/latest/) — HTTP client for GitHub API calls  
- [python-dotenv](https://github.com/theskumar/python-dotenv) — Load environment variables from `.env` file  

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/fastapi-github-gemini.git
   cd fastapi-github-gemini
   
2. python3 -m venv env
source env/bin/activate  # Linux/macOS
# or
env\Scripts\activate     # Windows

3. pip install requirements.txt

4. Create a .env file with your credentials
 GOOGLE_API_KEY=your_google_gemini_api_key
MONGODB_URI=your_mongodb_connection_string

6. Run the fast api server
 uvicorn main:app --reload
