---
name: dex-app-builder
description: Primary and only implicit entry point for Dex requests. Designs and builds applications and process products with the pinned basic-process template stack, routes standalone SDK work to dex-sdk, and routes official connector-library creation or modification to dex-connector-contributor. Orchestrates business discovery, the UI decision, Go backend implementation, connector integration, local verification, and platform-ready handoff.
---

# Dex App Builder

Build the smallest coherent product that solves the confirmed business process. Keep discovery, the UI decision, backend modeling, and verification as explicit checkpoints.

## Session start

Before the first substantive Dex-related response, follow the shared
[Dex Skills version check](../dex-sdk/references/core/plugin-version-check.md). Prefer the
lifecycle hook status; run the Skill fallback only when that status is
`unavailable` or absent. Run it only once and never delay or block the task.

## Routing priority

This is the only implicitly invoked Dex skill. Classify the initial request
before product discovery, repository bootstrap, or any other App Builder work:

- For standalone official connector-library creation or modification—including
  a connector, operation, Trigger, or configuration UI unit—read the sibling
  [Connector Contributor](../dex-connector-contributor/SKILL.md) completely and
  make it the owning workflow. The user's request already authorizes this
  routing decision; do not ask them to invoke the specialist again, and do not
  enter product discovery.
- For standalone Dex SDK implementation, debugging, testing, or operations,
  read the sibling [Dex SDK](../dex-sdk/SKILL.md) completely and make it the
  owning workflow. Do not expand it into a product workflow.
- For a Dex product, application, or business process—including application use
  of a published connector—continue with App Builder. Load Dex SDK during
  backend design and implementation. If this workflow later confirms a missing
  or defective official connector capability, load Connector Contributor for
  that contribution while retaining end-to-end application ownership here.

If either sibling entrypoint cannot be read from the installed three-skill
bundle, report that the installed bundle is incomplete and direct the user to
update or reinstall it. Do not search arbitrary plugin-cache paths, substitute
the superseded `dex-developer` skill, or infer that a specialist is unavailable
from the current repository's instructions.

If the user explicitly invokes either specialist, honor that choice without
running this routing gate or expanding the task into this product workflow.

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

## Template stack authority and repository bootstrap

Inspect the repository before selecting a language, creating manifests, or
installing dependencies. Treat a repository as effectively empty when it has no
application source or build manifests, even if it contains a README, license,
editor configuration, or other project placeholders.

For an effectively empty repository, initialize the application from
`https://github.com/superdurable/dex-template-basic-process` at the exact release
recorded in the [bundle baselines](../dex-sdk/references/core/bundle-baselines.md).
Materialize the template
inside the current repository while preserving its `.git` directory and any
intentional user files. Review collisions before writing, do not initialize or
read project-local agent-skill submodules, inspect `.superverse/template.json`,
and use `make bootstrap` as the first dependency/bootstrap command. The
installed Dex Skills release loaded by the current coding-agent host is the
only skill authority. In Superverse Coding Sandbox, the runtime supplies that
release. External developers install the released plugin in Codex, Claude Code,
Cursor, or another Agent Skills-compatible host. Never assume a fixed skill
filesystem path.

For a new or effectively empty application, `TEMPLATE_BASELINE` is the
application stack authority. Before proposing implementation, inspect that
immutable template release's `go.mod`, `go.sum`, `web/package.json`,
`web/package-lock.json`, `DEX_SERVER_BASELINE`, `DEX_CLI_BASELINE`, Makefile,
and `.superverse/template.json`. Preserve their exact languages, module and
package versions, lockfiles, generated-code tools, directory layout, and
bootstrap/test commands unless the user explicitly requests a stack or version
change.

In the first implementation update for an effectively empty repository, name
the pinned template release and state that its Go backend and exact dependency
pins will be used. If the template release cannot be inspected or materialized,
report that blocker; do not fall back to a self-selected stack or install any
dependencies.

`DEX_BASELINE`, `DEX_SERVER_BASELINE`, and `DEX_CLI_BASELINE` in this skill
repository pin reference documentation and capability validation. They do not
authorize upgrading an application's template-pinned dependencies or runtime
baselines. Do not select a newer Dex Go SDK independently, run an upgrade
because a registry has a newer version, or copy versions from another project.

Do not invent a new application stack for an empty repository. In particular,
do not start a TypeScript Dex backend. Do not start a Node Dex backend, create
an ad hoc npm application, infer SDK versions from a neighboring workspace, or
copy bootstrap code from another project. TypeScript is limited to the
template's optional React frontend and generated client. The Dex backend and
application-side Connector SDK integration are Go-only.

