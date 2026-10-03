# Read-after-write consistency and asynchronous completion

Use this reference before implementing or reviewing sequential Client mutations and reads. Classify the **write API → read API pair**, not Signal alone. Language-level `await`, a completed Future, or a nil error proves only that the selected API's response boundary was reached.

## Three different guarantees

1. **Acceptance:** the backend accepted the request. A successful Signal submission does not itself wait for Interpreter processing.
2. **Read-after-write:** after the write returns successfully, a subsequent read of the authoritative Flow state reflects its direct effects or a later state. The read may block until the Interpreter catches up. Strong does not mean zero latency.
3. **Business completion:** Steps, provider operations, cleanup, and other work triggered by the write have finished. A fresh state read does not automatically establish this.

Temporal orders an accepted Signal before a subsequent Workflow Query. This is not a promise that arbitrary blocking Signal work finishes first. Dex's ordinary RPC Signal receiver applies Attribute writes and Channel publications/deletions without a durable wait before those mutations. A later typed read-only RPC prepares its snapshot with a Workflow Query. For valid direct mutations, this pair provides strong read-after-write on Temporal. Do not add callback waits or convergence polling just because the write uses a Signal.

This guarantee requires a successful write, a read initiated afterward, the same logical Flow and appropriate state selections, and no application failure preventing the effect from being applied. An AttributeMap instance must be loaded by the read RPC. Channel pending-message reads must load the queue; another consumer can remove a just-published message. Concurrent writes can supersede the value. Strong read-after-write does not add transaction isolation, make a multi-RPC sequence atomic, or guarantee a particular value survives competing mutations.

## Write/read matrix

| Write and delivery path | Subsequent read or confirmation | Guarantee and limit |
| --- | --- | --- |
| Non-transactional `InvokeRPC` with direct Attribute/AttributeMap writes; Query → Worker → Execute-RPC Signal | Typed read-only RPC over the same retained Attributes, with required map loads | **Strong on Temporal** for successfully applied direct state. The first successful read must include the write or a later state. |
| RPC Channel publish/delete via the same Signal | Typed queue snapshot RPC with Channel/ChannelMap loads | **Strong on Temporal** for direct queue state. A consumed/deleted message is not expected to remain pending. Non-transactional deletion of a missing ID can be a no-op while other effects apply. |
| Transactional/locked RPC, or Server-forced synchronous Update | Typed read-only RPC over direct state | Update waits for its handler and commit path. **Strong on Temporal** for direct state; does not wait for triggered Steps or external projections. Requires an active Flow. |
| `UpdateFlowConfig` → update-config Signal | Raw Server/CLI Flow state Query; Worker-target changes can also be confirmed by a typed read RPC reaching the new Worker | **Strong Temporal Query readback** once processing can run. The write returns on acceptance; a delayed-start Flow may make the read wait until startup. Applies only supplied fields and does not recall already-dispatched work. The public SDK does not expose a generic configuration-read API. |
| `SkipTimer` → Query validation + skip-timer Signal | Current Timer/Step state Query; named Step completion or business snapshot for the result | Query can observe the direct Timer change. **Subsequent Execute/business completion is asynchronous.** The Timer may fire between validation and Signal handling; acceptance alone is not proof of execution. |
| `StopFlow` CANCEL/default or FAIL → stop Signal | `WaitForFlow` and explicit terminal status | **Asynchronous terminal completion.** Signal handling requests cooperative cleanup; terminalization and Attribute Store draining can finish later or fail. CANCEL, FAIL and TERMINATE are different outcomes. |
| `StopFlow` TERMINATE → backend termination, not Signal | Engine terminal status | Ends the backend execution without cooperative cleanup. It does not prove provider compensation or projection completion. |
| `TriggerContinueAsNew` → trigger Signal | Diagnostic current-run summary/history; business RPCs continue to use stable FlowID | **Asynchronous rollover.** The signal sets the trigger; draining, snapshotting and creating the successor still take work. RunID must not become a business revision/fence. |
| Any indexed Attribute write | `SearchFlows`, CLI search, or Web work discovery | **Eventual visibility.** Workflow Query consistency does not make the visibility index synchronous. Search misses are not proof the write failed. |
| Any Attribute Store-enabled write | External Attribute Store query | **Asynchronous latest-state projection.** Valid direct Flow state can be readable before the projection finishes. Projection failures do not roll back Flow state; retry exhaustion can prevent convergence. |
| RPC Step movements, cancellation or close decisions | Named Step wait, Attribute-match/business condition, or terminal result | **Asynchronous business completion.** Cancellation can yield before later Step movements are queued; a direct Attribute snapshot is not a scheduling/completion barrier. |
| Raw `SetAttributes` / `PublishToChannel` → Execute-RPC Signal | Raw Attribute/Channel Query or typed application snapshot | Same direct-state Temporal boundary. These Server APIs are not public SDK state APIs; applications should use typed RPCs. |
| Raw `DeleteChannelMessage` | Pending Channel Query | Temporal uses synchronous Update; Cadence uses Query validation followed by Signal. No uniform cross-backend strong guarantee. Applications use typed RPC deletion. |
| Internal SubFlow completion Signal | Parent's SubFlow condition, parent Step completion or business state | Delivery acknowledgement is not proof the parent consumed the result or completed subsequent work. This is an internal signal, not a Client completion API. |

