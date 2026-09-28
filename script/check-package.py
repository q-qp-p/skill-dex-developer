#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SDK = ROOT / "dex-sdk"
APP_BUILDER = ROOT / "dex-app-builder"
CONNECTOR_CONTRIBUTOR = ROOT / "dex-connector-contributor"
SDK_REFERENCES = SDK / "references"
PLUGIN_VERSION_CHECK = SDK_REFERENCES / "core" / "plugin-version-check.md"
BUNDLE_VERSION = SDK / "VERSION"
BUNDLE_BASELINES = SDK_REFERENCES / "core" / "bundle-baselines.md"
BASELINE_FILES = (
    "DEX_BASELINE",
    "DEX_SERVER_BASELINE",
    "DEX_CLI_BASELINE",
    "TEMPLATE_BASELINE",
)
VERSION_CHECK_SCRIPT = ROOT / "hooks" / "version-check.mjs"
HOOK_CONFIGS = {
    "codex": ROOT / "hooks" / "codex.json",
    "claude": ROOT / "hooks" / "claude.json",
    "cursor": ROOT / "hooks" / "cursor.json",
}
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
    "bundle-baselines.md",
    "data-handling.md",
    "error-handling.md",
    "getting-started.md",
    "modeling.md",
    "operations.md",
    "patterns.md",
    "plugin-version-check.md",
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
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PUBLISHED_RELEASE_TAG = re.compile(
    r"^(?:[a-z0-9][a-z0-9-]*/)?v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
)
PUBLISHED_CLI_RELEASE_TAG = re.compile(
    r"^cli-v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$"
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

    skill_content = (SDK / "SKILL.md").read_text()
    for text in (
        "### Flow boundary default",
        "Default a new design to no SubFlows",
        "A separate top-level Flow is not a SubFlow",
        "200-concurrent-Step architecture-review threshold",
        "Code reuse, provider",
        "### Dex-first state ownership",
        "Default durable application state to typed Flow Attributes",
        "ownership-design question",
        "complex/ad-hoc indexes",
        "sustained high-contention",
        "Never create ambiguous dual",
    ):
        if text not in skill_content:
            fail(f"dex-sdk/SKILL.md must contain storage principle: {text}")

    core_modeling = (SDK_REFERENCES / "core" / "modeling.md").read_text()
    for text in (
        "different authoritative owner and retention or cleanup",
        "independent top-level Flow",
        "state must not pollute the authoritative store",
        "## Start with parallel Steps",
        "## Gate SubFlows as an evolution",
        "more than 200 concurrent Step executions",
        "architecture-review threshold",
        "not a Dex Server",
        "the user explicitly confirms the SubFlow design",
    ):
        if text not in core_modeling:
            fail(f"Core modeling must contain Flow-boundary principle: {text}")
    if "Prefer a SubFlow when work needs its own identity" in core_modeling:
        fail("Core modeling must not present SubFlow as an initial-design preference")

    core_patterns = (SDK_REFERENCES / "core" / "patterns.md").read_text()
    for text in (
        "Parallel Steps are the default",
        "Do not introduce SubFlows in an initial design",
        "200-concurrent-Step",
        "obtain explicit user confirmation",
        "does not automatically select a",
        "alone is insufficient",
    ):
        if text not in core_patterns:
            fail(f"Core patterns must contain SubFlow gate: {text}")
    if "Choose SubFlows for independent retry, scaling, ownership, or identity" in core_patterns:
        fail("Core patterns must not allow one-factor SubFlow selection")

    go_patterns = (SDK_REFERENCES / "go" / "patterns.md").read_text()
    for text in (
        "Apply the Core SubFlow evolution gate",
        "do not make SubFlows the",
        "default for new designs or for ordinary parallel work",
    ):
        if text not in go_patterns:
            fail(f"Go patterns must route through the SubFlow gate: {text}")

    core_data_handling = (SDK_REFERENCES / "core" / "data-handling.md").read_text()
    for text in (
        "## Dex-first storage decision",
        "begin with Dex as the durable system of record",
        "Data shared by several processes does not automatically need a database",
        "Do not add a database, cache, ORM, outbox, or shadow read model",
        "One fact must never have two ambiguous authorities",
    ):
        if text not in core_data_handling:
            fail(f"Core data handling must contain storage principle: {text}")

    operations = (SDK_REFERENCES / "core" / "operations.md").read_text()
    for text in (
        "## FDG 2.0 management metadata",
        "generated only by the Go analyzer",
        "Action input capture hints",
    ):
        if text not in operations:
            fail(f"Core operations must contain FDG language boundary: {text}")

    for language in LANGUAGES:
        handbook = (SDK_REFERENCES / language / f"{language}.md").read_text()
        for text in (
            "## Dex Web v2 management metadata",
            "FDG 2.0 management-interface analyzer",
        ):
            if text not in handbook:
                fail(f"{language} handbook must contain FDG language boundary: {text}")


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
        "default coordinator",
        "If App Builder receives a standalone specialist request",
        "classify it",
        "before product discovery",
        "standalone official connector-library creation or modification",
        "make it the owning workflow",
        "published connector—continue with App Builder",
        "installed bundle is incomplete",
        "Do not search arbitrary plugin-cache paths",
        "../dex-sdk/references/go/go.md",
        "Go SDK",
        "strict FDG 2.0",
        "writable repository or",
        "project workspace",
        "effectively empty",
        "../dex-sdk/references/core/bundle-baselines.md",
        "`TEMPLATE_BASELINE` is the",
        "application stack authority",
        "In the first implementation update for an effectively empty repository",
        "do not fall back to a self-selected stack",
        "authorize upgrading an application's template-pinned dependencies",
        "TypeScript is limited to the",
        "template's optional React frontend",
        "SDK integration are Go-only",
        "cannot use the current Connector SDK",
        "preserving its `.git` directory",
        "`make bootstrap` as the first dependency/bootstrap command",
        "do not start a TypeScript Dex backend",
        "Do not advance the scaffold independently",
        "Connector SDK supports application integration only from Go",
        "infer SDK versions from a neighboring workspace",
        "### No custom UI",
        "### Custom UI",
        "management UI capability mapping",
        "Complete the management UI capability mapping before making",
        "Summary RPC",
        "Display RPC",
        "Action RPC metadata",
        "A request for an admin portal, dashboard, or management backend",
        "specific interaction Dex Web v2 cannot provide",
        "low-fidelity static wireframe",
        "must not use application",
        "page names, purposes, and direct links",
        "design the application OpenAPI contract in the same pass",
        "update `openapi/openapi.yaml`",
        "generated server interfaces",
        "ignored local build outputs",
        "never add them to Git or a pull request",
        "Do not resume dynamic frontend work",
        "component-level mocks of the generated client",
        "test-local Playwright request interception",
        "Do not create an application-level mock server",
        "Mock evidence never replaces real Dex durability",
        "Only after the real Dex and Connector end-to-end journey passes",
        "GetApplicationInfo",
        "trusted authentication boundary",
        "public external product",
        "https://superdurable.github.io/dex-connectors-library/catalog.yaml",
        "match every required Trigger, Query, Mutation, and UI capability",
        "stop connector-dependent",
        "do not infer support from memory",
        "`dex-connector-contributor`",
        "schedules a Connector Step",
        "temporary Go",
        "connector library already exists",
        "unified Connector SDK",
        "generic HTTP connector only when the service is genuinely internal",
        "static `ConnectionName`",
        "`NewLocalConnection`",
        "external effects in `Execute`",
        "`WaitFor` free of provider or Dex mutations",
        "one `admin` role by default",
        "data-lifecycle and execution-shape boundary matrices",
        "parallel-Step alternatives",
        "greater-than-200 concurrent-Step requirement",
        "New applications default to no",
        "explicitly confirms it",
        "### Dex-first backend storage",
        "Use Dex Flow state as the default durable application store",
        "Cross-Flow reuse alone is not a reason",
        "Do not add an external database, cache, ORM, outbox, or shadow read model",
        "high-concurrency reads and writes",
        "“Future flexibility”",
    )
    for text in required:
        if text not in content:
            fail(f"dex-app-builder/SKILL.md must contain: {text}")

    stage_markers = (
        "## Stage 2: establish the confirmed application surface",
        "## Stage 3: design the Flow, Connectors, and OpenAPI contract",
        "## Stage 4: integrate the Custom UI, verify, polish, and hand off",
    )
    for marker in stage_markers:
        if marker not in content:
            fail(f"Dex App Builder must contain stage: {marker}")
    stage_positions = [content.index(marker) for marker in stage_markers]
    if stage_positions != sorted(stage_positions):
        fail("Dex App Builder stages must keep static UI before contract/backend before integration/polish")
    if content.index("Complete the management UI capability mapping before making") > content.index(stage_markers[0]):
        fail("Dex App Builder must complete management UI mapping before selecting a UI mode")

    ui_workflow = (references_dir / "ui-workflow.md").read_text()
    ui_stages = (
        "### 1. Low-fidelity static checkpoint",
        "### 2. Contract and backend design",
        "### 3. Integration and durable verification",
        "### 4. Visual polish",
    )
    for text in (
        *ui_stages,
        "no hooks or",
        "application state",
        "Use no images",
        "custom icons, animation, branding",
        "npm --prefix web run dev",
        "make generate",
        "application's business boundary",
        "generated TypeScript client calls",
        "ignored local build artifacts",
        "component-level mocks of the generated client",
        "request interception inside that Playwright test only",
        "Do not add an",
        "application-level mock API",
        "real Dex and Connector end-to-end path",
        "Use this only after discovery completes the management UI capability mapping",
        "requires a recorded",
        "Dex Web v2 capability gap",
    ):
        if text not in ui_workflow:
            fail(f"UI workflow must contain: {text}")
    ui_stage_positions = [ui_workflow.index(marker) for marker in ui_stages]
    if ui_stage_positions != sorted(ui_stage_positions):
        fail("Custom UI workflow must keep wireframe, contract/backend, integration, and polish in order")
    for obsolete in (
        "### Mock checkpoint",
        "start with `make mock`",
        "wait for explicit user approval. Do not connect a real Dex backend",
        "Bring the template mock server into conformance",
        "retain Mock Controls only in mock mode",
    ):
        if obsolete in content or obsolete in ui_workflow:
            fail(f"Custom UI workflow must not restore the mock-first gate: {obsolete}")

    build_handoff = (references_dir / "build-test-handoff.md").read_text()
    for text in (
        "low-fidelity static",
        "ignored local build outputs",
        "Never stage",
        "make bootstrap",
        "make generate",
        "make check-fdg-v2",
        "make test-unit",
        "make test-integration",
        "make test-e2e",
        "make build",
        "make dev",
        "make check",
        "generates only",
        "component-level mocks of the generated client",
        "test-local Playwright request interception",
        "application-level mock server",
        "neither generated directory is",
        "Run real Dex and Connector",
        "before visual polish",
        "generated server interfaces",
        "storage decision matrix",
        "Remove an unneeded dependency when Dex meets the requirement",
        "approved discovery artifact must name the Dex Web v2 capability gap",
        "management UI capability mapping was completed before the UI-mode",
    ):
        if text not in build_handoff:
            fail(f"build and handoff must contain: {text}")

    connector_architecture = (references_dir / "connector-architecture.md").read_text()
    for text in (
        "application integration only from a Go backend",
        "it is not a Connector SDK backend",
        "## Application composition",
        "## Released capability discovery",
        "connectors.dex.dev/catalog/v1alpha1",
        "<directory>/<version>",
        "verification blocker",
        "User/API RPC requests provider work",
        "connector, operation, or Trigger is a connector contribution",
        "## Internal connector library decision",
        "Do not infer access to a private repository",
        "uncommitted `go.work` or temporary Go",
    ):
        if text not in connector_architecture:
            fail(f"connector architecture must contain: {text}")

    product_discovery = (references_dir / "product-discovery.md").read_text()
    for text in (
        "## Stack checkpoint",
        "defaults to the exact stack",
        "without Connector SDK support",
        "connector capability matrix",
        "canonical published catalog",
        "immutable `connector.yaml`",
        "internal connector library",
        "## Storage decision",
        "Default each durable fact to Dex",
        "cross-Flow reuse alone is not a gap",
        "projection still introduces an external database",
        "“We may need it later” is not evidence",
        "## Actor, role, operation, and permission matrix",
        "one `admin` role for the trusted",
        "justify every non-`admin`",
        "## Flow-boundary decisions",
        "parallel Steps share one Flow identity and lifecycle",
        "independent top-level Flows start separately",
        "SubFlows have an explicit parent-child lifecycle",
        "different authoritative owner and a different",
        "own waits, Timers, and terminal outcomes",
        "state must not pollute the authoritative store",
        "New applications default to no SubFlows",
        "more than 200 concurrent Step executions",
        "architecture-review threshold, not a claimed Dex",
        "user explicitly confirms the SubFlow design",
        "## Management UI capability mapping",
        "Model each record as a Run",
        "Summary RPC",
        "Display RPC",
        "Action metadata",
        "Work Queue permission history",
        "editable scalar Attributes",
        "Run timeline, Step graph",
        "## UI-mode decision",
        "only after completing the management UI capability",
        "recorded Dex Web v2 capability gap",
    ):
        if text not in product_discovery:
            fail(f"product discovery must contain: {text}")
    management_mapping_position = product_discovery.index("## Management UI capability mapping")
    ui_decision_position = product_discovery.index("## UI-mode decision")
    role_position = product_discovery.index("## Actor, role, operation, and permission matrix")
    flow_boundary_position = product_discovery.index("## Flow-boundary decisions")
    storage_position = product_discovery.index("## Storage decision")
    if not role_position < flow_boundary_position < storage_position:
        fail("product discovery must derive roles, then Flow boundaries, then storage")
    if management_mapping_position > ui_decision_position:
        fail("product discovery must map Dex Web management capabilities before the UI-mode decision")

    dex_web = (references_dir / "dex-web-v2.md").read_text()
    for text in (
        "## Management UI design",
        "Design those contracts before proposing a custom management backend or UI",
        "### QR capture hint",
        "capture:qr-code",
        "without submitting the Action",
        "Superverse remains responsible for identity",
    ):
        if text not in dex_web:
            fail(f"Dex Web v2 reference must contain: {text}")