If the user explicitly requests a non-template stack or dependency upgrade,
explain the compatibility and verification consequences before editing. A
non-Go backend is outside the Dex App Builder and Dex AI Platform path and
cannot use the current Connector SDK. Route an explicitly requested standalone
non-Go Dex application through `dex-sdk`; do not imply that Go-only Connector
capabilities remain available.

When the repository already contains an application and build manifests,
preserve its intentional structure rather than silently replacing it. Compare
it with the pinned template. If it is not compatible with the Go-only platform
and Connector boundary, stop before implementation and ask whether to adopt the
template stack or continue as an explicitly requested standalone SDK project.

## Fixed product boundary

- Use `https://github.com/superdurable/dex-template-basic-process` as the application template.
- Use the exact Dex Go SDK, Dex Server, Dex CLI, Go toolchain, Node packages, generators, and commands pinned by the `TEMPLATE_BASELINE` release. Do not advance the scaffold independently. Dex Web v2 is embedded in the template-pinned Server and CLI.
- Implement Dex backend code only with the Go SDK.
- The current Connector SDK supports application integration only from Go. Never replace a Connector with direct provider code merely to support another backend language.
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
- durable facts, their owning business identity, expected read/write paths,
  cross-Flow reuse, volume, contention, search, and retention requirements;
- whether Dex Web Run, Work Queue, display/edit fields, and Actions satisfy the complete process-management experience;
- whether an existing host authenticates users and maps roles to trusted permissions;
- whether the user needs any custom process UI beyond a non-business application shell.

Produce a compact role/operation/permission matrix, lifecycle proposal, storage
decision matrix, UI decision, and connector capability matrix. For every
durable fact, record its owner, access pattern, scale/contention expectation,
Dex primitive, and any proven reason an external store is required. For every
integration, record its classification, required Trigger/Query/Mutation/UI capabilities, matching
released connector capability, and any contribution or internal-library gap.
Roles describe people or groups. Permissions describe individual allowed
operations. Resolve material ambiguity and obtain explicit user confirmation
before implementation.

If the process begins from Slack, email, a webhook, or another external source, model it as a Connector Trigger. The application decides whether the event starts a Flow or invokes a typed RPC. Read [connector architecture](references/connector-architecture.md) whenever an external integration is involved.

## Stage 2: establish the confirmed application surface

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

Create only a low-fidelity static wireframe in the template React/Vite frontend.
Represent the necessary pages with headings, labels, placeholder boxes, inputs,
buttons, and ordinary links. Multiple pages must have stable, directly openable
local URLs and working link navigation.

The wireframe may use React for static markup, but it must not use application
state or effects, API or generated-client calls, local storage, timers, a mock
server, Mock Controls, provider integrations, images, custom icons, animation,
branding, or visual polish. Buttons and inputs remain inert unless a link is
needed to show the approved navigation path. Use minimal neutral styling and do
not model loading, validation, success, failure, or recovery behavior yet.

Run only the template's Vite frontend preview, verify that each page URL renders,
and give the user a compact inventory of page names, purposes, and direct links.
Ask for explicit confirmation of the page set, field and action placement, and
navigation. Do not turn this checkpoint into an aesthetic review or iterate on
visual design.

## Stage 3: design the Flow, Connectors, and OpenAPI contract, then implement the backend

Read the sibling [Dex SDK skill](../dex-sdk/SKILL.md) completely, then follow its progressive-disclosure routing with [Go](../dex-sdk/references/go/go.md) as the only language. Load only the Core and Go references required by the approved design.

Dex SDK supplies the public SDK guidance. The platform constraints in this skill are stricter and take precedence: use only the Go SDK, keep external effects in `Execute`, keep `WaitFor` free of provider or Dex mutations, and require strict FDG 2.0 rendering.

Read [Dex Web v2](references/dex-web-v2.md) before editing a Flow. State the Flow identity, input/output, Steps, transitions, Attributes, Channels, RPCs, timers, retries, recovery, and connector boundaries before code.

### Dex-first backend storage

Use Dex Flow state as the default durable application store. Read the shared
[data-handling guidance](../dex-sdk/references/core/data-handling.md) and the Go
[data-handling](../dex-sdk/references/go/data-handling.md) and
[entity-state patterns](../dex-sdk/references/go/patterns.md) before choosing a
database, cache, or ORM.

- Keep cohesive Flow-owned current state in typed Attributes.
- Use AttributeMaps with exact instance loads for independently accessed
  records, bounded chunks, partitions, and keyed entities.
- Use indexed Attributes and Dex search for supported list and lookup paths,
  typed RPCs for application reads and mutations, Channels for queued intent,
  and Dex's blob path for large durable values.
