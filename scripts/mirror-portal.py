#!/usr/bin/env python3
"""
Mirror the deployed Accelerate BASSO Resource Portal into the portal/
directory so it is served from this site's domain.

The portal is a Next.js static export deployed at
https://accelerate-basso.github.io/portal/ with basePath /portal, so every
internal link and asset path is domain-relative (/portal/...). Copying the
deployed files verbatim lets the same site run at
https://accelerate-basso.regenstrief.org/portal/.

Downloads only — no code from the portal repository is executed. Starting
from the known routes, every downloaded text file is scanned for /portal/...
references and the crawl repeats until no new files are found.

Usage:
    python3 scripts/mirror-portal.py [--base-url URL] [--out DIR]
"""

import argparse
import re
import shutil
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

try:  # some local Python installs lack system root certificates
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()

DEFAULT_BASE = "https://accelerate-basso.github.io/portal"

# Routes that exist even if nothing links to them.
SEED_PATHS = [
    "index.html",
    "index.txt",
    "resources.html",
    "resources.txt",
    "contribute.html",
    "contribute.txt",
    "404.html",
    "404.txt",
    "favicon.ico",
]

# /portal/... references inside HTML, JS, CSS, and RSC payloads.
REF_PATTERN = re.compile(r"/portal/([A-Za-z0-9_\-./~%]+)")
# Chunk paths that Next.js sometimes references without the basePath prefix.
NEXT_PATTERN = re.compile(r"(?<![A-Za-z0-9_/-])(_next/static/[A-Za-z0-9_\-./~%]+)")

TEXT_EXTENSIONS = {".html", ".txt", ".js", ".css", ".json", ".xml", ".svg", ".map"}


def fetch(url: str) -> bytes | None:
    request = urllib.request.Request(url, headers={"User-Agent": "portal-mirror"})
    try:
        with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
            return response.read()
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return None
        raise


def normalize(path: str) -> str:
    path = urllib.parse.unquote(path.split("?")[0].split("#")[0])
    return path.strip("/").rstrip(".")


def candidates_for(path: str) -> list[str]:
    """File names a discovered reference may correspond to on the server."""
    if "." in path.rsplit("/", 1)[-1]:
        return [path]
    # Extensionless route link (e.g. /portal/resources): the static export
    # stores it as resources.html, and its RSC payload as resources.txt.
    return [f"{path}.html", f"{path}.txt"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--out", default="portal")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    import pathlib

    out_dir = pathlib.Path(args.out)
    if out_dir.exists():
        shutil.rmtree(out_dir)

    queue = list(SEED_PATHS)
    seen: set[str] = set(queue)
    saved: list[str] = []
    missing: list[str] = []

    while queue:
        path = queue.pop(0)
        content = fetch(f"{base}/{path}")
        if content is None:
            missing.append(path)
            continue

        target = out_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        saved.append(path)

        suffix = "." + path.rsplit(".", 1)[-1] if "." in path else ""
        if suffix not in TEXT_EXTENSIONS:
            continue
        text = content.decode("utf-8", errors="ignore")
        refs = set(REF_PATTERN.findall(text)) | set(NEXT_PATTERN.findall(text))
        for ref in refs:
            ref = normalize(ref)
            if not ref:
                continue
            for candidate in candidates_for(ref):
                if candidate not in seen:
                    seen.add(candidate)
                    queue.append(candidate)

    print(f"Mirrored {len(saved)} files from {base} into {out_dir}/")
    if missing:
        print(f"{len(missing)} referenced paths returned 404 (skipped):")
        for path in sorted(missing):
            print(f"  {path}")
    if "index.html" not in saved:
        print("ERROR: index.html was not downloaded", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
