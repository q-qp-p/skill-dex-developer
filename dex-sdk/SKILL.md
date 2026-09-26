---
name: dex-sdk
description: Technical sub-skill for implementing, debugging, testing, and operating applications with the Superdurable Dex SDK in Python, Go, Java, TypeScript, or Rust. Use when the user explicitly invokes $dex-sdk for standalone SDK work or when $dex-app-builder or $dex-connector-contributor loads it. Do not select it as the primary workflow for Dex product, application, or business-process requests.
---

# Dex SDK

Build reliable applications through Dex's public programming model. Keep the user's experience in Dex terms and APIs.

## Session start

Before the first substantive response in each chat, follow the shared
[plugin version check](../references/plugin-version-check.md). Run it only once,
and never let it delay or block the user's task.

## Stay at the application boundary

- Model behavior with Flows, Steps, Waits, Attributes, Channels, Streams, RPCs, Timers, SubFlows, Workers, and the Client.
- Use Dex Web, dexcli, SDK errors, and application logs for inspection and recovery.
- Use typed Flow RPCs as the application boundary for reading and writing Attributes, AttributeMaps, Channels, and ChannelMaps. Do not use removed Client state APIs. Attribute match remains the blocking observation API.
- Do not expose Dex Server internals as application requirements. Discuss them only when the user explicitly asks to develop Dex itself.
- Diagnose read-only by default. Do not stop, time travel, publish, invoke, delete, edit, or otherwise mutate a Flow unless the user authorizes it.

## Establish source authority

Before writing code, identify the language, package manager, installed Dex SDK version, registry, Worker and Client bootstrap, and repository test commands.

Preserve the installed SDK version unless the user asks to upgrade. The project's source, lockfile, installed SDK, and version-matched examples are authoritative. This bundle's exact API excerpts are pinned to the immutable release tag in their visible source links and recorded in the source repository's `DEX_BASELINE`; use them as guidance, not as evidence that a different installed version has the same signature.

If the project version differs from the baseline, name the matching installed-source path or immutable tag/commit used before writing exact API code. If that source is unavailable, stop at the version-independent Flow model, identify what is needed, and ask to inspect or fetch it. Never claim verification without an auditable version-matched source, label baseline syntax as compatible with an unverified version, or invent a Dex API.

Check for a superseded copy of this skill. `dex-developer` is its former name. A direct install such as `~/.claude/skills/dex-developer`, or one added with `npx skills`, is not updated by the plugin and can remain the Dex skill that loads, with older pinned Server and CLI releases. When a `dex-developer` skill is also available, tell the user to remove that direct install, install `superdurable-dex@superdurable`, and start a new session; do not delete it yourself. When `dexcli version` is newer than the source repository's `DEX_CLI_BASELINE`, say that the loaded guidance may trail the installed CLI and suggest updating the plugin.

## Load references progressively

Always read the entry page for the project's language first:

- [Python](references/python/python.md)
- [Go](references/go/go.md)
- [Java](references/java/java.md)
- [TypeScript](references/typescript/typescript.md)
- [Rust](references/rust/rust.md)

Before writing or reviewing any Client boundary—including Flow start, RPC, cleanup, admission, waits, or external Stream writes—read [Error handling](references/core/error-handling.md) and the selected language's **error-handling.md**. This is implementation guidance; do not defer it until a failure needs troubleshooting.

Then load only the references required by the task:

| Task | Core reference | Language reference |
| --- | --- | --- |
| First application or architecture | [Getting started](references/core/getting-started.md) and [Error handling](references/core/error-handling.md) | language entry and **error-handling.md** |
| Flow boundary or state model | [Modeling](references/core/modeling.md) | selected language's **primitives.md** |
| Primitive selection or exact API | [Primitives](references/core/primitives.md) | selected language's **primitives.md** |
| StepOptions, durability, timeout, heartbeat, retry, loads, locks, or failure route | [StepOptions](references/core/step-options.md) | selected language's **advanced-features.md** |
| Design-pattern choice | [Patterns](references/core/patterns.md) | selected language's **patterns.md** |
| Client calls, admission, RPC, cleanup, waits, or external Streams | [Error handling](references/core/error-handling.md) | selected language's **error-handling.md** |
| Integration or failure-path tests | [Testing](references/core/testing.md) | selected language's **testing.md** |
| Failure diagnosis | [Troubleshooting](references/core/troubleshooting.md) and [Error handling](references/core/error-handling.md) | selected language's **error-handling.md** and **gotchas.md** |
| Production inspection or mutation | [Operations](references/core/operations.md) | selected language's **observability.md** |
| Server deployment or component topology | [Operations](references/core/operations.md) | language entry for Client and Worker targets |
| Connector selection, local credentials, or named connections | [Operations](references/core/operations.md) | language entry for runtime support |
| Large state, maps, or projections | [Data handling](references/core/data-handling.md) | selected language's **data-handling.md** |
| Open-Flow compatibility or upgrade | [Versioning](references/core/versioning.md) | selected language's **versioning.md** |
| Cancellation, BlobCache, or other advanced behavior | relevant core topic | selected language's **advanced-features.md** |
| Durable AI agent | [AI agents](references/core/ai-agents.md) | selected language's primitives, data, patterns, and advanced features |

