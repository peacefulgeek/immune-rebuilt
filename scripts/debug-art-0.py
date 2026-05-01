#!/usr/bin/env python3
import sys, re, importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

spec = importlib.util.spec_from_file_location("b", ROOT / "scripts" / "build-five-hundred-queue.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Use SPECS, render_body, gate_check
specs = mod.SPECS
sp0 = specs[0]
print("slug:", sp0["slug"])
print("category:", sp0["category"])

body, excerpt = mod.render_body(sp0, 0, "2025-05-01T09:00:00Z")
hrefs = re.findall(r'href="[^"]+"', body)
for h in hrefs:
    print("  HREF:", h)
print()
print("len:", len(body))
print("words:", mod.word_count(body))
ok, reasons = mod.gate_check(body)
print("gate ok:", ok)
print("reasons:", reasons)
