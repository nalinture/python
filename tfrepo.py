import requests

GITHUB_TOKEN = 'your_enterprise_token'
BASE_API_URL = 'https://github.dev.tn.net/api/v3'
HEADERS = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}

def has_tf_file(owner, repo):
    url = f"{BASE_API_URL}/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    resp = requests.get(url, headers=HEADERS)
    if resp.status_code != 200:
        print(f"Error accessing {owner}/{repo}: {resp.status_code}")
        return False
    tree = resp.json().get('tree', [])
    return any(item['path'].endswith('.tf') for item in tree if item['type'] == 'blob')

with open('gitrepolist.txt') as file:
    for line in file:
        repo_url = line.strip()
        if not repo_url:
            continue
        # Extract owner and repo name from the URL
        parts = repo_url.rstrip('/').split('/')
        if len(parts) < 2:
            continue
        owner, repo = parts[-2], parts[-1]
        if has_tf_file(owner, repo):
            print(repo_url)
