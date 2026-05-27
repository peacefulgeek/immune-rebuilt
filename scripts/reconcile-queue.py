#!/usr/bin/env python3
"""Reconcile the queue manifest against the published manifest.

- Drops any slug already present in preview-manifest.json (the 100 published).
- Re-assigns publish_at dates so the queue starts the day AFTER the last published
  date (one article per day, no gaps, no overlap with published).
- Preserves order from the original queue manifest.
- Writes back to client/public/content/queue-manifest.json.

Idempotent.
"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "client" / "public" / "content"
PUB = CONTENT / "preview-manifest.json"
QUE = CONTENT / "queue-manifest.json"

pm = json.loads(PUB.read_text(encoding="utf-8"))
qm = json.loads(QUE.read_text(encoding="utf-8"))

published = pm.get("articles") or pm.get("items") or []
queue = qm.get("items") or qm.get("articles") or []

published_slugs = {a["slug"] for a in published}
published_dates = sorted(
    {(a.get("publish_at") or a.get("published_at") or "")[:10] for a in published}
)
last_published_day = published_dates[-1]
y, m, d = (int(x) for x in last_published_day.split("-"))
start = date(y, m, d) + timedelta(days=1)

# Drop slugs that overlap with published.
queue_filtered = [a for a in queue if a["slug"] not in published_slugs]

dropped = len(queue) - len(queue_filtered)

# Reassign sequential daily dates, one per day, starting at `start`.
for i, a in enumerate(queue_filtered):
    d = (start + timedelta(days=i)).isoformat()
    iso = f"{d}T09:00:00.000Z"
    a["publish_at"] = iso
    if "published_at" in a:
        a["published_at"] = iso

qm_out = dict(qm)
if "items" in qm:
    qm_out["items"] = queue_filtered
else:
    qm_out["articles"] = queue_filtered

QUE.write_text(json.dumps(qm_out, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"[reconcile] published = {len(published)}")
print(f"[reconcile] queue before = {len(queue)}, dropped (already published) = {dropped}, queue after = {len(queue_filtered)}")
print(f"[reconcile] new queue date range = {queue_filtered[0]['publish_at'][:10]} .. {queue_filtered[-1]['publish_at'][:10]}")
print(f"[reconcile] total authored articles = {len(published) + len(queue_filtered)}")
