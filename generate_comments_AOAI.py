import os
import sys
import requests

API_KEY = os.getenv("AZURE_OPENAI_KEY")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT").rstrip("/") + "/"  
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # gpt-4o

# Function to make the API call; builds URL for calling Azure OpenAI's gpt-4o; headers authenticate the request with the AOAI key
def call_openai_to_comment(code: str, filename: str) -> str:
    url = f"{ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2025-01-01-preview"
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    
    prompt = f"""
You are a code-commenting assistant.

Task:
1. Insert brief, helpful #-style comments into the Python code below.  
2. Each comment must be shorter than the line or block it explains.  
3. **Return ONLY the updated source code** — no markdown fences, no extra text.

### BEGIN FILE
{code}
### END FILE
"""

    # Standard chat format payload. max_tokens=1000 can be increased if files are long
    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful coding assistant who comments Python code clearly."},
            {"role": "user", "content": prompt}
         ],
         "temperature": 0.3,
         "max_tokens": 1000,
     }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        print("Request failed:", response.status_code)
        print(response.text)
        raise Exception("OpenAI API call failed.")

def process_file(filepath: str, sdk_repo_folder: str):
    full_path = os.path.join(sdk_repo_folder, filepath)
    print(f"Reading file: {full_path}")
    with open(full_path, "r") as f:
        code = f.read()

    commented_code = call_openai_to_comment(code, filepath)

    with open(full_path, "w") as f:
        f.write(commented_code)

def main():
    updated_files_list = sys.argv[1]  # Path to /tmp/updated_files.txt
    sdk_repo_folder = sys.argv[2]     # Usually "python-sdk"

    print(f"Reading list of changed files from: {updated_files_list}")

    with open(updated_files_list, "r") as f:
        files = [line.strip() for line in f if line.strip().endswith(".py")]

    print(f"Detected {len(files)} .py files to process:")
    for fpath in files:
        print(fpath)
        process_file(fpath, sdk_repo_folder)

if __name__ == "__main__":
    main()
