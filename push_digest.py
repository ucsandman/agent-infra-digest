#!/usr/bin/env python3
"""Push agent-infra-digest commits to ucsandman/agent-infra-digest via the GitHub
git-database API, using the custom.github connector surrogate.

The connector credential never touches this script: authd swaps the surrogate
on egress. Each local commit SHA given on argv is recreated parented to the
remote HEAD (or to the previous published commit), so clones fast-forward
with a plain `git pull` (no force). Only the listed commits move; nothing else
in the remote history is touched.

Usage: python3 push_digest.py <local-sha> [<local-sha> ...]
"""
import base64
import json
import subprocess
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
import dynamic_credentials as dc  # noqa: E402

OWNER, REPO = "ucsandman", "agent-infra-digest"
API = f"https://api.github.com/repos/{OWNER}/{REPO}"
REPO_DIR = "/home/hatch/workspace/agent-infra-digest"
HEADERS = {
    "User-Agent": "agent-infra-digest-publish",
    "Accept": "application/vnd.github+json",
    "Content-Type": "application/json",
}


def api(method, url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    dc.add_surrogate_to_request(req, "custom.github", allowed_hosts=["api.github.com"])
    try:
        resp = urllib.request.urlopen(req, timeout=30)
        body = resp.read()
        return resp.status, (json.loads(body.decode()) if body else None)
    except urllib.error.HTTPError as e:
        detail = e.read(500).decode("utf-8", "replace")[:300]
        raise SystemExit(f"HTTP {e.code} on {method} {url}\n{detail}")


def git(*args):
    return subprocess.run(
        ["git", "-C", REPO_DIR, *args], capture_output=True, check=True
    ).stdout


def publish_tree(full_sha):
    """Recreate the full tree of local commit full_sha on the remote."""
    tree_entries = []
    for line in git("ls-tree", "-r", full_sha).decode().splitlines():
        mode, typ, sha, path = line.split(None, 3)
        assert typ == "blob", line
        content = git("cat-file", "blob", sha)
        _, blob = api(
            "POST", API + "/git/blobs",
            {"content": base64.b64encode(content).decode(), "encoding": "base64"},
        )
        tree_entries.append(
            {"path": path, "mode": mode, "type": "blob", "sha": blob["sha"]}
        )
    _, tree = api("POST", API + "/git/trees", {"tree": tree_entries})
    return tree["sha"]


def main():
    commits = [git("rev-parse", c).decode().strip() for c in sys.argv[1:]]
    assert commits, "usage: push_digest.py <local-sha> [...]"

    _, repo = api("GET", API)
    print("repo:", repo["full_name"])
    _, existing = api("GET", API + "/git/refs/heads/main")
    parent = existing["object"]["sha"]
    print("remote HEAD:", parent[:7])

    for full_sha in commits:
        message = git("log", "-1", "--format=%B", full_sha).decode().strip()
        tree_sha = publish_tree(full_sha)
        _, commit = api(
            "POST", API + "/git/commits",
            {"message": message, "tree": tree_sha, "parents": [parent],
             "author": {"name": "Sparrow", "email": "sparrow@practicalsystems.io"}},
        )
        parent = commit["sha"]
        print(f"commit {message[:28]!r}:", parent[:7])

    _, ref = api("PATCH", API + "/git/refs/heads/main", {"sha": parent, "force": False})
    print("ref:", ref["ref"], "->", parent[:7])


if __name__ == "__main__":
    main()
