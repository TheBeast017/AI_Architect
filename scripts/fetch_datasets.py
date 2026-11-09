#!/usr/bin/env python3
"""Dataset registry helper (doc 17.6). Never downloads without --yes. Writes a manifest entry per download.

  python scripts/fetch_datasets.py list
  python scripts/fetch_datasets.py zenodo-files zenodo_topopt_v2      # list files + sizes (needs network)
  python scripts/fetch_datasets.py download <direct-file-url> --id my_id --yes
STATUS: list works offline; zenodo-files / download are UNTESTED here (sandbox had no access) - see plan.md Phase 2.
"""
from __future__ import annotations
import argparse, hashlib, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = json.loads((ROOT / "datasets" / "sources.json").read_text())["sources"]
RAW = ROOT / "engineering-agent-data" / "raw"
MANIFEST = ROOT / "engineering-agent-data" / "manifests" / "datasets_manifest.jsonl"


def cmd_list(_):
    for s in SRC:
        print(f"[stage {s['stage']}] {s['id']:<18} {s['kind']:<12} {s['url']}\n    {s.get('notes','')}")


def cmd_zenodo(a):
    s = next((x for x in SRC if x["id"] == a.id), None)
    if not s or "zenodo_record" not in s:
        sys.exit("not a zenodo source")
    with urllib.request.urlopen(f"https://zenodo.org/api/records/{s['zenodo_record']}") as r:
        data = json.load(r)
    print("license:", data.get("metadata", {}).get("license"))
    for f in data.get("files", []):
        print(f"{f['key']:<50} {f['size']/1e6:>10.1f} MB  {f['links']['self']}")


def cmd_download(a):
    req = urllib.request.Request(a.url, method="HEAD")
    with urllib.request.urlopen(req) as r:
        size = int(r.headers.get("Content-Length", 0))
    print(f"size: {size/1e6:.1f} MB")
    if not a.yes:
        sys.exit("dry run - re-run with --yes after checking the license and size")
    RAW.mkdir(parents=True, exist_ok=True)
    dest = RAW / (a.id + "_" + Path(a.url).name)
    h = hashlib.sha256()
    with urllib.request.urlopen(a.url) as r, open(dest, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk); h.update(chunk)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST, "a") as m:
        m.write(json.dumps({"id": a.id, "url": a.url, "file": str(dest), "bytes": dest.stat().st_size,
                            "sha256": h.hexdigest(), "accessed": time.strftime("%Y-%m-%d"),
                            "license": "FILL IN - see engineering-agent-data/licenses/"}) + "\n")
    print("saved", dest)


p = argparse.ArgumentParser()
sp = p.add_subparsers(dest="c", required=True)
sp.add_parser("list").set_defaults(f=cmd_list)
z = sp.add_parser("zenodo-files"); z.add_argument("id"); z.set_defaults(f=cmd_zenodo)
d = sp.add_parser("download"); d.add_argument("url"); d.add_argument("--id", required=True)
d.add_argument("--yes", action="store_true"); d.set_defaults(f=cmd_download)
a = p.parse_args(); a.f(a)