def check_connector_contributor() -> None:
    references_dir = CONNECTOR_CONTRIBUTOR / "references"
    if references_dir.exists():
        fail(
            "Dex Connector Contributor must defer to the target repository, "
            "not ship references"
        )
    check_reachable_links(CONNECTOR_CONTRIBUTOR, [])

    content = (CONNECTOR_CONTRIBUTOR / "SKILL.md").read_text()
    required = (
        "../dex-sdk/references/core/plugin-version-check.md",
        "../dex-sdk/SKILL.md",
        "../dex-sdk/references/go/go.md",
        "superdurable/dex-connectors-library",
        "Add <XYZ> to Dex official connector library",
        "Git remote identity",
        "user's verified GitHub fork",
        "explicit authorization",
        "`origin`",
        "`upstream`",
        "`AGENTS.md`",
        "files under `docs/`",
        "sole connector-authoring authority",
        "stop before connector implementation",
    )
    for text in required:
        if text not in content:
            fail(f"dex-connector-contributor/SKILL.md must contain: {text}")

    forbidden = (
        "../dex-app-builder/references/dex-web-v2.md",
        "<!-- connector-source:",
        "## Non-negotiable boundaries",
        "## Example gate",
        "## Handoff gate",
    )
    for text in forbidden:
        if text in content:
            fail(f"Dex Connector Contributor must not duplicate target-repository guidance: {text}")

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
        SDK: "true",
        CONNECTOR_CONTRIBUTOR: "true",
    }
    for skill, allow_implicit in expected.items():
        agent = skill / "agents" / "openai.yaml"
        content = agent.read_text()
        policy = f"allow_implicit_invocation: {allow_implicit}"
        if policy not in content:
            fail(f"{agent.relative_to(ROOT)} must contain: {policy}")
        skill_content = (skill / "SKILL.md").read_text()
        frontmatter = skill_content.split("---", 2)[1]
        if "disable-model-invocation: true" in frontmatter:
            fail(f"{(skill / 'SKILL.md').relative_to(ROOT)} must allow model invocation")


