---
name: dex-connector-contributor
description: Create or modify official Superdurable Dex connectors, operations, Triggers, and configuration UI units in superdurable/dex-connectors-library. Use for standalone official connector-library work and when dex-app-builder routes a confirmed connector gap to it. Do not use as the primary workflow for an application that merely consumes connectors.
---

# Dex Connector Contributor

Contribute one reviewable connector capability to the official
`superdurable/dex-connectors-library`. Preserve Dex durability, provider
correctness, credential isolation, generated contracts, and release order.

The host-neutral request template is:

```text
Add <XYZ> to Dex official connector library
```

## Session start

Before the first substantive Dex-related response, follow the shared
[Dex Skills version check](../dex-sdk/references/core/plugin-version-check.md). Prefer the
lifecycle hook status; run the Skill fallback only when that status is
`unavailable` or absent. Run it only once and never delay or block the task.

## Required foundations

Before changing connector behavior:

1. Read the sibling [Dex SDK skill](../dex-sdk/SKILL.md) completely.
2. Follow its progressive-disclosure routing, loading only the required Core
   references and the [Go handbook](../dex-sdk/references/go/go.md).
3. Read the shared [Dex Web v2 reference](../dex-app-builder/references/dex-web-v2.md)
   for Start Flow, Connections, configuration, and Studio behavior.
4. Read [repository workflow](references/repository-workflow.md).
5. Load only the task references that apply:
   [operations](references/operations.md), [Triggers](references/triggers.md),
   [UI units](references/ui-units.md), and
   [examples, testing, and PR](references/examples-testing-pr.md).

Dex SDK owns Flow, Step, retry, Attribute, Stream, RPC, and versioning
semantics. Do not restate or weaken them. The connector-library rules in this
skill are additional constraints.

Use this repository's sibling `dex-sdk` skill for Dex application semantics.
Do not load or install the superseded `dex-developer` skill, which pins older
releases.

## Scope gate

Use this skill only for the official connector library. If the task only uses a
published connector in an application, route to `dex-sdk` or
`dex-app-builder`. If a missing or defective connector blocks an application,
separate the connector contribution into this workflow; keep any temporary
application `go.work` or `replace` uncommitted until an exact connector release
exists.

Use only a provider's documented public API or official SDK. Do not scrape a
private endpoint, copy browser credentials, reverse-engineer an internal
protocol, or claim support that the provider does not publish.

## Contribution sequence

Use this order:

1. Resolve the connector-library checkout by verified Git remote identity—not
   by the chat's initial working directory or a directory name—using the target
   checkout discovery in [repository workflow](references/repository-workflow.md).
   Report the exact target checkout path before changing it.
2. Resolve and verify the user's GitHub fork using the discovery and user
   handoff in the repository workflow. Use its verified maintainer branch path
   only when the user explicitly chooses it. Reuse a safe checkout or create an
   isolated topic worktree from the latest `upstream/main` without disturbing
   unrelated files.
3. Inspect repository instructions and identify the provider capability,
   public contract, auth scopes, rate limits,
   idempotency support, pagination, event acknowledgement, and failure modes.
4. Update `connector.yaml`, then run code generation before provider code.
5. Implement the provider adapter and provider-facing tests.
6. Add Trigger and UI-unit behavior when the capability needs them.
7. Add or extend a connector-local runnable example.
8. Run the complete verification matrix and inspect generated/catalog drift.
9. Commit one clean module-scoped change, push to the user's fork (or the
   verified maintainer branch), open a ready-for-review PR against the official
   repository, and monitor required CI until it passes.

Do not skip the manifest-first step. Generated `Config`, `Credentials`,
definitions, branch constants, operation-specific factories, UI constants, and
defaults must remain derived from `connector.yaml`.

## Non-negotiable boundaries

- The current Connector SDK and official connector modules are Go-only.
  TypeScript is limited to optional configuration UI units. If another backend
  language is required, explain that it is unsupported and ask the user to open
  an issue; do not invent a connector runtime or application API.
- Make provider calls only from a Connector Step `Execute`. RPCs route or
  mutate Dex state; they do not call providers.
- Require only the happy-path branch by default. Mark every other operation
  branch `optional: true`; make one required only when the application must
  choose a distinct continuation and explain why.
- Default Execute durability to `async`. Use `sync` only when the operation is
  more likely than not to exceed five seconds, the Dex SDK heuristic that leaves
  margin inside the ASYNC local phase's limit of about seven seconds; a high
  timeout alone does not qualify.
- Size the heartbeat for silent calls. A non-streaming provider call emits no
  heartbeat, so a call longer than the one-minute default needs
  `heartbeatTimeout` at least equal to `executeMethodTimeout`, or streamed
  progress.
- Keep credentials and raw secrets out of Flow input, Attributes, Results,
  receipts, Streams, logs, generated values, fixtures, and release artifacts.
- Register every application-provided Attribute and Stream in the consuming
  Flow persistence schema.
- Pin an exact published `sdkgo` version in each connector module. Never commit
  a branch, pseudo-version, SHA, or local `replace`.
- If the connector exposes an SDK contract gap, verify the SDK and connector
  together locally, then publish the SDK PR and tag before opening the connector
  PR that consumes it.
- Release one connector module per PR unless a repository-wide mechanical
  change genuinely requires more.

## Example gate

A new connector or major capability normally includes a runnable example inside
that connector. Extend a suitable existing example instead of duplicating it.

- With a Trigger, demonstrate real provider event delivery to a typed Flow
  start and/or typed RPC target, including duplicate delivery and restart
  recovery.
- Without a Trigger, generate valid FDG 2.0 and run the example through Dex Web
  v2 **Start Flow**.

The example is part of acceptance, not illustrative pseudocode.

## Handoff gate

Do not call the contribution complete until:

- module-isolated race tests and vet pass with `GOWORK=off`;
- UI tests and production builds pass when UI exists;
- codegen, registry, catalog, real Dex integration, FDG 2.0, current Dex
  compatibility, and repository `make check` pass;
- safe live provider tests pass when credentials exist, or the PR names the
  exact unverified live behavior;
- the worktree contains one clean commit and no unrelated changes;
- the ready-for-review PR records test evidence and required CI is green.

Publish and monitor CI with the `gh` steps in
[examples, testing, and PR](references/examples-testing-pr.md#publish-and-monitor-ci).
Codex users who have an `$opr` workflow may use it for the same steps.
