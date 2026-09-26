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

### Codex desktop app

Open the plugin browser, choose **Add a marketplace**, and use:

| Field | Value |
| --- | --- |
| Source | `https://github.com/superdurable/dex-skills` |
| Git ref | `main` |
| Sparse paths | Leave empty. |

Add the marketplace, open **Super Durable**, and install **Dex**. This route
does not require the separate Codex CLI.

### Codex CLI

Only use this route when `codex --version` works in the shell:

```bash
codex plugin marketplace add superdurable/dex-skills
codex
```

Inside Codex CLI, open `/plugins`, select the **Super Durable** marketplace,
and install **Dex**. There is no `codex plugin add` step in these instructions.

Open an existing repository or create an empty one, then start a new task. Use
`$dex-app-builder` for the primary product workflow. Explicitly invoke
`$dex-sdk` only for standalone SDK work or `$dex-connector-contributor` only
for standalone official connector-library contribution.

### Claude web and desktop

Open **Customize → Plugins → Add → Add marketplace**, choose **Add from a
repository**, and enter `https://github.com/superdurable/dex-skills`. Install
**Dex** from the **Super Durable** marketplace. Claude saves the installation
to the account, so it is also available in Claude Code when signed in with the
same account.

### Claude Code CLI

Run from a shell where the `claude` command is installed:

```bash
claude plugin marketplace add superdurable/dex-skills
claude plugin install superdurable-dex@superdurable
```

Or run the slash-command equivalents inside an interactive Claude Code session:

```text
/plugin marketplace add superdurable/dex-skills
/plugin install superdurable-dex@superdurable
```

Invoke `/superdurable-dex:dex-sdk`, `/superdurable-dex:dex-app-builder`, or
`/superdurable-dex:dex-connector-contributor`.

### Cursor desktop app

Import `https://github.com/superdurable/dex-skills` from **Customize → From
GitHub Repository**, then open **Dex**, select **Install**, and choose a user or
project scope. The three skills appear as `/dex-sdk`, `/dex-app-builder`, and
`/dex-connector-contributor`.

### Cursor CLI

Cursor's official documentation describes marketplace installation through
**Customize** and does not document a separate shell command for installing
this GitHub marketplace. Install the plugin through the desktop app; do not
guess a `cursor plugin install` command.

Agent Skills clients can install the same bundle directly:

```bash
npx skills add superdurable/dex-skills --all
```

## Upgrade

An active chat keeps the plugin version it loaded when the chat started. After
an upgrade, restart the client when applicable and begin a new chat in the
repository.

At the beginning of a new chat, each Dex skill makes a short, best-effort check
against the repository's current stable version. When a newer version exists,
the first substantive response includes a brief BTW notice with this upgrade
guide. The check is silent when the plugin is current or the network is
unavailable, and it never upgrades the plugin automatically.

### Codex desktop app

Open the plugin browser's marketplace management view, find **Super Durable**,
and select **Upgrade**. Wait for the upgrade to finish, restart the desktop app,
and start a new task. No Codex CLI command is required for this route.

### Codex CLI

Refresh only the Super Durable marketplace, then start a new Codex session:

```bash
codex plugin marketplace upgrade superdurable
codex
```

Inside Codex CLI, open `/plugins` and confirm that **Dex** is enabled.

### Claude Code CLI

Update Dex directly from a shell:

```bash
claude plugin update superdurable-dex@superdurable
```

Or update the marketplace inside an interactive Claude Code session:

```text
/plugin marketplace update superdurable
```

Start a new session after a manual update. To receive future releases
automatically, open `/plugin`, select **Marketplaces → Super Durable**, and
select **Enable auto-update**.

### Claude web and desktop

Claude's public web and desktop documentation does not describe a separate
per-user upgrade command. Organization-managed GitHub marketplaces are updated
by an owner from **Organization settings → Plugins & skills → Marketplaces →
Update**; account users receive the synced version. The Claude Code commands
above are the documented manual route for a personally registered marketplace.

### Cursor

For a GitHub-imported team marketplace, an administrator can click **Refresh**
or enable **Auto Refresh**, then users reload the Cursor window. Cursor does not
document a personal `cursor plugin update` shell command for a direct GitHub
import; manage that installation through **Customize** instead of guessing one.

## Migrating from the old plugin

The former plugin ID `dex` and invocation `$dex-developer` were replaced by
`superdurable-dex` and `$dex-sdk`. Remove or update the old marketplace install,
install **Dex** from the **Super Durable** marketplace, and start a new task so
the new skill names are discovered.

A direct skill install is not replaced by the plugin. If
`~/.claude/skills/dex-developer`, another client's skills-directory copy, or an
`npx skills` install of `dex-developer` exists, it keeps loading its older
pinned Server and CLI guidance and can shadow the plugin. Remove it with the
tool that installed it, install `superdurable-dex@superdurable`, and start a new
task.

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

When the target repository is empty or contains only placeholders such as a
README, App Builder first initializes it from the pinned
`superdurable/dex-template-basic-process` release. It preserves the repository's
Git history and intentional files, then uses the template's `make bootstrap`
path. It does not invent a TypeScript backend, create an ad hoc npm scaffold, or
borrow SDK setup from a neighboring project.

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
Go SDK `v0.13.1`. Before verification, advance the scaffold's Server and CLI
baseline files, `go.mod` SDK requirement, `.agents/skills` submodule pin, and
template contract test together, and confirm `dexcli version` meets the CLI
baseline. Dex Web v2 is embedded in the Server and CLI artifacts. Connector
integrations reuse released
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
cloning that fork locally. A maintainer with verified push access may
explicitly choose an upstream topic branch that follows the repository's branch
convention instead.

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
`connectors/google/spreadsheet/v0.7.0`. The snapshot deliberately trails newer
connector releases; new work pins the latest published component tag.

## Releases

The three skills and all client manifests share the version in `VERSION`. A merge
to `main` creates GitHub Release `v<version>` when that tag does not already
exist. See [CONTRIBUTING.md](CONTRIBUTING.md) for validation and release rules.

## License

[MIT](LICENSE)
