#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "dex-sdk"
APP_BUILDER = ROOT / "dex-app-builder"
CONNECTOR_CONTRIBUTOR = ROOT / "dex-connector-contributor"
SDK_REFERENCES = SDK / "references"
PLUGIN_VERSION_CHECK = ROOT / "references" / "plugin-version-check.md"
LOGO = ROOT / "assets" / "logo.png"
MANIFESTS = {
    "codex": ROOT / ".codex-plugin" / "plugin.json",
    "claude": ROOT / ".claude-plugin" / "plugin.json",
    "cursor": ROOT / ".cursor-plugin" / "plugin.json",
}
MARKETPLACES = {
    "codex": ROOT / ".agents" / "plugins" / "marketplace.json",
    "claude": ROOT / ".claude-plugin" / "marketplace.json",
    "cursor": ROOT / ".cursor-plugin" / "marketplace.json",
}
CORE_TOPICS = {
    "ai-agents.md",
    "data-handling.md",
    "error-handling.md",
    "getting-started.md",
    "modeling.md",
    "operations.md",
    "patterns.md",
    "primitives.md",
    "step-options.md",
    "testing.md",
    "troubleshooting.md",
    "versioning.md",
}
LANGUAGES = ("python", "go", "java", "typescript", "rust")
LANGUAGE_TOPICS = {
    "advanced-features.md",
    "data-handling.md",
    "error-handling.md",
    "gotchas.md",
    "observability.md",
    "patterns.md",
    "primitives.md",
    "testing.md",
    "versioning.md",
}
APP_BUILDER_REFERENCES = {
    "build-test-handoff.md",
    "connector-architecture.md",
    "dex-web-v2.md",
    "product-discovery.md",
    "ui-workflow.md",
}
CONNECTOR_CONTRIBUTOR_REFERENCES = {
    "repository-workflow.md",
    "operations.md",
    "triggers.md",
    "ui-units.md",
    "examples-testing-pr.md",
}
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PUBLISHED_RELEASE_TAG = re.compile(
    r"^(?:[a-z0-9][a-z0-9-]*/)?v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)
PUBLISHED_CLI_RELEASE_TAG = re.compile(
    r"^cli-v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)
PUBLISHED_COMPONENT_TAG = re.compile(
    r"^[a-z0-9][a-z0-9-]*(?:/[a-z0-9][a-z0-9-]*)*/v"
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)
MARKDOWN_LINK = re.compile(r"\[[^]]+\]\(([^)]+)\)")
FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)
SOURCE_MARKER = re.compile(r"<!-- dex-source: ([^\s]+) -->")
FLOATING_SOURCE_LINK = re.compile(
    r"https://github\.com/superdurable/dex/(?:blob|tree)/main/"
)


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def version_tuple(version: str) -> tuple[int, int, int]:
    match = SEMVER.fullmatch(version)
    if match is None:
        fail(f"VERSION must be stable SemVer: {version}")
    return tuple(int(part) for part in match.groups())


def local_link_target(markdown: Path, target: str) -> Path | None:
    if "://" in target or target.startswith(("#", "mailto:")):
        return None
    relative_target = target.split("#", 1)[0].strip("<>")
    if not relative_target:
        return None
    return (markdown.parent / relative_target).resolve()


def check_reachable_links(skill: Path, references: list[Path]) -> None:
    markdown_files = [skill / "SKILL.md", *references]
    graph = {path.resolve(): set() for path in markdown_files}
    for markdown in markdown_files:
        content = markdown.read_text()
        if "[TODO:" in content:
            fail(f"unfinished placeholder in {markdown.relative_to(ROOT)}")
        prose = FENCED_BLOCK.sub("", content)
        for target in MARKDOWN_LINK.findall(prose):
            resolved = local_link_target(markdown, target)
            if resolved is None:
                continue
            if not resolved.exists():
                fail(f"broken link in {markdown.relative_to(ROOT)}: {target}")
            if resolved in graph:
                graph[markdown.resolve()].add(resolved)

    reachable: set[Path] = set()
    pending = [(skill / "SKILL.md").resolve()]
    while pending:
        current = pending.pop()
        if current in reachable:
            continue
        reachable.add(current)
        pending.extend(graph[current] - reachable)
    unreachable = sorted(path for path in references if path.resolve() not in reachable)
    if unreachable:
        rendered = ", ".join(str(path.relative_to(ROOT)) for path in unreachable)
        fail(f"references not reachable from {skill.name}/SKILL.md: {rendered}")


def check_sdk(baseline: str) -> None:
    core_files = {path.name for path in (SDK_REFERENCES / "core").glob("*.md")}
    if core_files != CORE_TOPICS:
        fail(f"Core references must be exactly: {', '.join(sorted(CORE_TOPICS))}")

    for language in LANGUAGES:
        language_dir = SDK_REFERENCES / language
        expected = {*LANGUAGE_TOPICS, f"{language}.md"}
        actual = {path.name for path in language_dir.glob("*.md")}
        if actual != expected:
            fail(f"{language} references must be exactly: {', '.join(sorted(expected))}")

    references = sorted(SDK_REFERENCES.rglob("*.md"))
    expected_count = len(CORE_TOPICS) + len(LANGUAGES) * 10
    if len(references) != expected_count:
        fail(f"expected {expected_count} Dex SDK references, found {len(references)}")
    check_reachable_links(SDK, references)

    for markdown in [SDK / "SKILL.md", *references]:
        content = markdown.read_text()
        if FLOATING_SOURCE_LINK.search(content):
            fail(f"floating Dex source link in {markdown.relative_to(ROOT)}")
        for source_path in SOURCE_MARKER.findall(content):
            expected_link = (
                "https://github.com/superdurable/dex/blob/"
                f"{baseline}/{source_path}"
            )
            marker = f"<!-- dex-source: {source_path} -->"
            marker_position = content.index(marker)
            preceding = content[max(0, marker_position - 600):marker_position]
            if expected_link not in preceding:
                fail(
                    f"source marker in {markdown.relative_to(ROOT)} needs visible "
                    f"pinned link: {source_path}"
                )


def check_app_builder() -> None:
    references_dir = APP_BUILDER / "references"
    references = sorted(references_dir.rglob("*.md"))
    actual = {path.name for path in references}
    if actual != APP_BUILDER_REFERENCES:
        fail(
            "Dex App Builder references must be exactly: "
            f"{', '.join(sorted(APP_BUILDER_REFERENCES))}"
        )
    if (references_dir / "core").exists() or (references_dir / "go").exists():
        fail("Dex App Builder must not vendor Dex SDK Core or Go references")
    check_reachable_links(APP_BUILDER, references)

    content = (APP_BUILDER / "SKILL.md").read_text()
    required = (
        "../dex-sdk/SKILL.md",
        "../dex-sdk/references/go/go.md",
        "Go SDK",
        "strict FDG 2.0",
        "writable repository or",
        "project workspace",
        "effectively empty",
        "../TEMPLATE_BASELINE",
        "preserving its `.git` directory",
        "`make bootstrap` as the first dependency/bootstrap command",
        "do not start a TypeScript Dex backend",
        "infer SDK versions from a neighboring workspace",
        "### No custom UI",
        "### Custom UI",
        "GetApplicationInfo",
        "trusted authentication boundary",
        "public external product",
        "$dex-connector-contributor",
        "schedules a Connector Step",
        "temporary Go",
        "connector library already exists",
        "unified Connector SDK",
        "generic HTTP connector only when the service is genuinely internal",
        "static `ConnectionName`",
        "`NewLocalConnection`",
        "external effects in `Execute`",
        "`WaitFor` free of provider or Dex mutations",
    )
    for text in required:
        if text not in content:
            fail(f"dex-app-builder/SKILL.md must contain: {text}")

    connector_architecture = (references_dir / "connector-architecture.md").read_text()
    for text in (
        "## Application composition",
        "User/API RPC requests provider work",
        "connector, operation, or Trigger is a connector contribution",
        "## Internal connector library decision",
        "Do not infer access to a private repository",
        "uncommitted `go.work` or temporary Go",
    ):
        if text not in connector_architecture:
            fail(f"connector architecture must contain: {text}")

    product_discovery = (references_dir / "product-discovery.md").read_text()
    for text in ("connector capability matrix", "internal connector library"):
        if text not in product_discovery:
            fail(f"product discovery must contain: {text}")


def check_connector_contributor() -> None:
    references_dir = CONNECTOR_CONTRIBUTOR / "references"
    references = sorted(references_dir.rglob("*.md"))
    actual = {path.name for path in references}
    if actual != CONNECTOR_CONTRIBUTOR_REFERENCES:
        fail(
            "Dex Connector Contributor references must be exactly: "
            f"{', '.join(sorted(CONNECTOR_CONTRIBUTOR_REFERENCES))}"
        )
    if (references_dir / "core").exists() or (references_dir / "go").exists():
        fail("Dex Connector Contributor must not vendor Dex SDK Core or Go references")
    check_reachable_links(CONNECTOR_CONTRIBUTOR, references)

    content = (CONNECTOR_CONTRIBUTOR / "SKILL.md").read_text()
    required = (
        "../dex-sdk/SKILL.md",
        "../dex-sdk/references/go/go.md",
        "../dex-app-builder/references/dex-web-v2.md",
        "superdurable/dex-connectors-library",
        "documented public API or official SDK",
        "connector.yaml",
        "operation-specific",
        "optional: true",
        "seven seconds",
        "Start Flow",
        "GOWORK=off",
        "$opr",
        "user's GitHub fork",
        "upstream/main",
    )
    for text in required:
        if text not in content:
            fail(f"dex-connector-contributor/SKILL.md must contain: {text}")

    examples = (references_dir / "examples-testing-pr.md").read_text()
    for scenario in (
        "Operation-only connector",
        "real Flow start and typed RPC delivery",
        "Host API 0.2",
        "SDK PR/release",
    ):
        if scenario not in examples:
            fail(f"Connector Contributor acceptance scenarios must contain: {scenario}")

    workflow = (references_dir / "repository-workflow.md").read_text()
    for fork_contract in (
        "https://github.com/superdurable/dex-connectors-library/fork",
        "click **Create fork**",
        "Do not click the creation button for the user",
        "`origin` is the user's verified fork",
        "Push only to the user's fork",
    ):
        if fork_contract not in workflow:
            fail(f"Connector Contributor fork workflow must contain: {fork_contract}")
    for release in (
        "sdkgo/v0.8.0",
        "connectors/slack/v0.9.0",
        "connectors/google/gmail/v0.10.0",
        "connectors/google/spreadsheet/v0.7.0",
    ):
        if release not in workflow:
            fail(f"Connector Contributor reference releases must contain: {release}")

    agent = CONNECTOR_CONTRIBUTOR / "agents" / "openai.yaml"
    if not agent.is_file():
        fail("Dex Connector Contributor must define agents/openai.yaml")
    agent_content = agent.read_text()
    for text in ("Dex Connector Contributor", "$dex-connector-contributor"):
        if text not in agent_content:
            fail(f"dex-connector-contributor/agents/openai.yaml must contain: {text}")


def check_invocation_policy() -> None:
    expected = {
        APP_BUILDER: "true",
        SDK: "false",
        CONNECTOR_CONTRIBUTOR: "false",
    }
    for skill, allow_implicit in expected.items():
        agent = skill / "agents" / "openai.yaml"
        content = agent.read_text()
        policy = f"allow_implicit_invocation: {allow_implicit}"
        if policy not in content:
            fail(f"{agent.relative_to(ROOT)} must contain: {policy}")


def check_plugin_version_check() -> None:
    if not PLUGIN_VERSION_CHECK.is_file():
        fail("references/plugin-version-check.md must exist")
    content = PLUGIN_VERSION_CHECK.read_text()
    for text in (
        "https://raw.githubusercontent.com/superdurable/dex-skills/main/VERSION",
        "without additional user approval",
        "single stable semantic version",
        "repository version is higher",
        "substantive response",
        "Do not repeat the notice",
    ):
        if text not in content:
            fail(f"plugin version check must contain: {text}")

    relative_link = "../references/plugin-version-check.md"
    for skill in (APP_BUILDER, SDK, CONNECTOR_CONTRIBUTOR):
        content = (skill / "SKILL.md").read_text()
        if relative_link not in content:
            fail(f"{skill.name}/SKILL.md must load the plugin version check")


def check_skills(baseline: str) -> None:
    skills = sorted(path.parent for path in ROOT.glob("*/SKILL.md"))
    expected = sorted((SDK, APP_BUILDER, CONNECTOR_CONTRIBUTOR))
    if skills != expected:
        rendered = ", ".join(str(path.relative_to(ROOT)) for path in skills)
        fail(f"expected the three public Dex skills, found: {rendered}")
    if (ROOT / "plugins").exists():
        fail("plugins/ wrapper must not exist")
    if any(path.name == "dex-ai-platform-backend" for path in ROOT.rglob("*")):
        fail("backend companion skill must not exist")
    check_plugin_version_check()
    check_sdk(baseline)
    check_app_builder()
    check_connector_contributor()
    check_invocation_policy()


def check_manifest_common(path: Path, manifest: dict, version: str) -> None:
    if manifest.get("name") != "superdurable-dex":
        fail(f"{path.relative_to(ROOT)} must name plugin superdurable-dex")
    if manifest.get("version") != version:
        fail(f"{path.relative_to(ROOT)} version must be {version}")
    if manifest.get("repository") != "https://github.com/superdurable/dex-skills":
        fail(f"{path.relative_to(ROOT)} must use the dex-skills repository")
    if manifest.get("author", {}).get("name") != "Super Durable":
        fail(f"{path.relative_to(ROOT)} publisher must remain Super Durable")


def check_manifests(version: str) -> None:
    manifests = {name: load_json(path) for name, path in MANIFESTS.items()}
    for name, manifest in manifests.items():
        check_manifest_common(MANIFESTS[name], manifest, version)

    codex = manifests["codex"]
    if codex.get("skills") != "./":
        fail("Codex manifest must discover root skills with ./")
    interface = codex.get("interface")
    if not isinstance(interface, dict):
        fail("Codex manifest must define interface metadata")
    if interface.get("displayName") != "Dex":
        fail("Codex display name must be Dex")
    if interface.get("developerName") != "Super Durable":
        fail("Codex developer name must remain Super Durable")
    for field in ("composerIcon", "logo"):
        if interface.get(field) != "./assets/logo.png":
            fail(f"Codex {field} must use ./assets/logo.png")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not prompts or "$dex-app-builder" not in prompts[0]:
        fail("Codex default prompts must put $dex-app-builder first")
    if not any("$dex-sdk" in prompt for prompt in prompts):
        fail("Codex default prompts must expose $dex-sdk")
    if not any("$dex-connector-contributor" in prompt for prompt in prompts):
        fail("Codex default prompts must expose $dex-connector-contributor")

    cursor = manifests["cursor"]
    expected_skills = ["./dex-app-builder", "./dex-sdk", "./dex-connector-contributor"]
    if cursor.get("skills") != expected_skills:
        fail("Cursor manifest must expose all three public skills")
    if cursor.get("logo") != "assets/logo.png":
        fail("Cursor manifest must use assets/logo.png")

    if not LOGO.is_file() or not LOGO.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"):
        fail("assets/logo.png must be a PNG file")

    marketplaces = {name: load_json(path) for name, path in MARKETPLACES.items()}
    for name, marketplace in marketplaces.items():
        if marketplace.get("name") != "superdurable":
            fail(f"{MARKETPLACES[name].relative_to(ROOT)} must name marketplace superdurable")
        plugins = marketplace.get("plugins")
        if not isinstance(plugins, list) or len(plugins) != 1:
            fail(f"{MARKETPLACES[name].relative_to(ROOT)} must contain one plugin")
        if plugins[0].get("name") != "superdurable-dex":
            fail(f"{MARKETPLACES[name].relative_to(ROOT)} has the wrong plugin ID")

    if marketplaces["codex"].get("interface", {}).get("displayName") != "Super Durable":
        fail("Codex marketplace publisher must remain Super Durable")
    for name in ("claude", "cursor"):
        if marketplaces[name].get("owner", {}).get("name") != "Super Durable":
            fail(f"{name} marketplace publisher must remain Super Durable")

    codex_entry = marketplaces["codex"]["plugins"][0]
    source = codex_entry.get("source")
    if not isinstance(source, dict) or source.get("path") != "./":
        fail("Codex marketplace must point to the repository root")
    if "version" in codex_entry:
        fail("Codex marketplace entry must remain unversioned")

    claude_entry = marketplaces["claude"]["plugins"][0]
    if claude_entry.get("source") != "./" or claude_entry.get("version") != version:
        fail("Claude marketplace must point to the versioned repository root")
    if claude_entry.get("skills") != expected_skills:
        fail("Claude marketplace must expose all three public skills")

    cursor_entry = marketplaces["cursor"]["plugins"][0]
    if cursor_entry.get("source") != "./" or cursor_entry.get("version") != version:
        fail("Cursor marketplace must point to the versioned repository root")
    if cursor_entry.get("logo") != "assets/logo.png":
        fail("Cursor marketplace must use assets/logo.png")


def check_agent_rules() -> None:
    agents = (ROOT / "AGENTS.md").read_text()
    claude = (ROOT / "CLAUDE.md").read_text()
    cursor = (ROOT / ".cursor" / "rules" / "dex-skills.mdc").read_text()
    if agents != claude:
        fail("AGENTS.md and CLAUDE.md must contain equivalent rules")
    if not cursor.endswith(agents):
        fail("Cursor rule must contain the same repository instructions")
    pull_request_template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text()
    if "Dex-AI-Platform-PR:" in pull_request_template:
        fail("pull request template must not require a paired repository")
    if "quick_validate.py" not in pull_request_template:
        fail("pull request template must require skill validation")


def git_output(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def check_release_change(base_ref: str, current_version: str) -> None:
    changed = set(git_output("diff", "--name-only", f"{base_ref}...HEAD").splitlines())
    skill_prefixes = ("dex-sdk/", "dex-app-builder/", "dex-connector-contributor/")
    if not any(path.startswith(skill_prefixes) for path in changed):
        return
    required = {"CHANGELOG.md", "VERSION"}
    missing = required - changed
    if missing:
        fail(f"skill changes must update: {', '.join(sorted(missing))}")
    try:
        base_version = git_output("show", f"{base_ref}:VERSION").strip()
    except subprocess.CalledProcessError:
        return
    if version_tuple(current_version) <= version_tuple(base_version):
        fail(f"VERSION must increase beyond {base_version}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref")
    arguments = parser.parse_args()

    current_version = (ROOT / "VERSION").read_text().strip()
    version_tuple(current_version)
    baseline = (ROOT / "DEX_BASELINE").read_text().strip()
    if PUBLISHED_RELEASE_TAG.fullmatch(baseline) is None:
        fail("DEX_BASELINE must contain a published Dex release tag")
    server_baseline = (ROOT / "DEX_SERVER_BASELINE").read_text().strip()
    if PUBLISHED_RELEASE_TAG.fullmatch(server_baseline) is None:
        fail("DEX_SERVER_BASELINE must contain a published Dex release tag")
    cli_baseline = (ROOT / "DEX_CLI_BASELINE").read_text().strip()
    if PUBLISHED_CLI_RELEASE_TAG.fullmatch(cli_baseline) is None:
        fail("DEX_CLI_BASELINE must contain a published Dex CLI release tag")
    template_baseline = (ROOT / "TEMPLATE_BASELINE").read_text().strip()
    if PUBLISHED_RELEASE_TAG.fullmatch(template_baseline) is None:
        fail("TEMPLATE_BASELINE must contain a published template release tag")
    connector_baseline = (ROOT / "CONNECTOR_LIBRARY_BASELINE").read_text().strip()
    if PUBLISHED_COMPONENT_TAG.fullmatch(connector_baseline) is None:
        fail("CONNECTOR_LIBRARY_BASELINE must contain a published component tag")

    check_skills(baseline)
    check_manifests(current_version)
    check_agent_rules()
    if arguments.base_ref:
        check_release_change(arguments.base_ref, current_version)
    print(f"validated superdurable-dex {current_version} with three root skills")


if __name__ == "__main__":
    main()