def check_plugin_version_check() -> None:
    if not PLUGIN_VERSION_CHECK.is_file():
        fail("dex-sdk/references/core/plugin-version-check.md must exist")
    content = PLUGIN_VERSION_CHECK.read_text()
    for text in (
        "Dex Skills lifecycle version check",
        "status=current",
        "status=outdated",
        "status=unavailable",
        "https://api.github.com/repos/superdurable/dex-skills/releases/latest",
        "without additional user approval",
        "vMAJOR.MINOR.PATCH",
        "first substantive Dex-related",
        "Do not show the notice in a non-Dex conversation",
    ):
        if text not in content:
            fail(f"plugin version check must contain: {text}")

    relative_links = {
        APP_BUILDER: "../dex-sdk/references/core/plugin-version-check.md",
        SDK: "references/core/plugin-version-check.md",
        CONNECTOR_CONTRIBUTOR: "../dex-sdk/references/core/plugin-version-check.md",
    }
    for skill, relative_link in relative_links.items():
        content = (skill / "SKILL.md").read_text()
        if relative_link not in content:
            fail(f"{skill.name}/SKILL.md must load the Dex Skills version check")


def check_standalone_bundle(version: str) -> None:
    if BUNDLE_VERSION.read_text().strip() != version:
        fail("dex-sdk/VERSION must match the root VERSION")

    baselines = BUNDLE_BASELINES.read_text()
    for baseline_name in BASELINE_FILES:
        expected = (ROOT / baseline_name).read_text().strip()
        if f"{baseline_name}={expected}" not in baselines:
            fail(f"bundle baselines must mirror {baseline_name}={expected}")

    with tempfile.TemporaryDirectory() as temporary_directory:
        install_root = Path(temporary_directory).resolve()
        for skill in (APP_BUILDER, SDK, CONNECTOR_CONTRIBUTOR):
            shutil.copytree(skill, install_root / skill.name)

        installed_skills = sorted(
            path.parent.name for path in install_root.glob("*/SKILL.md")
        )
        expected_skills = sorted(
            skill.name for skill in (APP_BUILDER, SDK, CONNECTOR_CONTRIBUTOR)
        )
        if installed_skills != expected_skills:
            fail("standalone bundle must copy exactly the three public Skills")

        for markdown in install_root.rglob("*.md"):
            prose = FENCED_BLOCK.sub("", markdown.read_text())
            for target in MARKDOWN_LINK.findall(prose):
                resolved = local_link_target(markdown, target)
                if resolved is None:
                    continue
                if not resolved.is_relative_to(install_root):
                    fail(
                        "standalone link escapes the installed bundle in "
                        f"{markdown.relative_to(install_root)}: {target}"
                    )
                if not resolved.exists():
                    fail(
                        "broken standalone link in "
                        f"{markdown.relative_to(install_root)}: {target}"
                    )


