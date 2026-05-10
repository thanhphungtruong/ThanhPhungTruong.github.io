#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parent
TRAVEL_DIR = ROOT / "Travel"
MANIFEST = TRAVEL_DIR / "travel-media-manifest.js"

IMAGE_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

VIDEO_EXTENSIONS = {
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".m4v": "video/mp4",
    ".webm": "video/webm",
}

COUNTRY_KEY_ALIASES = {
    "philippines": "philippine",
    "republic-of-korea": "south-korea",
    "korea": "south-korea",
    "viet-nam": "vietnam",
}


def country_key(name: str) -> str:
    key = []
    last_was_dash = False
    for char in name.lower().replace("&", "and"):
        if char.isalnum():
            key.append(char)
            last_was_dash = False
        elif not last_was_dash:
            key.append("-")
            last_was_dash = True
    normalized = "".join(key).strip("-")
    return COUNTRY_KEY_ALIASES.get(normalized, normalized)


def media_type(path: Path) -> tuple[str, str] | None:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image", IMAGE_EXTENSIONS[suffix]
    if suffix in VIDEO_EXTENSIONS:
        return "video", VIDEO_EXTENSIONS[suffix]
    return None


def browser_path(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return quote(relative, safe="/")


def build_manifest() -> list[dict[str, str]]:
    items = []
    if not TRAVEL_DIR.exists():
        return items

    for country_dir in sorted(path for path in TRAVEL_DIR.iterdir() if path.is_dir()):
        for path in sorted(country_dir.rglob("*")):
            if not path.is_file():
                continue
            kind = media_type(path)
            if kind is None:
                continue
            item_type, mime = kind
            items.append(
                {
                    "country": country_dir.name,
                    "countryKey": country_key(country_dir.name),
                    "name": path.stem,
                    "src": browser_path(path),
                    "type": item_type,
                    "mime": mime,
                    "alt": f"{country_dir.name} travel media",
                }
            )
    return items


def main() -> None:
    TRAVEL_DIR.mkdir(exist_ok=True)
    data = build_manifest()
    MANIFEST.write_text(
        "window.TRAVEL_MEDIA_MANIFEST = "
        + json.dumps(data, indent=2, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {MANIFEST.relative_to(ROOT)} with {len(data)} media files.")


if __name__ == "__main__":
    main()
