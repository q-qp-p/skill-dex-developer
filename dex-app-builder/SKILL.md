---
name: dex-app-builder
description: Primary entry point for designing and building Dex applications and process products. Use by default for Dex product, application, or workflow requests unless the user explicitly invokes $dex-sdk for standalone SDK work or $dex-connector-contributor for official connector-library work. Orchestrates business discovery, the UI decision, Go backend implementation, connector integration, local verification, and platform-ready handoff.
---

# Dex App Builder

Build the smallest coherent product that solves the confirmed business process. Keep discovery, the UI decision, backend modeling, and verification as explicit checkpoints.

## Session start

Before the first substantive response in each chat, follow the shared
[plugin version check](../references/plugin-version-check.md). Run it only once,
and never let it delay or block the user's task.

## Routing priority

Treat this skill as the default coordinator for Dex application, product, and
workflow requests. Keep end-to-end ownership while loading the specialist
skills only where their capability is required:

- load sibling `$dex-sdk` during backend design and implementation;
- load sibling `$dex-connector-contributor` only when an official connector,
  operation, Trigger, or configuration UI unit must be created or changed.

If the user explicitly invokes either specialist for a standalone task, honor
that choice and do not expand the work into this product workflow.

## Development workspace gate

Before implementation, confirm that the host provides a writable repository or
project workspace plus file-editing and command-execution tools. An existing
repository or a new empty repository both satisfy this requirement.

If no development workspace is available, explain that this plugin supplies
developer guidance rather than a hosted application builder. Continue business
discovery, architecture, and the implementation handoff when useful, but do not
claim to create files, run tests, build artifacts, or deploy the application.
Recommend continuing the confirmed plan in Codex or another coding-agent host
connected to the target repository.

## Repository bootstrap

Inspect the repository before selecting a language, creating manifests, or
installing dependencies. Treat a repository as effectively empty when it has no
application source or build manifests, even if it contains a README, license,
editor configuration, or other project placeholders.

For an effectively empty repository, initialize the application from
`https://github.com/superdurable/dex-template-basic-process` at the exact release
recorded in [TEMPLATE_BASELINE](../TEMPLATE_BASELINE). Materialize the template
inside the current repository while preserving its `.git` directory and any
intentional user files. Review collisions before writing, initialize the
template's pinned submodules, inspect `.superverse/template.json`, and use
`make bootstrap` as the first dependency/bootstrap command.

Do not invent a new application stack for an empty repository. In particular,
do not start a TypeScript Dex backend, create an ad hoc npm application, or
infer SDK versions from a neighboring workspace. Do not copy bootstrap code
from another project. Dex App Builder starts from the template's Go backend and
its optional React TypeScript UI skeleton.

When the repository already contains an application and build manifests,
preserve its intentional structure. Compare it with the pinned template and
adapt the required architecture without replacing existing work unless the user
explicitly approves that replacement.

## Fixed product boundary

- Use `https://github.com/superdurable/dex-template-basic-process` as the application template.
- Target Dex Server `v0.13.2`, Dex CLI `v0.13.8`, and Dex Go SDK `v0.13.1`. Before verification, advance the scaffold's pins together as described in [build, test, and handoff](references/build-test-handoff.md#baselines-and-local-cli), and confirm `dexcli version` is at least `v0.13.8`. Dex Web v2 is embedded in Server and CLI.
- Implement Dex backend code only with the Go SDK.
- Target strict Dex Web v2 / FDG 2.0 rendering. Never fall back to rendering v1.
- Treat Dex Web v2 as the process-management UI for Runs, Work Queue, search, details, edits, and Actions unless the user confirms a custom UI is necessary.
- A retained Hello World page and OpenAPI generation skeleton do not count as a custom process UI.
- Keep production Work Queue authorization behind a trusted authentication boundary. Dex Web's local permission selector is development-only.
- Keep credentials in a connector/runtime boundary. A Flow stores only a logical connection ID.
- Do not mutate another repository, fork, publish, deploy, upload, or open a pull request without authorization for that action.

Read [product discovery](references/product-discovery.md) before proposing architecture.

## Stage 1: confirm the business process and application surface

Begin with discussion, not code. Identify:

- process maintainer;
- managers, operators, approvers, terminal users, and participants;
- each role's allowed operations and the stable permission required by each human Action;
- external systems that trigger or participate in the process;
- whether each integration is a public external product or an
  organization-controlled internal service;
