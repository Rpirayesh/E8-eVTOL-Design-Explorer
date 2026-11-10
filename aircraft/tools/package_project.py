"""Package the repository layout so extracted instructions stay valid.

Run from any directory with Python 3.10+. No third-party dependencies.
The archive deliberately excludes itself, Git metadata, caches and installed
developer dependencies. It preserves aircraft/ and the original Explorer.
"""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / "downloads" / "E8_Aircraft_Concept_0_1.zip"
EXCLUDED = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"}


def release_files():
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or path == DESTINATION:
            continue
        if any(part in EXCLUDED for part in relative.parts):
            continue
        if path.suffix in {".pyc", ".pyo", ".FCBak"} or path.name == ".DS_Store":
            continue
        yield path, relative.as_posix()


def main():
    # The checksum file excludes itself; all paths are relative to aircraft/.
    aircraft = ROOT / "aircraft"
    checksum_path = aircraft / "CHECKSUMS.txt"
    entries = [
        (hashlib.sha256(path.read_bytes()).hexdigest(), relative.removeprefix("aircraft/"))
        for path, relative in release_files()
        if relative.startswith("aircraft/") and path != checksum_path
    ]
    checksum_path.write_text("".join(f"{digest}  {name}\n" for digest, name in entries))
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    files = list(release_files())
    with zipfile.ZipFile(DESTINATION, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in files:
            archive.write(path, "E8_Aircraft_Concept_0_1/" + relative)
    with zipfile.ZipFile(DESTINATION) as archive:
        corrupt = archive.testzip()
        if corrupt:
            raise RuntimeError(f"Corrupt archive member: {corrupt}")
        for path, relative in files:
            if archive.read("E8_Aircraft_Concept_0_1/" + relative) != path.read_bytes():
                raise RuntimeError(f"Archive mismatch: {relative}")
    print(json.dumps({
        "archive": str(DESTINATION.relative_to(ROOT)),
        "files": len(files),
        "bytes": DESTINATION.stat().st_size,
        "sha256": hashlib.sha256(DESTINATION.read_bytes()).hexdigest(),
        "all_archived_files_match": True,
    }, indent=2))


if __name__ == "__main__":
    main()
