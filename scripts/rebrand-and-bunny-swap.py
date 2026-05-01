#!/usr/bin/env python3
"""Rewrite the codebase from 'Immune Rebuilt' / immunerebuilt.com
to 'Immune Rebuilt' / immunerebuilt.com, and swap every CloudFront /manus-storage
hero URL to its Bunny CDN equivalent. Then delete all local images.

Bunny URLs follow this pattern:
  https://conscious-elder.b-cdn.net/immune-rebuilt/<filename>.webp

The pull-zone hostname is overridable via the BUNNY_PULL_ZONE_URL env at
runtime; the file URL we write is the production URL right now.
"""
from __future__ import annotations
import json, re, os, sys
from pathlib import Path

ROOT = Path("/home/ubuntu/autoimmune-reset")
BUNNY_BASE = "https://conscious-elder.b-cdn.net/immune-rebuilt"

REBRAND_PAIRS = [
    ("Immune Rebuilt", "Immune Rebuilt"),
    ("immune rebuilt", "immune rebuilt"),
    ("immune-rebuilt", "immune-rebuilt"),  # only in user-visible text contexts; we'll be careful below
    ("immunerebuilt.com", "immunerebuilt.com"),
    ("IMMUNEREBUILT.COM", "IMMUNEREBUILT.COM"),
    ("ROOT-CAUSE WRITING ON AUTOIMMUNE HEALING", "ROOT-CAUSE WRITING ON AUTOIMMUNE HEALING"),
    ("immunerebuilt.com", "immunerebuilt.com"),
]
# Files we DO NOT touch with the immune-rebuilt → immune-rebuilt rebrand
# because the project directory is still /home/ubuntu/autoimmune-reset (filesystem path)
# and node_modules / git internals must stay literal.
SKIP_DIRS = {"node_modules", ".git", "dist", ".manus-logs", "patches"}

# ---------- 1. Build name→URL map for the local files ----------
def filename_only(p: str) -> str:
    return os.path.basename(p)

def cloudfront_to_bunny(url: str) -> str:
    """Take a CloudFront generate_image URL and map it back to its base webp filename
    (everything before the trailing -<22charSuffix>.webp), then build the Bunny URL."""
    fn = filename_only(url)  # e.g. art-01-rootcauses-Hp9ZeSmBpRNwLD8tBzakXP.webp
    if not fn.endswith(".webp"):
        return url
    base = re.sub(r"-[A-Za-z0-9]{22}\.webp$", ".webp", fn)
    return f"{BUNNY_BASE}/{base}"

def manus_to_bunny(path: str) -> str:
    """https://conscious-elder.b-cdn.net/immune-rebuilt/ar-hero-meadow.webp → bunny equivalent."""
    fn = filename_only(path)
    if not fn.endswith(".webp"):
        return path
    base = re.sub(r"_[a-f0-9]{8}\.webp$", ".webp", fn)
    return f"{BUNNY_BASE}/{base}"

# ---------- 2. Walk the tree ----------
def iter_files():
    for p in ROOT.rglob("*"):
        if not p.is_file():
            continue
        if any(seg in SKIP_DIRS for seg in p.parts):
            continue
        if p.suffix in {".png", ".webp", ".jpg", ".jpeg", ".ico"}:
            continue
        yield p

# ---------- 3. URL substitution ----------
URL_PATTERNS = [
    (re.compile(r'https://d2xsxph8kpxj0f\.cloudfront\.net/[^"\s\)]+\.webp'), cloudfront_to_bunny),
    (re.compile(r'/manus-storage/[A-Za-z0-9_\-]+\.webp'), manus_to_bunny),
]

def fix_text(t: str) -> tuple[str, int]:
    n = 0
    for pat, fn in URL_PATTERNS:
        def sub(m):
            nonlocal n
            out = fn(m.group(0))
            if out != m.group(0):
                n += 1
            return out
        t = pat.sub(sub, t)
    # Rebrand strings (apply only outside of literal filesystem paths and shell file paths)
    for old, new in REBRAND_PAIRS:
        if old in t:
            # Avoid touching the filesystem project directory path
            if old == "immune-rebuilt":
                # Substitute only in URL-ish or descriptive contexts (not filesystem paths)
                # We use a negative-lookbehind for /home/ubuntu/
                new_t = re.sub(r'(?<!/home/ubuntu/)immune-rebuilt', new, t)
                if new_t != t:
                    n += 1
                    t = new_t
            else:
                cnt = t.count(old)
                if cnt:
                    t = t.replace(old, new)
                    n += cnt
    return t, n

# ---------- 4. Apply ----------
total_files = 0
total_changes = 0
for p in iter_files():
    try:
        original = p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, IsADirectoryError):
        continue
    new, n = fix_text(original)
    if n:
        p.write_text(new, encoding="utf-8")
        total_files += 1
        total_changes += n
        print(f"  {p.relative_to(ROOT)}: {n}")
print(f"--- rewrote {total_changes} substitutions across {total_files} files")
