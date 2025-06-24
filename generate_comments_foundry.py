import os
import sys
import requests

# Set environment values
API_KEY = os.getenv("AZURE_AI_FOUNDRY_KEY")
ENDPOINT = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")  
DEPLOYMENT_NAME = os.getenv("AZURE_AI_FOUNDRY_DEPLOYMENT_NAME") 

headers = {
    "Content-Type": "application/json",
    "api-key": API_KEY
}

def call_foundry_to_comment(code, filename):
    prompt = (
        f"You are an AI assistant helping developers understand their Python sample code.\n"
        f"Add helpful inline comments to the following code file: {filename}.\n"
        f"If comments already exist, preserve them and append useful explanations.\n\n"
        f"Code:\n\n{code}\n\n# Add inline comments below:"
    )

    payload = {
        "messages": [
            {"role": "system", "content": "You are a helpful Python documentation assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "top_p": 0.95,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "max_tokens": 1000
    }

    url = f"{ENDPOINT}/openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2023-05-15"
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print(f"Request failed: {response.status_code}\n{response.text}")
        raise Exception("Foundry API call failed.")

    result = response.json()
    return result["choices"][0]["message"]["content"]

def process_file(filepath):
    print(f"Reading file: {filepath}")
    with open(filepath, 'r') as f:
        code = f.read()

    commented_code = call_foundry_to_comment(code, filepath)

    with open(filepath, 'w') as f:
        f.write(commented_code)

    print(f"Finished writing comments to: {filepath}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_comments.py updated_files.txt python-sdk")
        sys.exit(1)

    files_list_path = sys.argv[1]
    sdk_repo_path = sys.argv[2]

    print(f"\nReading list of changed files from: {files_list_path}")

    with open(files_list_path, 'r') as f:
        changed_files = [line.strip() for line in f if line.strip().endswith('.py')]

    print(f"\nDetected {len(changed_files)} .py files to process:\n" + "\n".join(changed_files))

    for relative_path in changed_files:
        full_path = os.path.join(sdk_repo_path, relative_path)
        if os.path.exists(full_path):
            print(f"Processing {relative_path}...")
            process_file(full_path)
        else:
            print(f"Skipping {relative_path} - file not found at {full_path}")

if __name__ == "__main__":
    main()
