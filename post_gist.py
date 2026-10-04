import json
import urllib.request
import os
import sys

token = os.getenv("GITHUB_TOKEN")
if not token or token.startswith("ghp_YOUR"):
    print("Error: GITHUB_TOKEN is not set properly.")
    print("Run: export GITHUB_TOKEN=\"ghp_yourActualTokenHere\"")
    sys.exit(1)

gist_payload = {
    "description": "Alpha Root Kernel Consensus Manifest",
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
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "Termux-Gist-Uploader"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        print(f"\n[Success] Gist posted to cornbread78!\nURL: {res_data['html_url']}\n")
except Exception as e:
    print(f"\n[Error] {e}\n")
