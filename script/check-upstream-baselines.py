#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def fail(message: str) -> None:
    raise SystemExit(message)


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def require_revision(checkout: Path, expected: str, label: str) -> None:
    checkout = checkout.resolve()
    if not (checkout / ".git").exists():
        fail(f"{label} is not a Git checkout: {checkout}")
    actual = git(checkout, "rev-parse", "HEAD")
    resolved = git(checkout, "rev-parse", f"{expected}^{{commit}}")
    if actual != resolved:
        fail(f"{label} checkout {actual} does not match baseline {resolved}")


def require_text(path: Path, *needles: str) -> None:
    content = path.read_text()
    for needle in needles:
        if needle not in content:
            fail(f"{path} is missing required text: {needle}")


def require_ancestor(checkout: Path, ancestor: str, descendant: str, label: str) -> None:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=checkout,
        check=False,
    )
    if result.returncode != 0:
        fail(f"{label} {ancestor} is not an ancestor of {descendant}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dex-root", required=True, type=Path)
    parser.add_argument("--template-root", required=True, type=Path)
    arguments = parser.parse_args()

    server_baseline = (ROOT / "DEX_SERVER_BASELINE").read_text().strip()
    cli_baseline = (ROOT / "DEX_CLI_BASELINE").read_text().strip()
    template_baseline = (ROOT / "TEMPLATE_BASELINE").read_text().strip()
    require_revision(arguments.dex_root, cli_baseline, "Dex CLI")
    require_revision(arguments.template_root, template_baseline, "template")
    require_ancestor(arguments.dex_root, server_baseline, cli_baseline, "Dex Server baseline")

    require_text(
        arguments.dex_root / "cli" / "internal" / "flowviz" / "v2_directives.go",
        "GetDexSummary",
        "GetDexDisplay",
        "dex:group",
        "RPCOptions.Action",
        "ActionRequiresPermission",
        '"ui-slot"',
        '"capture"',
        '"qr-code"',
        "capture requires a source:user string input field",
    )
    require_text(
        arguments.dex_root / "cli" / "schema" / "flow-definition-graph.v2.schema.json",
        '"capture"',
        '"qr-code"',
    )
    require_text(
        arguments.dex_root / "cli" / "README.md",
        "--schema-version 2.0",
        "Go-only",
    )
    require_text(
        arguments.dex_root / "web" / "api" / "v2.go",
        "V2PermissionModeTrustedHeader",
        "V2WorkQueuePermissionsHeader",
        "Action permission denied",
        'json:"capture,omitempty"',
    )
    require_text(
        arguments.dex_root / "web" / "app" / "v2" / "workspace" / "qrScanner.ts",
        "await import('@zxing/browser')",
        "facingMode: { ideal: 'environment' }",
        "for (const track of stream.getTracks()) track.stop()",
    )
    require_text(
        arguments.dex_root / "sdk-go" / "README.md",
        "Once a permission has",
        "remains searchable after completion",
    )
    require_text(
        arguments.dex_root / "cli" / "internal" / "flowviz" / "go_connector_factory.go",
        "parseConnectorFactoryStep",
        "parseConnectorAnnotations",
        '"annotations"',
        '"connectionName"',
        '"moduleVersion"',
    )
    require_text(
        arguments.dex_root / "cli" / "internal" / "flowviz" / "go_connector_trigger.go",
        "collectConnectorTriggerBindings",
        '"bindingName"',
        "TriggerBindingFactoryConfigMarker",
    )
    require_text(
        arguments.dex_root / "cli" / "internal" / "dev" / "config.go",
        "connector-config-dir",
        "connector-release-override",
    )
    require_text(
        arguments.dex_root / "web" / "connector_connection_store.go",
        "connections.json",
        "TriggerBindings",
        "putTriggerBinding",
        "os.Rename",
    )
    require_text(
        arguments.dex_root / "web" / "connector_oauth.go",
        "code_verifier",
        "connectorOAuthResponseValue",
        "credentials[mapping.Credential]",
        "credentialSecrets",
    )
    require_text(
        arguments.dex_root / "cli" / "internal" / "flowviz" / "go_connector_configuration_ui.go",
        "ConnectorConfigurationUI",
        "ConnectorUIUnit",
        "ConnectorUIBinding",
        "compile-time literals",
    )
    require_text(
        arguments.dex_root / "web" / "connector_studio_command.go",
        "connectorStudioCommandRequest",
        "CONNECTOR_STUDIO_COMMAND_NOT_FOUND",
        "containsConnectorSecret",
        "https",
    )
    require_text(
        arguments.dex_root / "web" / "connector_use_configuration.go",
        "validateConnectorUseConfiguration",
        "allowedPointers",
        "Connector configuration path",
    )
    require_text(
        arguments.dex_root / "web" / "app" / "v2" / "connectors" / "ConnectorsPage.tsx",
        "provider.command.execute",
        "use.configuration.save",
        "connector.frame.resize",
        "Local override",
    )
    require_text(
        arguments.dex_root / "web" / "api" / "v2_start.go",
        "START_FLOW_DISABLED",
        "WORKER_UNHEALTHY",
        "v2StartStepInput",
        "SkipWaitFor: definition.Start.SkipWaitFor",
        "hostedStartRequestIdentity",
        "START_IDENTITY_CONFLICT",
    )
    require_text(
        arguments.dex_root / "web" / "api" / "v2.go",
        "requireEmbeddedMutationCSRF",
        "WEB_MUTATION_CSRF_INVALID",
        "subtle.ConstantTimeCompare",
    )
    require_text(
        arguments.dex_root / "web" / "project_configuration.go",
        "projectconfig",
        "APPLICATION_ENVIRONMENT_FORBIDDEN",
    )

    template_manifest = json.loads(
        (arguments.template_root / ".superverse" / "template.json").read_text()
    )
    template_version = template_manifest.get("templateVersion")
    if not isinstance(template_version, str) or SEMVER.fullmatch(template_version) is None:
        fail("template baseline must declare a stable templateVersion")
    expected_commands = {
        "bootstrap": "make bootstrap",
        "generate": "make generate",
        "checkFdgV2": "make check-fdg-v2",
        "checkContracts": "make check-contracts",
        "checkStatic": "make check-static",
        "build": "make build",
        "dev": "make dev",
        "releaseArtifacts": "make superverse-release-artifacts",
        "check": "make check",
    }
    if template_manifest.get("commands") != expected_commands:
        fail("template baseline must expose only the supported lean command set")
    require_text(
        arguments.template_root / ".gitignore",
        "/internal/api/generated/",
        "/web/src/api/generated/",
    )
    require_text(
        arguments.template_root / "dex-app.yaml",
        '"schemaVersion": "superverse.dev/dex-app/v1"',
        '"flowDefinitions"',
        '"connectors"',
    )
    require_text(
        arguments.template_root / "README.md",
        "## Hosted release artifacts",
        "make superverse-release-artifacts",
        "DEX_PROJECT_*",
        "projectconfig/provider",
    )
    require_text(
        arguments.template_root / "internal" / "connectorconfiguration" / "configuration.go",
        "projectconfig.LoadFromEnvironment",
        "ResolveApplicationEnvironment",
    )
    tracked_generated = git(
        arguments.template_root,
        "ls-files",
        "internal/api/generated",
        "web/src/api/generated",
    )
    if tracked_generated:
        fail("template baseline must not track generated OpenAPI clients")
    for removed_path in (
        "cmd/mock-server",
        "internal/mockserver",
        "docs/local-mock.md",
        "scripts/check-generated.sh",
        "scripts/run-mock-e2e.sh",
        "scripts/with-mock.sh",
        "web/e2e/mock-basic-process.spec.ts",
        "web/src/MockControls.tsx",
        "internal/process/integration_test.go",
        "scripts/run-e2e.sh",
        "web/e2e/basic-process.spec.ts",
        "web/playwright.config.ts",
    ):
        if (arguments.template_root / removed_path).exists():
            fail(f"template baseline still contains removed scaffolding: {removed_path}")
    template_web = json.loads((arguments.template_root / "web/package.json").read_text())
    if "test:e2e" in template_web.get("scripts", {}) or "@playwright/test" in template_web.get("devDependencies", {}):
        fail("source-only template must not install an application browser test framework")
    template_cli_baseline = (
        arguments.template_root / "DEX_CLI_BASELINE"
    ).read_text().strip()
    require_ancestor(
        arguments.dex_root,
        template_cli_baseline,
        cli_baseline,
        "template Dex CLI baseline",
    )
    template_server_baseline = (
        arguments.template_root / "DEX_SERVER_BASELINE"
    ).read_text().strip()
    require_ancestor(
        arguments.dex_root,
        template_server_baseline,
        server_baseline,
        "template Dex Server baseline",
    )
    template_go_mod = (arguments.template_root / "go.mod").read_text()
    template_sdk = re.search(
        r"(?m)^\s*github\.com/superdurable/dex/sdk-go\s+v([^\s]+)$",
        template_go_mod,
    )
    if template_sdk is None or SEMVER.fullmatch(template_sdk.group(1)) is None:
        fail("template baseline must pin a stable Dex Go SDK")
    require_text(
        arguments.template_root / "internal" / "process" / "flow.go",
        "GetDexSummary",
        "GetDexDisplay",
        "ActionRequiresPermission",
        "// dex:group",
    )
    if "// dex:action" in (
        arguments.template_root / "internal" / "process" / "flow.go"
    ).read_text():
        fail("template must use typed Action registration without dex:action")
    print("validated Dex Server, CLI, and basic-process template baselines")


if __name__ == "__main__":
    main()
