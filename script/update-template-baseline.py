#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
from datetime import date
import json
import os
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
STABLE_TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
STABLE_VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PLUGIN_MANIFESTS = (
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
    ".cursor-plugin/plugin.json",
)
MARKETPLACE_MANIFESTS = (
    ".claude-plugin/marketplace.json",
    ".cursor-plugin/marketplace.json",
)


def fail(message: str) -> None:
    raise SystemExit(message)


def version_parts(value: str, pattern: re.Pattern[str], label: str) -> tuple[int, int, int]:
    match = pattern.fullmatch(value.strip())
    if match is None:
        fail(f"{label} must be stable semantic version")
    return tuple(int(part) for part in match.groups())


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"invalid JSON in {path}: {error}")
    if not isinstance(value, dict):
        fail(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def validate_candidate(candidate_root: Path, template_tag: str) -> None:
    manifest = load_json(candidate_root / ".superverse" / "template.json")
    expected_version = template_tag.removeprefix("v")
    if manifest.get("templateVersion") != expected_version:
        fail("template release tag does not match its manifest version")
    if manifest.get("schemaVersion") != 1:
        fail("template release uses an unsupported manifest schema")
    if manifest.get("minimumSandboxImageContractRevision", 0) < 3:
        fail("template release does not require sandbox contract revision 3")
    if "dexSkill" in manifest:
        fail("template release still contains a project-local skill path")
    if (candidate_root / ".gitmodules").exists() or (candidate_root / ".agents").exists():
        fail("template release still vendors project-local skills")


def update_versioned_manifests(root: Path, next_version: str) -> None:
    for relative_path in PLUGIN_MANIFESTS:
        path = root / relative_path
        manifest = load_json(path)
        manifest["version"] = next_version
        write_json(path, manifest)
    for relative_path in MARKETPLACE_MANIFESTS:
        path = root / relative_path
        marketplace = load_json(path)
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1 or not isinstance(plugins[0], dict):
            fail(f"{relative_path} must contain one plugin")
        plugins[0]["version"] = next_version
        write_json(path, marketplace)


def add_changelog(root: Path, next_version: str, release_date: str, previous: str, latest: str) -> None:
    changelog_path = root / "CHANGELOG.md"
    changelog = changelog_path.read_text()
    marker = "All notable changes to Dex Skills are documented here.\n\n"
    if marker not in changelog:
        fail("CHANGELOG.md has no insertion marker")
    entry = (
        f"## {next_version} - {release_date}\n\n"
        f"- Advance the basic-process template baseline from `{previous}` to `{latest}`.\n"
        "- Require the released template to use Coding Sandbox contract revision 3 without project-local skills.\n"
        f"- Synchronize the Codex, Claude Code, and Cursor plugin manifests at version {next_version}.\n\n"
    )
    changelog_path.write_text(changelog.replace(marker, marker + entry, 1))


def write_outputs(values: dict[str, str]) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a") as output:
            for key, value in values.items():
                output.write(f"{key}={value}\n")
    print(json.dumps(values, sort_keys=True))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--template-tag", required=True)
    parser.add_argument("--template-root", required=True, type=Path)
    parser.add_argument("--release-date", default=date.today().isoformat())
    arguments = parser.parse_args()

    latest_parts = version_parts(arguments.template_tag, STABLE_TAG, "template tag")
    current_tag = (ROOT / "TEMPLATE_BASELINE").read_text().strip()
    current_parts = version_parts(current_tag, STABLE_TAG, "current template baseline")
    current_version = (ROOT / "VERSION").read_text().strip()
    current_version_parts = version_parts(current_version, STABLE_VERSION, "current plugin version")

    changed = latest_parts > current_parts
    next_version = current_version
    if changed:
        validate_candidate(arguments.template_root, arguments.template_tag)
        next_version = (
            f"{current_version_parts[0]}.{current_version_parts[1]}."
            f"{current_version_parts[2] + 1}"
        )
        (ROOT / "TEMPLATE_BASELINE").write_text(arguments.template_tag + "\n")
        (ROOT / "VERSION").write_text(next_version + "\n")
        update_versioned_manifests(ROOT, next_version)
        add_changelog(
            ROOT,
            next_version,
            arguments.release_date,
            current_tag,
            arguments.template_tag,
        )

    write_outputs(
        {
            "changed": str(changed).lower(),
            "template_previous": current_tag,
            "template_latest": arguments.template_tag,
            "version_previous": current_version,
            "version_latest": next_version,
        }
    )


if __name__ == "__main__":
    main()
