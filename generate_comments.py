import os
import openai
import sys

# Azure OpenAI configuration
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = "2023-05-15"
openai.api_key = os.getenv("AZURE_OPENAI_KEY") 

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") 

def call_openai_to_comment(code, filename):
    prompt = (
        f"You are an AI assistant helping developers understand their Python sample code.\n"
        f"Add helpful inline comments to the following code file: {filename}.\n"
        f"If comments already exist, preserve them and append useful explanations.\n\n"
        f"Code:\n\n{code}\n\n# Add inline comments below:"
    )

    response = openai.ChatCompletion.create(
        engine=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful Python documentation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )

    return response['choices'][0]['message']['content']

def process_file(filepath):
    with open(filepath, 'r') as f:
        code = f.read()

    commented_code = call_openai_to_comment(code, filepath)

    with open(filepath, 'w') as f:
        f.write(commented_code)

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_comments.py updated_files.txt python-sdk")
        sys.exit(1)

    files_list_path = sys.argv[1]
    sdk_repo_path = sys.argv[2]

    with open(files_list_path, 'r') as f:
        changed_files = [line.strip() for line in f if line.endswith('.py')]

    for relative_path in changed_files:
        full_path = os.path.join(sdk_repo_path, relative_path)
        if os.path.exists(full_path):
            print(f"Processing {relative_path}...")
            process_file(full_path)
        else:
            print(f"Warning: {relative_path} not found!")

if __name__ == "__main__":
    main()