The language directory is the routing unit. Do not load all five languages.

## Model before implementation

For non-trivial work, first state the Flow identity and lifecycle, typed start input and completion output, Steps and transitions, Flow-level durability default, method-level StepOptions, durable state, messages, synchronous RPCs, best-effort Streams, timers, retries, timeouts, recovery, and SubFlow boundaries.

Name every RPC handler and explicit RPC with a concrete action verb. Use complete domain names such as `get_queued_messages` or `move_queued_message_to_prioritized_messages`, not noun-only names, placeholders, or generic names such as `Get`, `Update`, `Manager`, `Data`, or `Handler`. Apply the same preference for complete, precise names to APIs, interfaces, classes, types, methods, functions, fields, variables, and constants. Brevity is not a goal; a name should communicate its operation and subject at the call site or registration boundary.

Use **Execute** for work-oriented transitions and **WaitFor** for durable waiting transitions. This is a modeling convention, not an SDK capability boundary: either phase may query or mutate an external provider when that is necessary to establish or reconcile its transition. Keep every external mutation idempotent or compensatable, including mutations made from `WaitFor`; do not turn `WaitFor` into an unbounded provider-polling loop when a durable Attribute, Channel, Stream, or Timer can express the wait.

Treat each WaitFor, Execute, and RPC invocation as a separate commit boundary. Split a provider action into its own Step when its successful completion deserves an independent checkpoint, retry/timeout policy, failure-recovery route, or audit boundary. For example, an idempotent Kafka or SQS send often merits its own Step so later failures do not resend it. Do not split solely because there is another API call: keep consecutive work in one Step when it shares one meaningful recovery boundary.

For a product mutation that entails multiple actions, cross-service calls, durable waits, retries, reconciliation, or cleanup, prefer starting one domain-named Dex Flow directly at the API boundary. Let that Flow own admission, orchestration, recovery, and completion. Keep the database for durable domain records, invariants, and read projections; do not introduce a database outbox plus dispatcher, polling command queue, or generic event-driven coordinator solely to start or sequence the Flow. A single bounded local operation can remain synchronous, and independently owned external integrations may still require explicit events.

Deduplicate root Flow starts with Dex start identity, not an application-owned database mechanism. Derive a stable Flow ID for the logical operation, derive the start Request ID from the complete logical request, choose the explicit ID reuse policy, and handle the SDK's typed already-started result. Never add a table, row, outbox, lease, lock, cache, or generic admission projection solely to deduplicate or serialize `startFlow`. If the API must confirm durable admission, wait for the admission Step or Flow result and read accepted business state from its owning domain record.

At application boundaries, preserve typed Dex failures until domain policy can distinguish business rejection, a closed-Flow race, a retryable service failure, and a local defect. Reconcile a not-active result from existing authoritative state; inspect the Flow only when an otherwise unknown terminal distinction changes the outcome. Use retained Streams only for best-effort observation, never as authoritative business state.

Prefer the nearest official pattern to an ad hoc coordination loop. Preserve its Flow shape while replacing the domain and integrations. When changing a Go or Python Flow, use `dexcli visualize SOURCE` after the shape is explicit; the visualizer does not currently support Java, TypeScript, or Rust.

## Complete the vertical slice

Application changes should include typed inputs, outputs, and failures; Flow and Step definitions; every persistence schema entry; constructor-injected dependencies; registry wiring; Worker and Client wiring when absent; an application boundary; and a real Dex Server integration test.

Keep stable Flow, Step, Attribute, Channel, Stream, and RPC names compatible with open executions unless the user has an explicit migration. Use unique Flow IDs and convergence polling rather than fixed sleeps.

Before handoff, verify build or type-check, the relevant integration scenario, registration of every durable primitive, retry and timeout recovery, duplicate requests, terminal behavior, heartbeat cadence, Stream best-effort semantics, and compatible Worker/Client registry and payload configuration.
