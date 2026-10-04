import json
import urllib.request
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN_HERE")

gist_payload = {
    "description": "Alpha Root Kernel Consensus Manifest & Sync Log",
    "public": True,
    "files": {
        "alpha_root_manifest.json": {
            "content": json.dumps({
                "project": "Alpha Root Kernel",
                "version": "1.0.4-stable",
                "path_vector": "04/04/00/00",
                "status": "synchronized"
            }, indent=2)
        }
    }
}

req = urllib.request.Request(
    "https://api.github.com/gists",
    data=json.dumps(gist_payload).encode("utf-8"),
    headers={
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        print(f"\nGist successfully created!\nURL: {res_data['html_url']}\n")
except Exception as e:
    print(f"\nError creating Gist: {e}\n")