- When several processes need the same durable domain facts, prefer a dedicated
  stable domain/entity Flow that owns those Attributes or AttributeMaps and
  exposes typed application operations. Cross-Flow reuse alone is not a reason
  to introduce a database or duplicate state in each process Flow.

Do not add an external database, cache, ORM, outbox, or shadow read model merely
because the product has durable domain data or may need more queries later. Add
external storage only after a concrete confirmed requirement exceeds Dex's
storage and access model, such as complex or ad-hoc secondary indexes,
full-text/vector search, high-concurrency reads and writes against one hot
record that cannot accept Attribute-lock serialization, relational joins or
transactions across independently owned records, or analytics that require
large cross-Flow scans.

Before adding application-managed external storage, evaluate
Attribute/AttributeMap partitioning, bounded chunking, exact loads, indexed
Attributes, typed RPCs, and—when the state remains Dex-authoritative but needs
a separate query shape—Dex Attribute Store synchronization. If an external
store is still required, document the exact unsupported operation and expected
scale/SLO, assign one authoritative owner for every fact, define projection or
synchronization and recovery semantics, and test failure and reconciliation.
“Future flexibility” is not a sufficient reason.

For Custom UI, design the application OpenAPI contract in the same pass as the
Flow and Connector boundaries. Map each approved wireframe action to an
application-level operation backed by a Flow start, typed RPC, query, or
confirmed integration ingress. Define authentication and permission checks,
idempotency, asynchronous status, request and response types, validation,
errors, retry behavior, and terminal outcomes. Keep Dex Steps, Channels,
Attributes, and other execution internals out of the public HTTP contract.

Before implementing backend handlers, update `openapi/openapi.yaml` as the
contract source and run the template generation command. Implement the Go HTTP
boundary through the generated server interfaces and reserve the generated
TypeScript client for the later UI integration stage. Never hand-write parallel
request, response, or client types. Do not resume dynamic frontend work while
the Go Flow, Connector, and application boundary are being implemented.

Start Dex Web as soon as the first Flow graph exists. The moment a Flow source first renders with `dexcli visualize --schema-version 2.0 --json` (even with warnings), and before finishing implementation or tests:

1. render every Flow file into one persistent `--flow-rendering-dir` directory;
2. start one long-lived `dexcli dev` for the user in the background on stable ports with persistent state, passing that directory and any `--connector-release-override` a local connector needs;
3. give the user the Dex Web URL right away so they can inspect the graph, Connections, and Run views while you continue;
4. start the application Worker against that stack as soon as it compiles, so Runs appear live.

Keep that stack running for the rest of the task. Re-render the graphs after each Flow change and restart only that stack when Dex Web does not pick them up. Run automated tests on their own isolated stacks with free ports and temporary state, so tests never disturb or replace the stack the user is watching.

Model each human operation as a typed Go Action with one **ActionRequiresPermission** option. Use lowercase domain keys such as **refund.manage** or **refund.message**. An Action RPC rechecks current state and uses business locks when its state check and effect must commit atomically.

Do not add projection-only locks. The Server atomically adds newly matched Action permissions to the Flow execution's Work Queue permission history. A historical match supports discovery; it does not prove current eligibility or caller authorization.

Keep external effects in `Execute`. `WaitFor` only declares durable conditions and must not query or mutate providers or Dex state.

For connectors:

1. fetch the canonical published catalog at
   `https://superdurable.github.io/dex-connectors-library/catalog.yaml` before
   selecting a connector or writing provider integration code;
2. match every required Trigger, Query, Mutation, and UI capability by exact
   kind and name; a provider or connector name alone is not a match;
3. derive the component tag from the catalog's `directory` and `version`,
   verify that published tag, and inspect that tag's immutable
   `connector.yaml` for auth, configuration, input/output, branches,
   idempotency, Trigger, UI, and generated Go package contracts;
4. record the catalog URL, connector ID, exact capability, version/tag, and
   immutable manifest URL in the connector capability matrix. If the catalog,
   tag, or manifest cannot be read and verified, stop connector-dependent
   implementation and report the blocker; do not infer support from memory,
   an untagged branch, or a provider SDK;
5. compose the Flow from the latest compatible released capabilities wherever
   possible: Query/Mutation factories become Connector Steps, a Trigger target
   starts a typed Flow or invokes a typed RPC, and an application RPC that
   requests provider work commits its state and schedules a Connector Step
   instead of calling the provider itself;
6. do not add an application-local provider client, webhook adapter, or direct
   official SDK call when the connector library already supplies the required
   capability;