- start triggers, inputs, outputs, deadlines, waits, approvals, retries, recovery, audit, search, and sensitive data;
- whether Dex Web Run, Work Queue, display/edit fields, and Actions satisfy the complete process-management experience;
- whether an existing host authenticates users and maps roles to trusted permissions;
- whether the user needs any custom process UI beyond a non-business application shell.

Produce a compact role/operation/permission matrix, lifecycle proposal, UI
decision, and connector capability matrix. For every integration, record its
classification, required Trigger/Query/Mutation/UI capabilities, matching
released connector capability, and any contribution or internal-library gap.
Roles describe people or groups. Permissions describe individual allowed
operations. Resolve material ambiguity and obtain explicit user confirmation
before implementation.

If the process begins from Slack, email, a webhook, or another external source, model it as a Connector Trigger. The application decides whether the event starts a Flow or invokes a typed RPC. Read [connector architecture](references/connector-architecture.md) whenever an external integration is involved.

## Stage 2: implement the confirmed UI mode

Read [UI workflow](references/ui-workflow.md), then use exactly one mode.

### No custom UI

Use Dex Web v2 as the only process-management experience. Define indexed Attributes, summary/display fields, editable fields, human-action Steps, and Action RPCs so Run and Work Queue modes cover the confirmed process.

Adapt the template to retain only its future-ready architecture:

- a non-business React/Vite Hello World page;
- the Go HTTP server;
- the OpenAPI source and generation pipeline;
- generated Go server interfaces and TypeScript client;
- build, generated-code, and smoke-test commands;
- one non-business `GetApplicationInfo` operation returning the application name and optional Dex Web URL.

Remove every custom process-management operation and surface: approval, rejection, retry, escalation, status, display, list, search, detail, Action or Attribute proxies, dashboards, forms, queues, lifecycle mock state, and Mock Controls. Remove their handlers, services, fixtures, generated usages, and E2E tests. Do not keep speculative endpoints.

When the process needs a trigger webhook, retain only that OpenAPI operation and the verification and correlation code it requires. Do not turn the webhook server into a second management backend. External-provider webhooks use a dedicated Connector Trigger; the generic HTTP connector is internal-only.

Do not run the custom-UI mock approval checkpoint in this mode. If the product later needs custom UI behavior, reuse the retained architecture and enter the custom-UI workflow before implementing it.

### Custom UI

Use the full template. Agree on roles, screens, navigation, state, actions, validation, loading, empty, failure, recovery, accessibility, and responsive behavior. Implement the runnable React TypeScript experience against the template's mock mode.

Start the template with `make mock`. Use its Go in-memory mock API and visible Mock Controls to exercise the proposed lifecycle, actions, reminders, loading, recovery, and reset behavior without a Dex Server. Extend the mock behavior only for confirmed interactions; keep production Flow code and provider integrations out of that path.

Show or describe the verified mock and wait for explicit user approval. Do not connect a real Dex backend or begin production backend implementation before approval. After approval, keep only APIs required by the approved UI or integration ingress.

## Stage 3: design and implement the Flow

Read the sibling [Dex SDK skill](../dex-sdk/SKILL.md) completely, then follow its progressive-disclosure routing with [Go](../dex-sdk/references/go/go.md) as the only language. Load only the Core and Go references required by the approved design.

Dex SDK supplies the public SDK guidance. The platform constraints in this skill are stricter and take precedence: use only the Go SDK, keep external effects in `Execute`, keep `WaitFor` free of provider or Dex mutations, and require strict FDG 2.0 rendering.

Read [Dex Web v2](references/dex-web-v2.md) before editing a Flow. State the Flow identity, input/output, Steps, transitions, Attributes, Channels, RPCs, timers, retries, recovery, and connector boundaries before code.

Model each human operation as a typed Go Action with one **ActionRequiresPermission** option. Use lowercase domain keys such as **refund.manage** or **refund.message**. An Action RPC rechecks current state and uses business locks when its state check and effect must commit atomically.

Do not add projection-only locks. The Server atomically adds newly matched Action permissions to the Flow execution's Work Queue permission history. A historical match supports discovery; it does not prove current eligibility or caller authorization.

Keep external effects in `Execute`. `WaitFor` only declares durable conditions and must not query or mutate providers or Dex state.

For connectors:

1. inspect the released catalog and matching connector manifests in
   `superdurable/dex-connectors-library` before writing integration code;
