import sys
import json
import base64
import requests

def get_repo_files(owner, repo, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    tree = response.json().get('tree', [])
    return [item['path'] for item in tree if item['path'].endswith('.tf')]

def get_file_content(owner, repo, path, token):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None
    content = response.json().get('content', '')
    return base64.b64decode(content).decode('utf-8', errors='ignore')

def extract_providers(file_content):
    providers = set()
    for line in file_content.splitlines():
        line = line.strip()
        if line.startswith("provider") and "{" in line:
            parts = line.split('"')
            if len(parts) > 1:
                providers.add(parts[1])
    return list(providers)

def process_repo(repo_url, token):
    # Extract owner/repo from URL
    try:
        parts = repo_url.strip().split("github.com/")[1].strip("/").split("/")
        owner, repo = parts[0], parts[1]
    except IndexError:
        return {"error": "Invalid URL format"}

    tf_files = get_repo_files(owner, repo, token)
    if tf_files is None:
        return {"error": "Unable to access repo or list files"}

    providers = set()
    for tf_file in tf_files:
        content = get_file_content(owner, repo, tf_file, token)
        if content:
            providers.update(extract_providers(content))

    return {"providers": list(providers)}

def main(input_file, output_file, token):
    with open(input_file, 'r') as f:
        repo_urls = [line.strip() for line in f if line.strip()]

    results = {}
    for url in repo_urls:
        print(f"Processing: {url}")
        results[url] = process_repo(url, token)

    with open(output_file, 'w') as out_file:
        json.dump(results, out_file, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 github_provider_extractor.py <input_file> <output_file> <github_token>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