def command_hook(config: dict, event: str, matcher: str, path: Path) -> dict:
    events = config.get("hooks")
    if not isinstance(events, dict):
        fail(f"{path.relative_to(ROOT)} must define hooks")
    entries = events.get(event)
    if not isinstance(entries, list) or len(entries) != 1:
        fail(f"{path.relative_to(ROOT)} must define exactly one {event} hook")
    entry = entries[0]
    if matcher:
        if entry.get("matcher") != matcher:
            fail(f"{path.relative_to(ROOT)} {event} matcher must be {matcher}")
        handlers = entry.get("hooks")
        if not isinstance(handlers, list) or len(handlers) != 1:
            fail(f"{path.relative_to(ROOT)} {event} must contain one command hook")
        return handlers[0]
    return entry


def check_hook_configs(manifests: dict) -> None:
    expected_paths = {
        "codex": "./hooks/codex.json",
        "claude": "./hooks/claude.json",
        "cursor": "./hooks/cursor.json",
    }
    for name, expected in expected_paths.items():
        if manifests[name].get("hooks") != expected:
            fail(f"{name} manifest hooks must be {expected}")
        if not HOOK_CONFIGS[name].is_file():
            fail(f"missing {HOOK_CONFIGS[name].relative_to(ROOT)}")

    shared = ROOT / "hooks" / "hooks.json"
    if shared.exists():
        fail("hooks/hooks.json must not exist; clients require dedicated hook configs")
    if not VERSION_CHECK_SCRIPT.is_file():
        fail("hooks/version-check.mjs must exist")
    script = VERSION_CHECK_SCRIPT.read_text()
    for text in (
        "releases/latest",
        "CACHE_TTL_MS = 15 * 60 * 1000",
        "HTTP_TIMEOUT_MS = 1000",
        "PLUGIN_DATA",
        "CLAUDE_PLUGIN_DATA",
        'allowNetwork: client !== "cursor" || refreshOnly',
        "additionalContext",
        "additional_context",
    ):
        if text not in script:
            fail(f"version hook script must contain: {text}")
    for forbidden in (
        "npm install",
        "npx skills",
        "plugin update",
        "plugin marketplace upgrade",
    ):
        if forbidden in script:
            fail(f"version check hook must not install or update: {forbidden}")

    codex_path = HOOK_CONFIGS["codex"]
    codex = load_json(codex_path)
    if codex.get("description") != (
        "Checks GitHub for a newer stable Dex Skills version. "
        "Reads public release metadata only and never installs updates."
    ):
        fail("Codex hook review description must explain its read-only version check")
    codex_hook = command_hook(codex, "SessionStart", "startup|clear", codex_path)
    if codex_hook.get("type") != "command":
        fail("Codex SessionStart hook must be a command hook")
    if codex_hook.get("command") != 'node "${PLUGIN_ROOT}/hooks/version-check.mjs" --client codex':
        fail("Codex hook must run the shared version script with the Codex client")
    if codex_hook.get("timeout") != 2:
        fail("Codex hook timeout must be two seconds")
    if codex_hook.get("statusMessage") != "Checking for Dex Skills updates":
        fail("Codex hook status message must identify the version check")

    claude_path = HOOK_CONFIGS["claude"]
    claude = load_json(claude_path)
    claude_hook = command_hook(
        claude, "SessionStart", "startup|clear|fork", claude_path
    )
    if claude_hook.get("type") != "command" or claude_hook.get("command") != "node":
        fail("Claude SessionStart hook must run Node directly")
    if claude_hook.get("args") != [
        "${CLAUDE_PLUGIN_ROOT}/hooks/version-check.mjs",
        "--client",
        "claude",
    ]:
        fail("Claude hook must run the shared version script with the Claude client")
    if claude_hook.get("timeout") != 2:
        fail("Claude hook timeout must be two seconds")

    cursor_path = HOOK_CONFIGS["cursor"]
    cursor = load_json(cursor_path)
    if cursor.get("version") != 1:
        fail("Cursor hook config version must be 1")
    cursor_workspace = command_hook(cursor, "workspaceOpen", "", cursor_path)
    cursor_session = command_hook(cursor, "sessionStart", "", cursor_path)
    if cursor_workspace.get("command") != (
        'node "${CURSOR_PLUGIN_ROOT}/hooks/version-check.mjs" '
        "--client cursor --refresh-only"
    ):
        fail("Cursor workspaceOpen must prewarm the version cache")
    if cursor_session.get("command") != (
        'node "${CURSOR_PLUGIN_ROOT}/hooks/version-check.mjs" --client cursor'
    ):
        fail("Cursor sessionStart must inject the cached version result")
    if cursor_workspace.get("timeout") != 2 or cursor_session.get("timeout") != 2:
        fail("Cursor hook timeouts must be two seconds")
    for forbidden in ("resume", "compact", "SessionEnd", "sessionEnd"):
        if forbidden in json.dumps({"codex": codex, "claude": claude, "cursor": cursor}):
            fail(f"version hooks must not run on {forbidden}")


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
    check_hook_configs(manifests)

    codex = manifests["codex"]
    if codex.get("skills") != "./":
        fail("Codex manifest must discover root skills with ./")
    if "mainSkill" in codex:
        fail("Codex manifest must not invent a mainSkill field")
    interface = codex.get("interface")
    if not isinstance(interface, dict):
        fail("Codex manifest must define interface metadata")
    if interface.get("displayName") != "Dex":
        fail("Codex display name must be Dex")
    if interface.get("developerName") != "Super Durable":
        fail("Codex developer name must remain Super Durable")
    long_description = interface.get("longDescription", "")
    for routing_text in (
        "Dex App Builder",
        "Dex SDK",
        "Dex Connector Contributor",
    ):
        if routing_text not in long_description:
            fail(f"Codex long description must contain: {routing_text}")
    for field in ("composerIcon", "logo"):
        if interface.get(field) != "./assets/logo.png":
            fail(f"Codex {field} must use ./assets/logo.png")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or len(prompts) != 4:
        fail("Codex default prompts must expose all three Dex workflows")
    required_prompts = {
        "Discover, design, and build this Dex process application.",
        "Add <XYZ> to Dex official connector library.",
        "Design a reliable Dex Flow for this application.",
        "Prototype and build this Dex workflow.",
    }
    if set(prompts) != required_prompts:
        fail("Codex default prompts must use the natural-language workflow templates")
    if any("$dex-" in prompt for prompt in prompts):
        fail("Codex Plugin default prompts must not use standalone Skill syntax")

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
    normalized_agents = " ".join(agents.split())
    for required in (
        "The template and this plugin publish independently",
        "`TEMPLATE_BASELINE`",
        "scheduled template baseline workflow",
        "Superverse must advance its exact template and skill pins together",
        "never add a skill submodule or a floating branch reference",
    ):
        if required not in normalized_agents:
            fail(f"release agent rules must contain: {required}")
    pull_request_template = (ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md").read_text()
    if "Dex-AI-Platform-PR:" in pull_request_template:
        fail("pull request template must not require a paired repository")
    if "quick_validate.py" not in pull_request_template:
        fail("pull request template must require skill validation")

    updater = (ROOT / "script" / "update-template-baseline.py").read_text()
    for required in (
        "minimumSandboxImageContractRevision",
        '"dexSkill" in manifest',
        "update_versioned_manifests",
        "TEMPLATE_BASELINE",
    ):
        if required not in updater:
            fail(f"template baseline updater must contain: {required}")
    workflow = (ROOT / ".github" / "workflows" / "update-template-baseline.yml").read_text()
    for required in (
        "schedule:",
        "workflow_dispatch:",
        "automation/update-template-baseline",
        "script/update-template-baseline.py",
        "gh pr create",
        "gh workflow run validate.yml",
    ):
        if required not in workflow:
            fail(f"template baseline workflow must contain: {required}")


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
    check_skills(baseline)
    check_standalone_bundle(current_version)
    check_manifests(current_version)
    check_agent_rules()
    if arguments.base_ref:
        check_release_change(arguments.base_ref, current_version)
    print(f"validated superdurable-dex {current_version} with three root skills")


if __name__ == "__main__":
    main()
