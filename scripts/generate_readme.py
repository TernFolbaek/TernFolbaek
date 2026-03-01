#!/usr/bin/env python3
import json
import os
import subprocess
from collections import defaultdict

OWNER = os.environ.get("OWNER")  # set in workflow
OUT = "README.md"

if not OWNER:
    raise SystemExit("Missing OWNER env var")

# Use GitHub CLI to list repos + topics
cmd = [
    "gh", "repo", "list", OWNER,
    "--limit", "500",
    "--json", "name,description,url,repositoryTopics,isArchived",
]
raw = subprocess.check_output(cmd, text=True)
repos = json.loads(raw)

groups = defaultdict(list)

for r in repos:
    if r.get("isArchived"):
        continue  # skip archived, remove this line if you want them included
    topics = [t["name"] for t in (r.get("repositoryTopics") or [])]
    if not topics:
        groups["Uncategorized"].append(r)
    else:
        for t in topics:
            groups[t].append(r)

def repo_line(r):
    desc = r.get("description") or ""
    if desc:
        return f"- [{r['name']}]({r['url']}) — {desc}"
    return f"- [{r['name']}]({r['url']})"

with open(OUT, "w", encoding="utf-8") as f:
    f.write(f"# {OWNER} Repositories\n\n")
    f.write("The below list is auto generated daily. It categorizes each repo based on the topics I set on the repo._\n\n")

    for topic in sorted(groups.keys(), key=lambda x: (x == "Uncategorized", x.lower())):
        f.write(f"## {topic}\n\n")
        for r in sorted(groups[topic], key=lambda x: x["name"].lower()):
            f.write(repo_line(r) + "\n")
        f.write("\n")

print(f"Wrote {OUT}")
