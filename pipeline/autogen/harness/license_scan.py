"""Copyleft license scan of agent-generated code (SRS Spec 4.3).

Before a run is archived or published, every file the agent added or changed
is searched for copyleft license markers: SPDX identifiers, the `license`
field of a package manifest, and the titles of the license texts themselves.

The scan is fail-closed, like the secret scan of Spec 1.5. A run is
publishable only when the scan completed and found nothing:

    clean                the scan completed and found no copyleft marker
    flagged              at least one file carries a copyleft marker
    scanner_unavailable  the scan could not complete, so nothing is known

A clean result is evidence about the files scanned. It is not legal
clearance (SRS Legal Considerations, L2).

The scan reads files as text on the host and never executes them. It does
not call git, so nothing inside the candidate's `.git` directory can
influence it.
"""

from __future__ import annotations

import hashlib
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

CLEAN = "clean"
FLAGGED = "flagged"
UNAVAILABLE = "scanner_unavailable"

# Directories that hold no agent-authored source.
SKIP_DIRS = frozenset({".git", "node_modules", ".venv", "__pycache__"})

# Only the head of a very large file is searched; license notices sit there.
MAX_BYTES = 1_000_000

_SPDX_IDS = {
    "AGPL": r"AGPL",
    "LGPL": r"LGPL",
    "GPL": r"GPL",
    "MPL": r"MPL",
    "EPL": r"EPL",
    "CDDL": r"CDDL",
    "EUPL": r"EUPL",
    "OSL": r"OSL",
    "CC-BY-SA": r"CC-BY-SA",
}

_TITLES = {
    "AGPL": r"GNU\s+Affero\s+General\s+Public\s+License",
    "LGPL": r"GNU\s+(?:Lesser|Library)\s+General\s+Public\s+License",
    "GPL": r"GNU\s+General\s+Public\s+License",
    "MPL": r"Mozilla\s+Public\s+License",
    "EPL": r"Eclipse\s+Public\s+License",
    "CDDL": r"Common\s+Development\s+and\s+Distribution\s+License",
    "EUPL": r"European\s+Union\s+Public\s+Licen[cs]e",
    "OSL": r"Open\s+Software\s+License",
    "CC-BY-SA": r"Creative\s+Commons\s+Attribution[-\s]ShareAlike",
}


def _compile() -> list[tuple[str, re.Pattern[str]]]:
    patterns = []
    for name in _SPDX_IDS:
        spdx = _SPDX_IDS[name]
        patterns.append(
            (
                name,
                re.compile(
                    # An SPDX tag, or the license field of a package manifest.
                    rf"(?:SPDX-License-Identifier\s*:|\"license\"\s*:\s*\")[\s(]*{spdx}"
                    rf"|{_TITLES[name]}",
                    re.IGNORECASE,
                ),
            )
        )
    return patterns


COPYLEFT_PATTERNS = _compile()


@dataclass
class LicenseScan:
    """The outcome of one scan, as recorded in the run artifact."""

    status: str
    matches: list[dict[str, str]] = field(default_factory=list)
    files_scanned: int = 0
    error: str | None = None

    @property
    def publishable(self) -> bool:
        """Clause 4.3.3: only a completed, clean scan may be published."""
        return self.status == CLEAN

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "license_scan": self.status,
            "license_matches": list(self.matches),
            "license_files_scanned": self.files_scanned,
        }
        if self.error:
            payload["license_scan_error"] = self.error
        return payload


def _files(root: Path):
    for directory, subdirs, names in os.walk(root):
        subdirs[:] = sorted(d for d in subdirs if d not in SKIP_DIRS)
        for name in sorted(names):
            path = Path(directory) / name
            # A link could point outside the workspace; it is not agent code.
            if not path.is_symlink():
                yield path


def tree_manifest(root: Path) -> dict[str, str]:
    """Hash every file under `root`, to tell later what the agent changed."""
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in _files(root)
    }


def licenses_in(text: str) -> list[str]:
    """Return the copyleft license families named in `text`."""
    return [name for name, pattern in COPYLEFT_PATTERNS if pattern.search(text)]


def scan_workspace(root: Path, *, baseline: dict[str, str] | None = None) -> LicenseScan:
    """Scan the agent-generated files under `root` for copyleft markers.

    `baseline` is the `tree_manifest` taken before the agent ran. Files
    whose content still matches it are the unchanged starting code and are
    skipped. Without a baseline every file is scanned.
    """
    root = Path(root)
    if not root.is_dir():
        return LicenseScan(UNAVAILABLE, error=f"workspace not found: {root}")

    baseline = baseline or {}
    matches: list[dict[str, str]] = []
    scanned = 0

    try:
        for path in _files(root):
            relative = path.relative_to(root).as_posix()
            data = path.read_bytes()
            if baseline.get(relative) == hashlib.sha256(data).hexdigest():
                continue
            scanned += 1
            head = data[:MAX_BYTES]
            if b"\0" in head:
                continue  # binary
            for name in licenses_in(head.decode("utf-8", errors="ignore")):
                matches.append({"path": relative, "license": name})
    except OSError as exc:
        # A file that cannot be read is a file that was not scanned.
        return LicenseScan(UNAVAILABLE, files_scanned=scanned, error=str(exc))

    return LicenseScan(FLAGGED if matches else CLEAN, matches=matches, files_scanned=scanned)
