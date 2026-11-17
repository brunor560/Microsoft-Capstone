"""SRS Spec 4.3: copyleft license scan of agent-generated code.

Fully offline: the scan reads files on the host and needs no Docker.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from harness import license_scan
from harness.license_scan import (
    CLEAN,
    FLAGGED,
    UNAVAILABLE,
    licenses_in,
    scan_workspace,
    tree_manifest,
)

GPL_HEADER = (
    "// This program is free software: you can redistribute it and/or modify\n"
    "// it under the terms of the GNU General Public License as published by\n"
    "// the Free Software Foundation, either version 3 of the License.\n"
)


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    (tmp_path / "server.js").write_text("// SPDX-License-Identifier: MIT\nmodule.exports = {};\n")
    (tmp_path / "package.json").write_text('{"name": "app", "license": "MIT"}\n')
    return tmp_path


# --- TC-4.3-2: a clean fixture is reported clean -----------------------------


def test_permissive_code_is_clean(workspace):
    result = scan_workspace(workspace)
    assert result.status == CLEAN
    assert result.matches == []
    assert result.files_scanned == 2
    assert result.publishable


# --- TC-4.3-1: a planted copyleft sample is flagged --------------------------


@pytest.mark.parametrize(
    "text, family",
    [
        (GPL_HEADER, "GPL"),
        ("/* SPDX-License-Identifier: GPL-3.0-or-later */", "GPL"),
        ("# SPDX-License-Identifier: AGPL-3.0-only", "AGPL"),
        ("// SPDX-License-Identifier: (LGPL-2.1)", "LGPL"),
        ("Licensed under the GNU Affero General Public License", "AGPL"),
        ("GNU LESSER GENERAL PUBLIC LICENSE\nVersion 3", "LGPL"),
        ("This Source Code Form is subject to the Mozilla Public License, v. 2.0", "MPL"),
        ('{"name": "x", "license": "GPL-2.0"}', "GPL"),
    ],
)
def test_copyleft_markers_are_recognised(text, family):
    assert licenses_in(text) == [family]


@pytest.mark.parametrize(
    "text",
    [
        "// SPDX-License-Identifier: MIT",
        "Licensed under the Apache License, Version 2.0",
        '{"license": "ISC"}',
        "const gplCount = 0; // not a license statement",
    ],
)
def test_permissive_text_is_not_flagged(text):
    assert licenses_in(text) == []


def test_planted_sample_is_flagged_and_blocks_publication(workspace):
    """Clauses 4.3.1 to 4.3.3."""
    (workspace / "vendor.js").write_text(GPL_HEADER + "function copied() {}\n")

    result = scan_workspace(workspace)

    assert result.status == FLAGGED
    assert result.matches == [{"path": "vendor.js", "license": "GPL"}]
    assert not result.publishable
    assert result.to_dict()["license_scan"] == "flagged"


def test_nested_files_are_scanned(workspace):
    nested = workspace / "src" / "lib"
    nested.mkdir(parents=True)
    (nested / "util.js").write_text("// SPDX-License-Identifier: AGPL-3.0\n")

    result = scan_workspace(workspace)

    assert result.matches == [{"path": "src/lib/util.js", "license": "AGPL"}]


# --- only agent-generated code is judged -------------------------------------


def test_unchanged_baseline_files_are_not_scanned(workspace):
    """A starting file that already names a copyleft license is not the agent's."""
    (workspace / "COPYING").write_text("GNU GENERAL PUBLIC LICENSE\n")
    baseline = tree_manifest(workspace)

    result = scan_workspace(workspace, baseline=baseline)

    assert result.status == CLEAN
    assert result.files_scanned == 0


def test_a_file_the_agent_changed_is_scanned(workspace):
    baseline = tree_manifest(workspace)
    (workspace / "server.js").write_text(GPL_HEADER)

    result = scan_workspace(workspace, baseline=baseline)

    assert result.status == FLAGGED
    assert result.files_scanned == 1


def test_dependency_and_git_directories_are_skipped(workspace):
    for name in ("node_modules", ".git"):
        (workspace / name).mkdir()
        (workspace / name / "LICENSE").write_text("GNU GENERAL PUBLIC LICENSE\n")

    assert scan_workspace(workspace).status == CLEAN


def test_binary_files_are_not_searched(workspace):
    (workspace / "image.bin").write_bytes(b"\0\0GNU General Public License\0")

    assert scan_workspace(workspace).status == CLEAN


# --- TC-4.3-3: a scan that cannot complete fails closed ----------------------


def test_missing_workspace_is_scanner_unavailable(tmp_path):
    result = scan_workspace(tmp_path / "does-not-exist")

    assert result.status == UNAVAILABLE
    assert not result.publishable
    assert result.error


def test_unreadable_file_is_scanner_unavailable(workspace, monkeypatch):
    def broken_read(self):
        raise PermissionError(f"cannot read {self.name}")

    monkeypatch.setattr(Path, "read_bytes", broken_read)

    result = scan_workspace(workspace)

    assert result.status == UNAVAILABLE
    assert not result.publishable
    assert "cannot read" in result.to_dict()["license_scan_error"]


def test_only_a_clean_scan_is_publishable():
    for status, expected in [(CLEAN, True), (FLAGGED, False), (UNAVAILABLE, False)]:
        assert license_scan.LicenseScan(status).publishable is expected
