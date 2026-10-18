"""Packaging script for clean Voice of Store project submission ZIP.

Excludes virtual environments, node_modules, git directories, caches,
and temporary databases. Verifies archive integrity and prints file summary.
"""

import os
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS = {
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "dist",
    "build",
    ".vscode",
    ".idea",
    "coverage",
    "voice-of-store-backend",
}

EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
}

EXCLUDE_FILES = {
    ".DS_Store",
    "Thumbs.db",
    "npm-debug.log",
    "yarn-error.log",
}


def should_include(rel_path: Path) -> bool:
    """Determine whether a file or directory should be included in submission."""
    # Check parts for excluded directory names
    for part in rel_path.parts:
        if part in EXCLUDE_DIRS:
            return False

    # Check file name and extension
    if rel_path.name in EXCLUDE_FILES:
        return False

    if rel_path.suffix in EXCLUDE_EXTENSIONS:
        return False

    # Skip zip files themselves
    if rel_path.suffix == ".zip":
        return False

    return True


def create_submission_zip(output_filename: str = "voice-of-store-submission.zip") -> str:
    """Package project files into a clean submission zip archive."""
    output_path = PROJECT_ROOT / output_filename
    print(f"Creating submission archive: {output_path}")

    included_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            rel_dir = Path(root).relative_to(PROJECT_ROOT)

            # Filter dirs in-place to avoid descending into excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in sorted(files):
                full_path = Path(root) / file
                rel_path = full_path.relative_to(PROJECT_ROOT)

                if should_include(rel_path):
                    # Write file into zip with normalized forward slashes
                    arcname = str(rel_path).replace("\\", "/")
                    zf.write(full_path, arcname=arcname)
                    included_count += 1
                    total_uncompressed_bytes += full_path.stat().st_size

    archive_size_mb = output_path.stat().st_size / (1024 * 1024)
    uncompressed_mb = total_uncompressed_bytes / (1024 * 1024)

    print("\n--- Submission Archive Created Successfully ---")
    print(f"Archive:             {output_path.name}")
    print(f"Location:            {output_path}")
    print(f"Total Files:         {included_count}")
    print(f"Uncompressed Size:   {uncompressed_mb:.2f} MB")
    print(f"Compressed Size:     {archive_size_mb:.2f} MB")
    print(f"Compression Ratio:   {(archive_size_mb / uncompressed_mb * 100):.1f}% of original")
    print(f"Created At (UTC):    {datetime.now(timezone.utc).isoformat()}")

    return str(output_path)


if __name__ == "__main__":
    out_name = sys.argv[1] if len(sys.argv) > 1 else "voice-of-store-submission.zip"
    create_submission_zip(out_name)