`StartFlow` and TimeTravel/Reset are not Signal writes. Their returned run identifies an accepted/new execution; use a named admission Step or Flow result if the API must establish business acceptance or completion. A Stream message is best-effort observation, not an authoritative receipt for any of the operations above.

## Backend and lifecycle boundaries

Dex's Temporal Query adapter uses `QueryWorkflow`. Its Cadence Query adapter uses the ordinary `QueryWorkflow` path without selecting strong consistency. A separate Cadence strong-query helper does not upgrade every public Query. Do not copy Temporal's direct-state guarantee into Cadence guidance; use bounded authoritative polling when an application on Cadence needs confirmed effects. Cadence does not support the Temporal synchronous Update path.

A delayed-start Flow can accept a Signal before the Interpreter initializes its receivers. A strong Query can wait for that processing instead of returning stale state. Set a read deadline that allows the configured start delay; a timeout proves only that confirmation was not obtained. Interpreter unavailability can similarly block or fail the read. Do not weaken a strong path into polling to hide that failure.

A Worker-target update changes future routing; dispatched calls may still use the previous Worker. Validate configuration readback separately from the new Worker's registration, reachability and typed RPC response. A stale Pod IP or unavailable Worker is a routing/availability failure, not evidence of eventual Attribute consistency. Prefer a stable reachable Worker target when the deployment supports one.

Continue-As-New keeps business identity stable. Client RPCs resolve the current run and have bounded transition retry paths. Do not claim an atomic snapshot across concurrent rollover or a retained historical run and its successor. A query-only RPC can read retained terminal state; locks, transactions, returned effects and Server-forced Update require an active execution. Retention expiry must remain an explicit missing/unavailable result.

## Confirmation and retries

Use a single typed authoritative read after a successful direct Temporal RPC write. For subsequent business work, select the existing named Step completion, Attribute match, business RPC state, or terminal-result API that proves the requested condition. Bound the wait and inspect terminal status; a completed Flow proves success only if its completion contract guarantees that condition.

Never use a fixed sleep as confirmation or blindly resend accepted requests. Do not attach a callback to every Signal operation. Add an application acknowledgement only when its business contract needs a stronger completion fact that existing public observation cannot express. Do not invent an operation receipt or SDK config-wait API.

If transport failure or timeout makes an RPC or Signal mutation's acceptance unknown, reconcile authoritative state before retrying an effect whose safe replay is not established. StartFlow follows the [start-first replay rule](error-handling.md#start-first-reconcile-only-after-an-error); a stable start identity and matching start options can permit bounded replay without a mandatory read. Preserve the request identity where the installed API supports it, and distinguish start deduplication from RPC or Signal idempotency. Config updates, timer skips and rollover triggers do not acquire exactly-once semantics merely because the client retries. An accepted command can still encounter closure or a processing failure; do not promise unconditional eventual success.

## Verification

For strong RPC read-after-write, test a real Server/Interpreter/Worker with repeated sequential writes, then invoke the typed read RPC immediately. Assert ordinary Attributes, loaded AttributeMap instances and non-consumed pending queues on the **first** successful read. No sleeps or convergence polling are allowed between that write and read. Cover Signal, transactional, locked and Server-forced Update paths.

Establish lifecycle transitions separately: trigger rollover, confirm the diagnostic successor, then read business state; close and test retained query-only reads. For delayed config updates, submit while startup is delayed, immediately query configuration, and independently read through the new Worker. The query may block; do not assert that every immediate query must return an old value.

Use a controlled gate on a subsequent business Step or projection writer to prove direct state is readable while later work remains unfinished. Release the gate and confirm completion with a bounded condition. For a paused Interpreter, distinguish accepted Signal submission from a Query deadline, then resume and confirm state. Cadence tests assert bounded convergence rather than borrowing Temporal's first-read assertion.

## Source authority

The following links explain the existing semantics at the bundle's immutable baselines. Preserve installed project versions and inspect version-matched source before writing exact API calls. This reference introduces no new API.

- [Server Signal submissions and RPC routing](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/api/service.go)
- [Signal receivers and direct effect application](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/interpreter/signalReceiver.go)
- [Attribute writes](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/interpreter/persistence.go)
- [Query snapshot preparation](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/interpreter/queryHandler.go)
- [Temporal adapter](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/client/temporal/client.go) and [Cadence adapter](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/client/cadence/client.go)
- [Attribute Store scheduling](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/interpreter/attributeSynchronizer.go)
- [SubFlow delivery](https://github.com/superdurable/dex/blob/server/v1.3.0/server/service/interpreter/activityImpl.go)
- [Go Client](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-go/dex/client.go), [Python Client](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-python/dex/client.py), [Python AsyncClient](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-python/dex/async_client.py), [Java Client](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-java/src/main/java/io/superdurable/dex/Client.java), [TypeScript Client](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-typescript/src/client.ts), [Rust Client](https://github.com/superdurable/dex/blob/sdk-go/v1.5.0/sdk-rust/crates/dex-sdk/src/client.rs)
- [CLI operations and success fields](https://github.com/superdurable/dex/blob/cli-v1.5.0/cli/internal/command/flow_client_operations.go)
- [Web action RPC routing](https://github.com/superdurable/dex/blob/server/v1.3.0/web/api/v2.go)

Temporal describes the [Signal/Query ordering boundary](https://community.temporal.io/t/querying-workflow-after-signal/11375). Validate the Dex handler itself rather than treating that general ordering guarantee as completion of downstream business work.
