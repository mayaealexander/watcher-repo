import os
import sys
from openai import AzureOpenAI

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-05-15",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

def call_openai_to_comment(code, filename):
    prompt = (
        f"You are an AI assistant helping developers understand their Python sample code.\n"
        f"Add helpful inline comments to the following code file: {filename}.\n"
        f"If comments already exist, preserve them and append useful explanations.\n\n"
        f"Code:\n\n{code}\n\n# Add inline comments below:"
    )
    print(f"\nCalling OpenAI for file: {filename}...")

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful Python documentation assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
    )

    result = response.choices[0].message.content
    print(f"LLM response for {filename}:\n{result[:500]}...\n")
    return result

def process_file(filepath):
    print(f"Reading file: {filepath}")
    with open(filepath, 'r') as f:
        code = f.read()

    commented_code = call_openai_to_comment(code, filepath)

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
