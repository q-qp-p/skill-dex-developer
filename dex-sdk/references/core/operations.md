# Production operations

Before reporting a mutation as effective or complete, identify its [write/read consistency and completion boundary](read-after-write.md). CLI `updated: true` and `skipped: true` acknowledge request acceptance. A subsequent Temporal Flow-state Query may block until the accepted signal is processed; search and projections can still lag.

Use this guide for Dex Server deployment, production inspection, and authorized recovery. Read [testing.md](testing.md) for verification scenarios and [troubleshooting.md](troubleshooting.md) for diagnostic routing.

## Diagnostic order

1. Capture the exact Flow ID, run ID, Flow type, SDK version, and Dex Server address.
2. Check Worker application logs for handler and connectivity errors.
3. Inspect the Flow in Dex Web.
4. Run a bounded read-only inspection:

```bash
dexcli flow summary <flow-id> --timeout 30s --no-hydrate
dexcli flow state <flow-id> --timeout 30s --no-hydrate
dexcli flow history <flow-id> --page-size 80 --timeout 30s --no-hydrate
```

5. Compare the active Step, Attributes, Channel waits, Timers, and recent semantic events with the intended graph.
6. Reproduce with the smallest matching integration test.
7. Fix application code or configuration, then decide whether existing executions need recovery.

## Inspect pending Channel messages

Invoke the application's typed snapshot RPC to obtain a Channel's current FIFO values and server-assigned IDs. An ID disappears once its message is consumed or deleted. If delete or transactional move returns Channel-message-not-found, treat the local view as stale, invoke the snapshot RPC again, and let the user choose again.

Only pending Channel state is mutable through these operations. Editing a message means deleting it successfully and publishing a replacement with a new ID; it does not rewrite Flow history or application conversation Attributes.

Use a transactional RPC when deletion must commit atomically with a replacement publication or other Flow-state writes. Without transactional execution, a missing deletion may be a no-op while other effects commit; reconcile from a fresh list.

For an application queue UI, prefer one application snapshot RPC that returns durable conversation state, description, and loaded pending queues together. Refresh that snapshot after mutations and live events, on focus or reconnect, and periodically at low frequency. Keep optimistic items only as a short bridge; the snapshot is canonical.

Use **dexcli flow search**, **summary**, **state**, and **history** for narrower JSON output. Use **--no-hydrate** when payload contents are unnecessary or sensitive.

## Inspect raw Temporal payloads

With Dex CLI v1.4.2 or later, run the local protobuf Codec Server to inspect Dex's
internal Temporal payloads in Temporal Cloud or a local Temporal Web UI:

```bash
dexcli codec-server
```

Configure **http://127.0.0.1:8804** as the Codec Server URL in Temporal Web UI.
The browser connects directly to this process. Temporal Cloud and HTTP/HTTPS
origins on localhost or loopback IP addresses are accepted on any port, so an
automatically selected local UI port needs no extra server arguments. External
and malformed origins are rejected. The codec server binds only to loopback;
keep it local and stop it with Ctrl+C when finished. Leave access-token and
cross-origin credential forwarding disabled.

