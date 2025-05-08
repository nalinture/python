import requests
import re
import base64

# Configuration
GITHUB_TOKEN = 'your_enterprise_token'  # Replace with your GitHub Enterprise token
BASE_API_URL = 'https://github.dev.tn.net/api/v3'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

# Function to find providers in a given repo
def find_providers(owner, repo):
    url = f"{BASE_API_URL}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error accessing {owner}/{repo}: {resp.status_code}")
        return []

    providers = set()
    tree = resp.json().get('tree', [])

    for item in tree:
        if item['type'] == 'blob' and item['path'].endswith('.tf'):
            content_url = f"{BASE_API_URL}/repos/{owner}/{repo}/contents/{item['path']}"
            content_resp = requests.get(content_url, headers=HEADERS)
            if content_resp.status_code != 200:
                continue
            content_json = content_resp.json()

            if content_json.get('encoding') == 'base64':
                decoded = base64.b64decode(content_json['content']).decode('utf-8')
                matches = re.findall(r'provider\s+"([^"]+)"', decoded)
                providers.update(matches)

    return list(providers)

# Read repo URLs and check for providers
with open('repos_with_tf.txt') as infile, open('repo_providers.txt', 'w') as outfile:
    for line in infile:
        repo_url = line.strip()
        if not repo_url:
            continue
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 2:
            continue
        owner, repo = parts[-2], parts[-1]
        providers = find_providers(owner, repo)
        if providers:
            result = f"{repo_url} : {', '.join(providers)}"
            print(result)
            outfile.write(result + '\n')