2. compose the Flow from the latest compatible released capabilities wherever
   possible: Query/Mutation factories become Connector Steps, a Trigger target
   starts a typed Flow or invokes a typed RPC, and an application RPC that
   requests provider work commits its state and schedules a Connector Step
   instead of calling the provider itself;
3. do not add an application-local provider client, webhook adapter, or direct
   official SDK call when the connector library already supplies the required
   capability;
4. give every operation-specific factory a static `ConnectionName` matching
   the generated Connection's runtime name, and use generated
   `NewLocalConnection` with the Connector SDK local store for local testing;
5. for a public external product with a documented API or official SDK, require
   dedicated Connector Trigger, Query, Mutation, and UI capabilities as needed;
6. when that public connector or required operation/Trigger is absent or
   defective, read sibling
   [Connector Contributor](../dex-connector-contributor/SKILL.md) completely
   and use `$dex-connector-contributor` to create or modify it;
7. after the local connector change builds, immediately test the application
   against its local module using an uncommitted `go.work` or temporary Go
   `replace`, while the contributor workflow pushes its contribution branch
   (the user's fork by default) and opens the upstream PR against the official
   connector library;
8. never commit a branch, commit SHA, pseudo-version, `go.work`, or local
   replacement as a production dependency; after release, remove the local
   override, pin the exact connector tag, and rerun real integration and E2E
   coverage;
9. for an organization-controlled internal service, ask whether an internal
   connector library already exists and whether the user wants to create one
   when it does not; a new internal library uses the unified Connector SDK,
   manifest/codegen contract, credential boundary, and module-level tests;
10. use the generic HTTP connector only when the service is genuinely internal
    and the user does not choose a reusable internal connector capability.

Each Connector Step passes only its current operation result to a branch target. Use generated result aliases such as `ListThreadMessagesResult` or `PostThreadReplyResult`. Persist thread identity, customer input, recovery context, and other business state in an application Step and Attribute before entering the Connector Step. Map the provider operation input with the pure `MapToOperationInput`; never recover upstream context from a result envelope. Use `Annotations` only for graph grouping and explanation metadata. Omit `ResultAttribute` unless a display, RPC, audit, recovery operator, or another path must read the raw result outside the transition chain.

For every Trigger binding, give the generated factory a static connection name and binding name. Keep its matcher configuration separate from workspace credentials. Supply an application-owned `TriggerFilter` and `FlowIDResolver`, then choose either `NewDexFlowTriggerTarget` with a typed Flow and `FlowInputMapper` or `NewDexRPCTriggerTarget` with a typed RPC and `RPCInputMapper`. The filter is the final admission rule for channel, sender, text, tenant, required routing fields, and other domain constraints. Returning false consumes the event without calling Dex. Filter, resolver, and mapper callbacks are pure functions without error results. Do not add manifest-level Flow/RPC Trigger kinds or a configurable RPC-name string.

For an RPC target, register the application's bound method with application-owned `dex.RPCOptions`, then pass that method directly to the target. The application decides whether redelivery needs deduplication, which bounded domain state records it, and which business state or effect requires a lock. Do not add connector-owned persistence or locks to every Trigger RPC.

Make connector mutations idempotent and reconcile unknown outcomes query-first. A missing connector release blocks production handoff. Never invent an unreleased connector API.

## Stage 4: verify and hand off

Read [build, test, and handoff](references/build-test-handoff.md). Run the narrowest tests while iterating, then the template's full supported check. Every Flow must pass FDG 2.0 JSON analysis with `valid: true`.

For No custom UI, verify the Hello World page, `GetApplicationInfo` generated-client call, generated-code checks, production build, absence of management routes, Dex Web actions/display, and any retained webhook. For Custom UI, preserve the approved mock path and run `make test-mock-e2e` before real Dex verification.

Use a real Dex Server for waits, RPCs, Channels, retries, Worker replacement, terminal behavior, Work Queue permission history, and connector boundaries. Use deadline-based convergence rather than fixed sleeps.

Finish with:

- confirmed business, UI-mode, permission-boundary, and connector decisions;
- implemented and verified behavior;
- connector release or fork/PR status;
- exact test evidence;
- remaining limitations and release blockers;
- a clean Git commit suitable for future platform import.

Dex AI Platform import is not implemented yet. Say the project is ready for future upload only when no connector release blocker remains; never fabricate a command or deployment result.