The codec converts known Dex binary protobuf payloads to ProtoJSON. Unknown
message types and other encodings pass through unchanged. The same tooling
applies to all five SDK languages. See the released
[CLI codec server usage](https://github.com/superdurable/dex/blob/cli-v1.5.0/cli/README.md#view-temporal-protobuf-payloads).

## Indexed Attribute capacity

The default local **dexcli dev** stack starts Temporal with SQLite. SQLite allocates a fixed number of custom Search Attribute slots per namespace and type. In a fresh local database, Dex uses three of those slots for system indexes, leaving this initial capacity for application Indexed Attributes:

| Dex index type | SQLite slots | Dex system indexes | Application slots initially left |
| --- | ---: | --- | ---: |
| **KEYWORD** | 10 | **FlowType**, **DexParentFlowID** | 8 |
| **KEYWORD_ARRAY** | 3 | **ActiveStepTypes** | 2 |
| **FULL_TEXT** | 3 | None | 3 |
| **BOOL**, **DATETIME**, **DOUBLE**, **INT** | 3 each | None | 3 each |

Index keys are shared across Flow types. Reusing one key with the same type does not consume another slot. Previously registered application keys remain in a persisted local database and reduce the current remainder. Worker startup fails while synchronizing indexes if a new key exceeds the remaining capacity.

Plan one namespace-wide pool before implementation. All application index keys must be explicit generic typed slots, reusable by every Flow type: **keyword1**, **keyword2**, **keywordList1**, **keywordList2**, **text1**, **text2**, **int1**, **int2**, **bool1**, **double1**, **datetime1**, and later numbers as needed within the available capacity. **keywordListN** uses **KEYWORD_ARRAY** and **textN** uses **FULL_TEXT**. Keep one type per physical key throughout the namespace; allocate different slots for different indexed fields within one Flow. Keep business meaning in Attribute names and document each Flow type's slot mapping. Application run searches must constrain **FlowType** and include **ExecutionStatus != "ContinuedAsNew"**, matching Dex Web's exclusion of earlier Continue-as-New runs. Parenthesize additional caller filters before combining them with these predicates. Raw SDK searches require these application predicates explicitly; include earlier runs only for intentional execution-chain inspection. Dex system indexes keep their reserved names. Do not index sensitive data or PII.

Changing a persisted local store's index key, type, or enabled state does not remove the old Search Attribute. Use a fresh local store and new ports while validating the new schema, or migrate the store deliberately.

Treat this as a local development constraint, not an application schema limit. Do not remove production query fields merely to fit local SQLite. To test more keys locally, point **dexcli dev** at an external Temporal deployment with enough visibility capacity using **--external-temporal-address**.

Production capacity is determined by its Temporal visibility backend. Elasticsearch-backed deployments do not have SQLite's fixed per-type slot pool, although Elasticsearch mapping limits can still apply. Temporal Cloud and self-hosted SQL visibility stores have their own limits. Verify the target environment against [Temporal's current Search Attribute limits](https://docs.temporal.io/search-attribute#custom-search-attribute-limits).

## FDG 2.0 management metadata

Dex Web can inspect Runs created by every SDK, but the current FDG 2.0
management-interface metadata is generated only by the Go analyzer. This
includes Indexed Attribute presentation, Summary and Display RPC fields, Action
forms and permissions, groups and explanations, and Action input capture hints.
Do not claim that Java, Python, TypeScript, or Rust source can publish this
metadata today. Those SDKs can operate Flows and use the supported Client and
CLI surfaces, while a Dex Web v2 management experience that depends on this
metadata currently requires a Go Flow definition.

## Local Connector credentials

Dex Web v2 can configure exact released official Connector modules for Go Flows during loopback **dexcli dev**. The Flow must use operation-specific factories, a static connection name, and static names for any Trigger bindings. Generic factories, local replacements, unreleased module versions, or version conflicts remain visible but are not configurable.

The default plaintext development store is `~/.dex/connectors/connections.json`. Pass **--connector-config-dir** to choose an isolated directory. Use the absolute path displayed in Connections mode when starting the application:

```bash
DEX_CONNECTOR_CONFIG_FILE="$HOME/.dex/connectors/connections.json" <your-app-command>
```

The file survives Dex Web and application restarts. Restarting Dex Web clears pending OAuth/PKCE exchanges, OAuth client secrets, and Studio UI sessions because those remain in memory. Stored short-lived credentials remain until expiry or explicit local deletion. Deletion does not revoke the provider grant.

Only the Go Connector SDK currently provides the local file loader. Never put the JSON record, access token, API key, or secret-bearing generated value into Flow state, logs, browser messages, or application responses.

Connection credentials and Trigger binding matchers are separate. One connection may serve several Flows without sharing their filters. Trigger delivery is at least once: use deterministic Flow IDs for starts. Application RPCs own their redelivery policy, bounded deduplication state when needed, and business locks.

## Native hosted project configuration

Server and CLI v1.3.0 embed native project configuration. Project Connectors can
render an exact admitted AppManifest before an application Release or Flow
definition exists. Flow operations still require the actual validated definition.
Project, environment, and Preview Session scope are immutable server startup
configuration; browser parameters cannot override them. An authenticated private
proxy supplies actor, mount, public origin, permissions, and CSRF context and
blocks internal AppManifest/validation endpoints from browser routing.

Dex and Go applications use the released Connector SDK's `sdkgo/projectconfig`
storage contract. Ordinary snapshots contain logical connection IDs; credentials
remain separately versioned private objects. Refresh/replacement applies on the
next provider call, while ordinary configuration requires validation and a new
deployment snapshot. OAuth dispatch is admitted before the provider call; an
uncertain response or restart must be reconciled rather than blindly dispatched
again. Never persist provider secrets in application Flow state or return them
to the browser. Other SDK languages need an explicit supported runtime boundary;
do not invent a language-specific project configuration loader.

The S3 client uses the default AWS credential chain when both static key fields
are omitted. Configure an explicit region and the workload's intended role;
reject partially supplied static credentials. Verify real workload role access,
project-prefix isolation, versioned conditional writes, KMS encryption, and denied
cross-project access. Host-profile success does not prove workload-role acceptance.

See the pinned [native project protocol](https://github.com/superdurable/dex/blob/server/v1.3.0/web/PROJECT_CONFIGURATION.md)
and [Web boundary](https://github.com/superdurable/dex/blob/server/v1.3.0/web/README.md).

## Deploy Dex Server components

The `dex-server` image starts Web, API, and Interpreter in one OS process by default. It serves FlowService gRPC on port 8801 and Dex Web HTTP on port 8802.

Before deploying a Worker, run `dexcli version check` against its target Server. Each Server and SDK release declares an inclusive protocol interval. Worker startup selects the highest common protocol before synchronizing Attribute indexes and binding WorkerService. Artifact versions are diagnostic only.

When upgrading from a Server that predates `GetServerInfo`, upgrade the Server before any SDK. New Workers reject a missing information RPC. After that first upgrade, either side may be newer while the intervals overlap.

A breaking Server release raises its minimum protocol. Stop old Workers and their traffic before upgrading the Server, upgrade every SDK in the maintenance window, then restart traffic. Isolated blue-green environments may run disjoint intervals, but they must not communicate. Running Workers do not renegotiate after a Server upgrade.

Use `dex-server start --services <selection>` to scale components independently. The selection must be a nonempty comma-separated combination of `web`, `api`, and `interpreter`:

```bash
dex-server start --services web
dex-server start --services api
dex-server start --services interpreter
dex-server start --services web,api
```

Web-only does not initialize storage, Temporal, Cadence, the index synchronizer, or the Interpreter. Configure its remote API target in YAML:

```yaml
web:
  bindAddress: 0.0.0.0
  port: 8802
  flowServiceTarget: dex-api:8801
  flowRenderingDirectory: ""
```

When `web.flowServiceTarget` is empty, Web connects to `localhost:<api.port>`. The connection uses plaintext gRPC and `api.grpcMaxMessageBytes`. Put TLS, authentication, and network policy at the deployment boundary.

`/healthz` reports Web process liveness, not upstream API readiness. Web starts while FlowService is unavailable; `/api/*` returns the existing mapped gRPC error until the API recovers.

For Interpreter-only deployments, point `interpreter.interpreterActivityConfig.internalServiceTarget` at the API service. Scale Web, API, and Interpreter replicas according to HTTP traffic, FlowService traffic, and execution load respectively.

```yaml
interpreter:
  interpreterActivityConfig:
    internalServiceTarget: dex-api:8801
```

API and Interpreter replicas must use the same intended Temporal namespace or Cadence domain and compatible production storage configuration.

### Temporal Cloud attribute indexes

Temporal Cloud API-key clients cannot call the Operator Service methods that
discover and create Search Attributes. Provision the following Dex system
indexes through the Temporal Cloud control plane before starting Dex:

- `FlowType`: Keyword
- `DexParentFlowID`: Keyword
- `ActiveStepTypes`: KeywordList

Provision every indexed application Attribute before its Worker starts. Then
configure every Dex Server process that uses the namespace:

```yaml
interpreter:
  attributeIndexesManagedExternally: true
```

This mode validates application declarations but deliberately does not discover,
create, or verify indexes. A missing or incorrectly typed index therefore fails
when Temporal first uses it; treat Cloud provisioning and Worker startup as one
deployment contract.

When multiple Server processes use Streams, configure a shared Redis 7+ backend. The in-memory backend is only for one process:

```yaml
streamStore:
  backend: redis
  redisURL: redis://redis:6379/0
```

Configure Redis with `noeviction` so capacity pressure becomes a visible Stream write failure. If Blob Store is enabled, use the same durable object-store configuration across API and Interpreter replicas; do not rely on pod-local blob directories.

Blob Store keeps payloads through 100 bytes inline by default and offloads from 101 bytes. Keep the storage ID short because it appears in every durable reference; prefer a name such as `p1` over `production1`. A reference such as `p1|c/ab3de7kp2x` uses the lowercase Base36 day offset from September 1, 2026 UTC and a deterministic lowercase Base36 object ID. It omits the Flow ID and encoding. The Server derives a physical path such as `260913$coding-session--c08256c4/ab3de7kp2x` from trusted context. ASCII letters, digits, hyphens, and underscores remain readable in the Flow ID segment; other UTF-8 bytes use uppercase percent escaping. Run IDs and Step execution IDs in input-snapshot paths remain Base64URL encoded. Object Blobs store the complete EncodedObject. `objectIdLength` defaults to 10; zero selects that default, negative values are invalid, and any positive length is accepted. Every Server sharing a namespace must use the same immutable value. Use 12 or 16 for unusually high per-Flow daily object counts. Values above 50 only add leading zero padding because the ID derives from SHA-256. Readers accept any nonempty lowercase Base36 object ID. Application code must treat references as opaque.

Successful ASYNC local Step input snapshots are disabled by default. Enable `blobStore.asyncStepInputSnapshotsEnabled` only when semantic history must retain the exact inputs sent to those methods. The setting is independent of the payload offload threshold and does not affect Flow execution, retry, or recovery. When disabled, no snapshot objects are written and the corresponding semantic-history inputs are unavailable. SYNC and regular-fallback inputs remain available from backend history.

## Safe recovery

Diagnosis is read-only by default. Stop, time travel, publish, invoke, skip a Timer, or mutate Attributes only when the user asks to change the Flow.

Before a mutation:

- resolve the current exact run
- explain the expected state change
- use an application Flow RPC or an explicit dexcli operation
- satisfy any explicit confirmation flag
- re-inspect the Flow afterward

Time travel is appropriate after deploying a code fix when replaying from a safe Step boundary will not duplicate an unprotected side effect. Preserve the original business resource, Flow ID, and operation identity; capture the exact diagnostic run and Step method before mutation. Reconcile provider objects and previously accepted writes first. Do not replace the account or resource merely to avoid its failed history. If a safe boundary cannot be established, design an explicit recovery or compensation Step instead.

A time-travel reset cannot invent a missing method boundary or rewrite the original Start options. A failure before the first Execute may have no Execute reset point. Do not silently replace it with a fresh Flow. If a corrected start is needed, obtain authorization for that recovery, prove the old execution is closed, reconcile effects, and preserve the intended Flow ID and logical request identity under the exact reuse policy. Closed-execution reuse is not cross-run request deduplication; application admission must protect external effects. Where a recorded WaitFor boundary is appropriate, select that method explicitly and decide whether replaying later writes is safe before choosing `--skip-writes-reapply`.

When a durable-history bug has already failed a Flow, validate the fix against that
same history when safe:

1. Deploy or restart the Worker with the corrected code.
2. Time travel the failed Flow to the last safe execution before the failure.
3. Let Dex replay and continue with the corrected Worker.
4. Re-inspect the new run and verify the formerly failing path and durable state.

This is stronger than testing only a new Flow because it exercises recovery from the
actual recorded history. Do not cross an external side effect unless it is idempotent,
compensated, or explicitly safe to repeat.

Sources:

- Dex CLI: https://docs.superdurable.io/references/cli
- Application operations: https://docs.superdurable.io/production/application-operations
- Versioning: https://docs.superdurable.io/production/application-operations#versioning-flow-code
