import os
from dotenv import load_dotenv

# Load values from .env
load_dotenv()

def check_env():
    print("GITHUB_APP_ID:", os.getenv("GITHUB_APP_ID"))
    print("GITHUB_APP_PRIVATE_KEY:", os.getenv("GITHUB_APP_PRIVATE_KEY"))
    print("GITHUB_REPOSITORY:", os.getenv("GITHUB_REPOSITORY"))
    print("OPENAI_API_KEY starts with:", (os.getenv("OPENAI_API_KEY") or "not set")[:3])

if __name__ == "__main__":
    check_env()
