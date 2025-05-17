import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import textwrap

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in your .env file")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-1.5-pro')

def fetch_github_user(username):
    """Fetch GitHub user details and repositories."""
    try:
        headers = {'Accept': 'application/vnd.github.v3+json'}
        user_url = f"https://api.github.com/users/{username}"
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"

        # Fetch user profile
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user_data = user_response.json()

        # Fetch repositories
        repos_response = requests.get(repos_url, headers=headers)
        repos_response.raise_for_status()
        repos_data = repos_response.json()

        # Combine user data and repos
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

        # Break into chunks if too long
        chunks = textwrap.wrap(full_info, 8000)
        return chunks

    except Exception as e:
        print(f"Error fetching GitHub user: {str(e)}")
        return None

def ask_question(content_chunks, query):
    """Ask Gemini a question based on GitHub user data."""
    try:
        prompt_template = """Context: {}

Question: {}

Based on the context provided, please answer the question. If the information is not available in the context, please say so."""

        for chunk in content_chunks:
            try:
                prompt = prompt_template.format(chunk, query)
                response = model.generate_content(prompt)

                if response.text and not response.text.lower().startswith(("i don't", "i cannot", "no information")):
                    return response.text
            except Exception:
                continue

        return "I couldn't find relevant information to answer your question about the GitHub user."
    except Exception as e:
        return f"An error occurred while generating the answer: {str(e)}"

def main():
    print("Welcome to the GitHub Profile QA Bot!")
    username = input("Enter GitHub username: ").strip()

    print(f"\nFetching GitHub data for user: {username}...")
    content_chunks = fetch_github_user(username)

    if not content_chunks:
        print("Failed to fetch user data. Exiting...")
        return

    print("\nGitHub user data loaded! You can now ask questions about this user.")
    print("(Type 'quit' to exit)")

    while True:
        query = input("\nEnter your question: ")
        if query.lower() == 'quit':
            break

        print("\nSearching for answer...")
        answer = ask_question(content_chunks, query)
        print("\nAnswer:", answer)

if __name__ == "__main__":
    main()