# AI-code-reviewer
Automated AI code reviewer built with Python, GitHub Actions, GitHub API and Gemini 3.8 Flash API.


<img width="800" height="450" alt="bettergif" src="https://github.com/user-attachments/assets/6271ef49-1f7f-4757-9d66-f330160f34df" />


## How It Works
1. Open a Pull Request or push new commits to an existing PR.
2. GitHub Actions runs the `review.yml` workflow.
3. The Python script `review.py` extracts the new code using the GitHub API and sends it to Gemini, acting according to a specific prompt.
4. The script parses the JSON and posts inline comments on the PR for any detected issues.


If you want to try this project on your own:
Copy the `review.py` script and the `.github/workflows/review.yml` file into your repository.
Get an API Key from your preferred AI, and add it to your repository as a secret named `LLM_API_KEY`
