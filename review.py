import os
import requests
import json
from google import genai
from google.genai import types

GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")  
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
PR_NUMBER = os.environ.get("PR_NUMBER")
LLM_API_KEY = os.environ.get("LLM_API_KEY")
GITHUB_API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com")

def get_pr_diff():
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"  
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def review_code_with_AI(diff_text):
    client = genai.Client(api_key=os.environ.get("LLM_API_KEY"))

    prompt = f"""
    Act as a Senior Software Engineer. Review the following Pull Request code diff. 
    Look for bugs, security vulnerabilities, or highly inefficient code. 
    Ignore minor styling changes unless they are critical.
    
    Return ONLY a JSON array with this exact structure for each found issue:
    [
        {{
            "file": "path/to/file",
            "line": modified_line_number,
            "review_comment": "Your review comment here"
        }}
    ]
    
    If the code is perfect and there is nothing to comment on, return an empty array [].
    
    PR DIFF:
    {diff_text}
    """

    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        reviews = json.loads(response.text)
        return reviews
    except Exception as e:
        print(f"Error while processing Gemini response: {e}")
        return []

def get_latest_commit_id():
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["head"]["sha"]

def post_review_comments(comments, commit_id):
    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/pulls/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    for comment in comments:
        payload = {
            "body": comment["review_comment"],
            "commit_id": commit_id,
            "path": comment["file"],
            "line": comment["line"],
            "side": "RIGHT"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 201:
            print(f"Comment added in {comment['file']} (Line {comment['line']})")
        else:
            print(f"Error while adding a comment in {comment['file']}: {response.text}")

if __name__ == "__main__":
    try:
        if not all([GITHUB_TOKEN, LLM_API_KEY, GITHUB_REPOSITORY, PR_NUMBER]):
            raise ValueError("Missing environment variables")

        diff = get_pr_diff()
        if not diff:
            print("No visible changes")
            exit(0)

        reviews = review_code_with_AI(diff)
        
        if reviews:
            commit_id = get_latest_commit_id()
            post_review_comments(reviews, commit_id)
        else:
            print("No new comments from the AI")
            
    except Exception as e:
        print(f"Execution failed: {e}")
        exit(1)