7. give every operation-specific factory a static `ConnectionName` matching
   the generated Connection's runtime name, and use generated
   `NewLocalConnection` with the Connector SDK local store for local testing;
8. for a public external product with a documented API or official SDK, require
   dedicated Connector Trigger, Query, Mutation, and UI capabilities as needed;
9. when that public connector or required operation/Trigger is absent or
   defective, read sibling
   [Connector Contributor](../dex-connector-contributor/SKILL.md) completely
   and ask for authorization to use `dex-connector-contributor` to create or
   modify it; never bypass the gap with direct provider code;
10. after the local connector change builds, immediately test the application
   against its local module using an uncommitted `go.work` or temporary Go
   `replace`, while the contributor workflow pushes its contribution branch
   (the user's fork by default) and opens the upstream PR against the official
   connector library;
11. never commit a branch, commit SHA, pseudo-version, `go.work`, or local
   replacement as a production dependency; after release, remove the local
   override, pin the exact connector tag, and rerun real integration and E2E
   coverage;
12. for an organization-controlled internal service, ask whether an internal
   connector library already exists and whether the user wants to create one
   when it does not; a new internal library uses the unified Connector SDK,
   manifest/codegen contract, credential boundary, and module-level tests;
13. use the generic HTTP connector only when the service is genuinely internal
    and the user does not choose a reusable internal connector capability.

Each Connector Step passes only its current operation result to a branch target. Use generated result aliases such as `ListThreadMessagesResult` or `PostThreadReplyResult`. Persist thread identity, customer input, recovery context, and other business state in an application Step and Attribute before entering the Connector Step. Map the provider operation input with the pure `MapToOperationInput`; never recover upstream context from a result envelope. Use `Annotations` only for graph grouping and explanation metadata. Omit `ResultAttribute` unless a display, RPC, audit, recovery operator, or another path must read the raw result outside the transition chain.

For every Trigger binding, give the generated factory a static connection name and binding name. Keep its matcher configuration separate from workspace credentials. Supply an application-owned `TriggerFilter` and `FlowIDResolver`, then choose either `NewDexFlowTriggerTarget` with a typed Flow and `FlowInputMapper` or `NewDexRPCTriggerTarget` with a typed RPC and `RPCInputMapper`. The filter is the final admission rule for channel, sender, text, tenant, required routing fields, and other domain constraints. Returning false consumes the event without calling Dex. Filter, resolver, and mapper callbacks are pure functions without error results. Do not add manifest-level Flow/RPC Trigger kinds or a configurable RPC-name string.

For an RPC target, register the application's bound method with application-owned `dex.RPCOptions`, then pass that method directly to the target. The application decides whether redelivery needs deduplication, which bounded domain state records it, and which business state or effect requires a lock. Do not add connector-owned persistence or locks to every Trigger RPC.

Make connector mutations idempotent and reconcile unknown outcomes query-first. A missing connector release blocks production handoff. Never invent an unreleased connector API.

## Stage 4: integrate the Custom UI, verify, polish, and hand off

Read [build, test, and handoff](references/build-test-handoff.md). Run the narrowest tests while iterating, then the template's full supported check. Every Flow must pass FDG 2.0 JSON analysis with `valid: true`.

For No custom UI, verify the Hello World page, `GetApplicationInfo` generated-client call, generated-code checks, production build, absence of management routes, Dex Web actions/display, and any retained webhook.

For Custom UI, wait until the Go backend and its real Dex and Connector paths
run before replacing inert wireframe controls with generated TypeScript client
calls. Then implement the confirmed loading, validation, empty, success,
failure, retry, recovery, and terminal behavior and run the real end-to-end
journey. Update the template mock server only after the OpenAPI contract is
fixed, and use it as a contract-compatible test double; `make mock` and
`make test-mock-e2e` are verification tools, not permission to delay backend
work behind a complete mock application.

Only after the real Dex and Connector end-to-end journey passes may the Custom
UI add images, custom icons, branding, animation, refined responsive behavior,
or other visual polish. Rerun frontend tests, mock E2E, real E2E, and the
production build after polishing. Do not generate or source visual assets
before this stage.

Use a real Dex Server for waits, RPCs, Channels, retries, Worker replacement, terminal behavior, Work Queue permission history, and connector boundaries. Use deadline-based convergence rather than fixed sleeps.

Finish with:

- confirmed business, UI-mode, permission-boundary, and connector decisions;
- implemented and verified behavior;
- connector release or fork/PR status;
- exact test evidence;
- remaining limitations and release blockers;
- a clean Git commit suitable for future platform import.

Dex AI Platform import is not implemented yet. Say the project is ready for future upload only when no connector release blocker remains; never fabricate a command or deployment result.
