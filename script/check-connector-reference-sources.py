#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import re
import subprocess
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "dex-connector-contributor" / "references"
SOURCE_BLOCK = re.compile(
    r"<!-- connector-source: (?P<path>[^\s]+) -->\s*\n"
    r"```(?P<language>[^\n]*)\n(?P<snippet>.*?)\n```",
    re.DOTALL,
)
GO_FENCE = re.compile(r"^```[ \t]*go(?:[ \t]+[^\n]*)?[ \t]*$", re.IGNORECASE | re.MULTILINE)
PINNED_LINK = re.compile(
    r"https://github\.com/superdurable/dex-connectors-library/"
    r"(?P<kind>blob|tree)/(?P<target>[^)\s#]+)"
)
REFERENCE_RELEASES = (
    "sdkgo/v0.11.0",
    "connectors/slack/v0.11.0",
    "connectors/google/gmail/v0.13.0",
    "connectors/google/spreadsheet/v0.8.0",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def normalized_lines(text: str) -> list[str]:
    return [" ".join(line.strip().split()) for line in textwrap.dedent(text).strip("\n").splitlines()]


def snippet_is_contiguous(source: str, snippet: str) -> bool:
    wanted = normalized_lines(snippet)
    source_lines = source.splitlines()
    for start in range(0, len(source_lines) - len(wanted) + 1):
        candidate = normalized_lines("\n".join(source_lines[start:start + len(wanted)]))
        if candidate == wanted:
            return True
    return False


def source_is_allowed(path: str) -> bool:
    source = Path(path)
    if source.is_absolute() or ".." in source.parts:
        return False
    if path == "docs/connector-contract.md":
        return True
    if source.parts and source.parts[0] == "sdkgo" and source.suffix == ".go":
        return True
    return len(source.parts) >= 3 and source.parts[0] == "connectors" and source.suffix in {".go", ".yaml", ".md"}


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def check_file(markdown: Path, connector_root: Path, baseline: str) -> int:
    content = markdown.read_text()
    blocks = list(SOURCE_BLOCK.finditer(content))
    marked_fences = {match.start("language") - 3 for match in blocks}
    for fence in GO_FENCE.finditer(content):
        if fence.start() not in marked_fences:
            fail(f"unmarked Go fence in {markdown.relative_to(ROOT)}")

    for match in blocks:
        source_path = match.group("path")
        if not source_is_allowed(source_path):
            fail(f"unsupported Connector source in {markdown.relative_to(ROOT)}: {source_path}")
        source = (connector_root / source_path).resolve()
        try:
            source.relative_to(connector_root)
        except ValueError:
            fail(f"Connector source escapes checkout in {markdown.relative_to(ROOT)}: {source_path}")
        if not source.is_file():
            fail(f"missing Connector source for {markdown.relative_to(ROOT)}: {source_path}")
        preceding = content[max(0, match.start() - 800):match.start()]
        expected = (
            "https://github.com/superdurable/dex-connectors-library/blob/"
            f"{baseline}/{source_path}"
        )
        following = content[match.end():min(len(content), match.end() + 800)]
        if expected not in preceding and expected not in following:
            fail(f"missing pinned source link for {source_path} in {markdown.relative_to(ROOT)}")
        if not snippet_is_contiguous(source.read_text(), match.group("snippet")):
            fail(f"non-contiguous Connector excerpt in {markdown.relative_to(ROOT)}: {source_path}")

    expected_prefixes = {
        kind: f"https://github.com/superdurable/dex-connectors-library/{kind}/{baseline}/"
        for kind in ("blob", "tree")
    }
    for link in PINNED_LINK.finditer(content):
        expected_prefix = expected_prefixes[link.group("kind")]
        if not link.group(0).startswith(expected_prefix):
            fail(f"Connector source link is not pinned in {markdown.relative_to(ROOT)}")
        linked_path = link.group(0)[len(expected_prefix):]
        if not source_is_allowed(linked_path):
            fail(f"unsupported Connector source link in {markdown.relative_to(ROOT)}: {linked_path}")
        if not (connector_root / linked_path).exists():
            fail(f"missing Connector source link path in {markdown.relative_to(ROOT)}: {linked_path}")
    return len(blocks)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--connector-root", required=True, type=Path)
    arguments = parser.parse_args()

    baseline = (ROOT / "CONNECTOR_LIBRARY_BASELINE").read_text().strip()
    connector_root = arguments.connector_root.resolve()
    if not (connector_root / ".git").exists():
        fail(f"not a Connector library checkout: {connector_root}")
    if git(connector_root, "rev-parse", "HEAD") != git(connector_root, "rev-parse", f"{baseline}^{{commit}}"):
        fail(f"Connector checkout must be at CONNECTOR_LIBRARY_BASELINE {baseline}")
    for release in REFERENCE_RELEASES:
        try:
            git(connector_root, "rev-parse", f"{release}^{{commit}}")
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", release, baseline],
                cwd=connector_root,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
            fail(f"published Connector reference release is missing from baseline: {release}")

    total = 0
    for markdown in sorted(REFERENCES.rglob("*.md")):
        total += check_file(markdown, connector_root, baseline)
    if total == 0:
        fail("expected at least one source-marked Connector excerpt")
    print(f"validated {total} source-marked excerpts against Connector library {baseline}")


if __name__ == "__main__":
    main()
