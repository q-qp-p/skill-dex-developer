# Dex Skills

Dex Skills is the official agent-skill monorepo for building with
[Superdurable Dex](https://docs.superdurable.io). One `superdurable-dex` plugin
ships three skills for Codex, Claude Code, and Cursor:

The plugin is displayed as **Dex**. `Super Durable` remains the marketplace
publisher, while the stable plugin ID remains `superdurable-dex`.

| Skill | Responsibility |
| --- | --- |
| `dex-app-builder` | Discover, prototype, implement, and locally verify an end-to-end Dex AI Platform product with a Go backend. |
| `dex-sdk` | Implement, debug, test, and operate Dex applications in Python, Go, Java, TypeScript, or Rust. |
| `dex-connector-contributor` | Create, verify, and upstream official connector operations, Triggers, and configuration UI units. |

Start with `dex-app-builder` for Dex product, application, and process work. It
loads the specialist `dex-sdk` and `dex-connector-contributor` skills when the
confirmed design requires them. Invoke a specialist directly only for a
standalone SDK or official connector-library task. Install the complete plugin
so all three skills are present.

## Requires a coding workspace

Dex Skills is a developer plugin, not a hosted application builder. To create
or modify an application, use it in Codex or another coding-agent host that has
a writable repository or project workspace plus file-editing and command tools.
The workspace can be an existing repository or a new empty repository.

Without that workspace, the skills can still help with business discovery,
architecture, and an implementation handoff. They cannot create project files,
run tests, build artifacts, or deploy the application from an ordinary chat.

## Install

### Codex

```bash
codex plugin marketplace add superdurable/dex-skills
codex plugin add superdurable-dex@superdurable
```

Open an existing repository or create an empty one, then start a new task. Use
`$dex-app-builder` for the primary product workflow. Explicitly invoke
`$dex-sdk` only for standalone SDK work or `$dex-connector-contributor` only
for standalone official connector-library contribution.

### Claude Code

Run inside Claude Code:

```text
/plugin marketplace add superdurable/dex-skills
/plugin install superdurable-dex@superdurable
/reload-plugins
```

Invoke `/superdurable-dex:dex-sdk`, `/superdurable-dex:dex-app-builder`, or
`/superdurable-dex:dex-connector-contributor`.

### Cursor

Import `https://github.com/superdurable/dex-skills` from **Customize → From
GitHub Repository**, then install `superdurable-dex`. The three skills appear
as `/dex-sdk`, `/dex-app-builder`, and `/dex-connector-contributor`.

Agent Skills clients can install the same bundle directly:

```bash
npx skills add superdurable/dex-skills --all
```

### Migrating from the old plugin

The former plugin ID `dex` and invocation `$dex-developer` were replaced by
`superdurable-dex` and `$dex-sdk`. Remove or update the old marketplace install,
install `superdurable-dex@superdurable`, and start a new task so the new skill
names are discovered.

## Dex SDK

`dex-sdk` uses progressive disclosure. Shared semantics live under
`dex-sdk/references/core/`, and each supported language has a matching handbook.
The skill inspects the project's installed SDK and version-matched runnable
sources before choosing exact APIs.

Exact source excerpts are pinned to the Dex release in `DEX_BASELINE`. CI checks
that every marked snippet remains a contiguous excerpt of its declared source.
The project dependency and lockfile remain authoritative when versions differ.

## Dex App Builder

`dex-app-builder` starts with business discovery: process maintainers, managers,
terminal users, permissions, triggers, actions, waits, approvals, recovery, and
audit requirements. It then confirms **No custom UI** or **Custom UI**.

No custom UI uses Dex Web v2 for every management interaction. The application
keeps only a non-business Hello World page, one `GetApplicationInfo` OpenAPI
operation, and the Go/OpenAPI/React generation skeleton for future evolution.
It removes approval, display, status, list, detail, Action-proxy, mock-lifecycle,
and other process-management surfaces. A confirmed trigger webhook may remain
as integration ingress.

For a custom frontend, start with `make mock`. The template runs a Go in-memory
mock API, Vite hot reload, and visible Mock Controls for lifecycle progression,
reminders, one-time failures, Retry, and Reset. Approve those interactions
before connecting the production Go/Dex backend. Run `make test-mock-e2e` for
the mock journey, then `make check` for real Dex durability and rendering.

Backend implementation is Go-only, starts from
`superdurable/dex-template-basic-process`, and must satisfy strict Dex Web v2 /
FDG 2.0 rendering. The supported stack is basic-process release `v0.2.1`
(template contract `1.4.1`), Dex Server `v0.13.2`, Dex CLI `v0.13.8`, and Dex
Go SDK `v0.13.1`. Advance the scaffold's Server and CLI baseline files to these
versions before verification. Dex Web v2 is embedded in the Server and CLI
artifacts. Connector integrations reuse released
dedicated connectors from `superdurable/dex-connectors-library`. Generic HTTP
is reserved for controlled internal systems; a missing or defective
external-provider connector routes to `dex-connector-contributor` and blocks
production handoff until released.

Flow design prefers existing released connector capabilities throughout:
Query/Mutation factories become Connector Steps, Triggers start typed Flows or
invoke typed RPCs, and RPC-requested provider work moves to a Connector Step.
When a public product has a documented API or official SDK but lacks the needed
connector, operation, or Trigger, App Builder routes the gap to
`dex-connector-contributor`. The application can test the local connector
immediately through an uncommitted Go `replace` while its fork and upstream PR
are reviewed, then must pin the exact release. For controlled internal services,
App Builder asks whether an internal connector library already exists or should
be created with the unified Connector SDK before falling back to generic HTTP.

For Go applications, Dex Web reads statically named Connector Steps and Trigger
bindings from FDG 2.0. It configures released Gmail, Slack, GitHub, or other
supported connectors in the local **Connections** view. The default plaintext
development store is `~/.dex/connectors/connections.json`; pass
`--connector-config-dir` to isolate a stack. Start the application with
**DEX_CONNECTOR_CONFIG_FILE** set to the absolute path shown by Dex Web.
The mock validates HTTP and UI behavior only; it cannot prove Dex durability,
Worker replacement, Timer, or RPC semantics. The workflow finishes with local
tests and a clean handoff ready for future Dex AI Platform upload; it does not
claim that upload is available today.

## Dex Connector Contributor

`dex-connector-contributor` is limited to official work in
`superdurable/dex-connectors-library`. It starts from a provider's documented
public API or official SDK, updates `connector.yaml` and generated contracts,
implements provider behavior, adds Trigger and configuration UI units when
needed, and includes a runnable connector-local example. It first discovers and
verifies the user's GitHub fork; when none exists, it asks permission, opens the
official fork page, and waits for the user to click **Create fork** before
cloning that fork locally.

The workflow loads `dex-sdk` Core and Go semantics plus the shared Dex Web v2
reference. It validates module-isolated race tests and vet, UI tests/build,
codegen and catalog drift, real Dex integration, strict FDG 2.0, current Dex
compatibility, and repository checks. Trigger examples exercise typed Flow/RPC
routing and replay. Operation-only examples run through Dex Web v2 **Start
Flow**. It finishes with a clean, ready-for-review PR and monitored CI.

Connector source excerpts are pinned to the repository snapshot in
`CONNECTOR_LIBRARY_BASELINE`. The reference releases are Connector SDK
`sdkgo/v0.8.0`, Slack `connectors/slack/v0.9.0`, Gmail
`connectors/google/gmail/v0.10.0`, and Google Sheets
`connectors/google/spreadsheet/v0.7.0`.

## Releases

The three skills and all client manifests share the version in `VERSION`. A merge
to `main` creates GitHub Release `v<version>` when that tag does not already
exist. See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and release rules.

## License

[MIT](LICENSE)
