#!/usr/bin/env python3
"""
Promote 70 articles from the queue to the published manifest so the site
ships with exactly 100 published. The remaining ~430 stay queued, drip-
publishing one per day via cron.

- Picks 70 slugs from the queue with the EARLIEST publish_at dates (so the
  publish dates remain in calendar order; the existing 30 already occupy
  Apr 1..Apr 30 2026, the 70 promoted ones occupy May 2 2026..Jul 10 2026
  approximately, one per day, no two on the same day).
- Each promoted article keeps its body (already 1800+ words, gate-passed).
- The remaining queued articles get their publish_at re-staggered to start
  AFTER the promoted block ends, so the cron continues to drip one per day.
- Output: re-writes preview-manifest.json (100 published) and
  queue-manifest.json (the rest, status='queued').
"""

import json
import os
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB_PATH = os.path.join(ROOT, "client", "public", "content", "preview-manifest.json")
QUE_PATH = os.path.join(ROOT, "client", "public", "content", "queue-manifest.json")

CAP = 100  # PUBLISH_CAP

with open(PUB_PATH) as f:
    pub = json.load(f)
with open(QUE_PATH) as f:
    que = json.load(f)

pub_arts = pub.get("articles", pub.get("items", []))
que_arts = que.get("articles", que.get("items", []))

print(f"BEFORE: published={len(pub_arts)} queued={len(que_arts)}")

need = CAP - len(pub_arts)
assert need >= 0, f"Already over cap: {len(pub_arts)} > {CAP}"
print(f"Need to promote {need} articles from queue to published")

# Sort queue by publish_at ASC (earliest first) so promoted slugs stay
# chronologically adjacent to the existing 30 (Apr 1..Apr 30 2026).
def get_pub_at(a):
    return a.get("published_at") or a.get("publish_at") or "9999-12-31T00:00:00Z"

que_arts.sort(key=get_pub_at)

# Pick the first `need` queue rows; promote them.
promoted = que_arts[:need]
remaining = que_arts[need:]

# Stagger the promoted publish dates: start the day after the latest
# already-published date, one per day, never two on the same day.
latest_pub_str = max((a.get("published_at") or a.get("publish_at", "")) for a in pub_arts)
latest_pub = datetime.fromisoformat(latest_pub_str.replace("Z", "+00:00"))
next_day = latest_pub + timedelta(days=1)

for i, a in enumerate(promoted):
    new_date = next_day + timedelta(days=i)
    iso = new_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    a["published_at"] = iso
    if "publish_at" in a:
        a["publish_at"] = iso
    a["last_modified_at"] = iso
    a["status"] = "published"

# Re-stagger the remaining queue: start the day after the last promoted date.
last_promoted = next_day + timedelta(days=len(promoted) - 1)
queue_start = last_promoted + timedelta(days=1)
for i, a in enumerate(remaining):
    new_date = queue_start + timedelta(days=i)
    iso = new_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    a["published_at"] = iso
    if "publish_at" in a:
        a["publish_at"] = iso
    a["status"] = "queued"

# Compose new published manifest = original 30 + 70 promoted
new_pub_arts = list(pub_arts) + promoted
new_pub = dict(pub)
new_pub["articles"] = new_pub_arts
new_pub["count"] = len(new_pub_arts)
new_pub["last_built"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

new_que = dict(que)
new_que["articles"] = remaining
new_que["count"] = len(remaining)
new_que["last_built"] = new_pub["last_built"]

with open(PUB_PATH, "w") as f:
    json.dump(new_pub, f, indent=2)
with open(QUE_PATH, "w") as f:
    json.dump(new_que, f, indent=2)

print(f"AFTER:  published={len(new_pub_arts)} queued={len(remaining)}")
print(f"Published date range: {get_pub_at(new_pub_arts[0])[:10]} .. {get_pub_at(new_pub_arts[-1])[:10]}")
if remaining:
    print(f"Queue date range:     {get_pub_at(remaining[0])[:10]} .. {get_pub_at(remaining[-1])[:10]}")
print("OK")
