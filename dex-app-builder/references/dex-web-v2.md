# Dex Web v2 and FDG 2.0

Reference capability baselines: Dex Server `v0.14.0`, Dex CLI `v0.14.0`, and
Dex Go SDK `v0.13.1`. These validate this skill's guidance; they are not an
instruction to upgrade an application. A generated application uses the exact
Server, CLI, and Go SDK versions pinned by its `TEMPLATE_BASELINE` release unless
the user explicitly requests an upgrade. Both Server and CLI embed Web v2,
including permission-based Work Queue, cumulative permission history,
trusted-header enforcement, dynamic definition sources, embedded reverse-proxy
mounts, local Flow starts, and local setup for Connector operations, Trigger
bindings, and configuration UI units.

Released connector modules may require an older Go SDK; at connectors `main` `d975226` every connector required `sdk-go v0.11.3`. Go minimum version selection builds the application with its own `v0.13.1` requirement, so keep the application pin and do not wait for connector re-releases.

Web v2 is Go-only. Validate every Flow with the v2 analyzer and never fall back to v1.

## Run and Work Queue surfaces

Dex Web derives its experience from:

- indexed Attributes for list and search columns;
- `GetDexSummary` for additional read-only list fields;
- `GetDexDisplay` for run detail fields;
- Step groups and explanations for the run timeline;
- waits on Channels/ChannelMaps for actionable human work;
- eligible Action RPCs for operator operations.

## Management UI design

Treat Dex Web v2 as the first management interface, not merely a Flow
inspector. Model one business record as one Run. Use Indexed Attributes for
supported filters, the Summary RPC for additional list fields, the Display RPC
for detail fields and UI slots, and RPC Action metadata for buttons, typed input
forms, current-state conditions, and permissions. Use editable scalar Display
Attributes for simple updates. Work Queue discovers Runs from cumulative Action
permission history, then the opened Run rechecks current Action eligibility.
Timeline, Step graph, execution details, and recovery information cover process
progress and failures.

Design those contracts before proposing a custom management backend or UI. A
custom surface requires a recorded interaction Dex Web v2 cannot provide; the
fact that a product needs administration does not establish such a gap.

In development `local-selector` mode, **Working as** selects one declared Action permission and filters Work Queue candidates. It does not authenticate a user or grant permission.

Production uses `trusted-header` behind an authenticated host or reverse proxy. The boundary strips browser-supplied permission headers, maps authenticated roles to permissions, and injects exactly one **X-Dex-Work-Queue-Permissions** header. Dex Web hides the selector, ignores request-body permissions, and authorizes Search and Actions against that trusted set. Port 8802 must not be reachable around the proxy.

## Start Flow

The v2 Run workspace shows **Start Flow** only in `local-selector` mode and only
when the selected local definition includes a supported typed Start input
schema. Use it for local development and operation-only connector examples. It
is not available in `trusted-header` mode and is not a production ingress
mechanism.

Choose a current Worker target, enter schema-valid JSON, and submit the start.
Dex Web validates the input before encoding it. The Server rejects disabled
starts with `START_FLOW_DISABLED`, unhealthy or unreachable Workers with
`WORKER_UNHEALTHY`, duplicate/conflicting identity, and invalid typed input with
a coded error. Do not work around those errors by removing types or bypassing
the Worker health check. A connector with a real provider Trigger uses that
Trigger instead of Start Flow for its Trigger acceptance path.

Observed with Dex CLI v0.13.8 and Go SDK v0.12.1:

- Dex Web loads local definitions only from
  `dexcli dev --flow-rendering-dir DIRECTORY`, which holds the FDG 2.0 JSON
  files. Without it the catalog is empty. Regenerate the JSON after every Flow
  change.
- Start Flow sends the FDG's Flow and Step type names. The analyzer uses the
  bare Go type name, while the Go SDK registers package-qualified defaults such
  as `orders.OrderFlow`, so the Worker rejects the start. Override
  `GetFlowType` and `GetStepType` with compile-time strings on every Flow and
  Step; the same names let Run-timeline nodes match the graph. They are durable
  identities, so choose them before Flows are open.
- Dex Web invokes `WaitFor` on the start Step, and the Worker rejects that call
  for an execute-only Step (`dex.StepDefaultsNoWaitFor`). Embed
  `dex.StepDefaults` in the start Step and return `dex.SkipWaitImmediately()`
  from its `WaitFor`.
- FDG 2.0 requires `GetDexSummary` and `GetDexDisplay`, both registered as
  RPCs, even when a Flow has little to show (`v2_view_rpc`).
- A start input field of type `map[string]any` cannot drive the form
  (`v2_start_input`).

For a headless check, use the same endpoints as the browser:
`GET /api/v2/catalog` returns `definitionRevision`;
`GET /api/v2/connector-connections` reports each connection's status;
`POST /api/v2/worker-health` probes a Worker address; and `POST /api/v2/start`
accepts `flowType`, `flowId`, `workerTargetAddress`, and raw JSON `input` with
that revision in the `X-Dex-Flow-Definition-Revision` header.

## Connections mode

In loopback **dexcli dev**, `/v2/connections` groups Connector Steps and Trigger bindings by connector ID and static connection name. It shows the exact module version, dependent Flows, Steps, operations, and bindings, plus **Missing**, **Ready**, **Expired**, **Conflict**, or **Unsupported** status. The Step drawer links the same identity to its setup page.

Automatic setup requires an operation-specific factory from an exact official released module, a static `ConnectionName`, and no local module replacement. Different module versions for one connector/name key are a blocking conflict. Generic factories and unsupported dependencies still render the Flow but cannot write credentials.

For connector development only, `dexcli dev` accepts
`--connector-release-override connector-id=artifact-directory`. Use an artifact
built from the same local connector source and display the visible **Local
override** status. Do not treat an override as a published release or commit it
as an application dependency. Never make an unreleased connector look released
by serving its working tree as the declared next version into the default Go
module cache; that copy persists in `GOMODCACHE` and shadows or conflicts with
the real release. Use the override, or a temporary `GOMODCACHE` for any
consumer that must resolve pre-release versions.

Dex Web verifies release metadata and the Studio artifact. A supported Studio bundle runs in an opaque-origin sandbox; otherwise the host renders the manifest form. Neither surface receives stored credential values. OAuth client credentials, PKCE state, and UI sessions are memory-only.

Connections presents authorization first, then nested operation and Trigger
configuration tabs. A Flow's static `ConnectorConfigurationUI` composes ordered
release-owned units. Each binding maps one generated unit port to one declared
RFC 6901 JSON Pointer; the host rejects undeclared paths. Dex Web writes only
non-secret operation configuration to sibling `use-configurations.json`, keyed
by connector, connection, operation, Flow type, and Step type. The application
loads it once through `localconfig`, so a configuration edit requires an
application restart.

Studio Host API 0.2 keeps the iframe at an opaque origin and accepts only
nonce-bound protocol messages. `use.configuration.save` writes the scoped
non-secret object. `connector.frame.resize` reports bounded content height.
The generic `provider.command.execute` broker can execute only a command
declared by that exact connector release: HTTPS destination, credential field,
fixed/request parameters, redirect bound, response-size bound, and backend
capability are host-enforced. The host injects credentials and rejects any
response that reflects a secret. Tokens, app secrets, authorization headers,
connection files, and stored credential values never enter the iframe.

Connection credentials and Trigger matcher configuration are separate records. Changing one binding does not change another Flow that reuses the same connection. Slack Studio writes stable channel and member IDs while displaying names, raw IDs, copy controls, and manual-ID fallback. Provider tokens and app secrets remain host-owned and are never sent to the Studio iframe.

Use `--connector-config-dir DIRECTORY` to isolate a local stack. Dex Web shows
the resolved connection and operation-configuration paths. The plaintext
development credential file must never be committed or uploaded. Restarting
Dex Web preserves stored connection, binding, and use configuration but clears
pending OAuth/PKCE exchanges and UI sessions. Credential replacement is read
for each provider call; non-secret connection, binding, and operation
configuration remains startup-bound in the application.

**POST /api/v2/search** accepts several permissions; a run matches any requested permission, then Flow type and other filters apply with AND. A historical permission match discovers work that is or was available. Dex Web rechecks current Action eligibility when the run opens.

## Source layout

For each Flow, keep all of these in one Go file:

- Step and Flow definitions;
- Attributes and other persistence declarations;
- Action input structs;
- `GetDexSummary`, `GetDexDisplay`, and Action handlers;
- all `dex:*` directives;
- transitions and Dex decisions.

## Directives

Every Step declares exactly:

```go
// dex:group group-id:review group-label:"Review"
// dex:explanation text:"Wait for a manager to approve the request."
```

Every indexed Attribute has one exact directive and `dex.Indexed` declaration:

```go
// dex:indexed-attribute attribute-key:case-status index-key:case-status index-type:keyword value-type:string description:"Current case status"
var CaseStatus = dex.DefineAttribute[string](
    "case-status",
    dex.Indexed(dex.AttributeIndex{Type: dex.IndexKeyword}),
)
```

Use `// dex:field` on summary and display RPCs. Summary fields are not editable and cannot duplicate indexed Attributes. Returned map keys exactly equal declared field keys. A display field may use `ui-slot:title`, `ui-slot:subtitle`, `ui-slot:status`, `ui-slot:recommendation`, or `ui-slot:reason`. The first four are unique within a view; reason may repeat.

Register every Action through `RPCOptions.Action`. `DefineAction` takes the label, one Attribute condition, and exactly one stable permission:

```go
dex.DefineRPC(flow.ApproveRequest, &dex.RPCOptions{
    Action: dex.DefineAction(
        "Approve",
        dex.WhenAttributeMatches(
            caseStatus,
            dex.AttributeMatchEqual(statusAwaitingApproval),
        ),
        dex.ActionRequiresPermission("request.approve"),
    ),
    LockAttributes: []dex.AttributeLock{
        dex.LockAttribute(caseStatus),
        dex.LockAttribute(approvalRequestKey),
    },
})
```

The analyzer reads this typed registration. Do not add `dex:action` or `dex:when` directives; they are rejected. An Action RPC re-checks current state before its durable mutation or Channel effect. Lock only the business state and effect that must commit atomically.

An Action without input uses `dex.None`. Otherwise every exported JSON field in a named same-file input struct has one `dex:input`. User-sourced inputs omit `attribute-key`; attribute-sourced inputs require a matching scalar Attribute.

### QR capture hint

A user-sourced string Action input may add `capture:qr-code` to its `dex:input`
directive. FDG 2.0 emits `capture: "qr-code"`. No other capture value is
supported, and Attribute-sourced or non-string fields fail analysis. Omitting
the hint preserves the ordinary text input.

Dex Web keeps that text input and adds **Scan QR code**. The scanner loads only
after a user opens it, prefers the rear camera, and copies the decoded text into
the field without submitting the Action. Pasting, a keyboard-style scanner, and
manual input remain available. Success, cancellation, errors, Run changes, and
unmounting release the camera tracks.

Camera access requires HTTPS or localhost. An embedding host must allow camera
access in its Permissions Policy. A denied permission, missing camera, or
insecure context leaves manual input available. Scanning does not authenticate
the operator, grant a permission, satisfy an Action condition, validate the
business value, or bypass the RPC. Superverse remains responsible for identity,
role-to-permission mapping, trusted-header injection, and the embedding camera
policy.

## Permission projection

The Go Worker includes the complete Action permission mapping only when a successful WaitFor, Execute, timeout Execute, or RPC invocation writes or deletes an Action condition source. Unrelated writes, failed invocations, and query-only RPCs omit it. Initial Flow and SubFlow state receives its projection directly from the Go SDK, including RPC-only Flows.

The Server overlays those business writes on authoritative Attribute state, evaluates every mapping, sorts and deduplicates newly matching permissions, and atomically adds them to `DexWorkQueuePermissions`. Once matched, a permission remains in that Flow execution's history, carries across Continue-as-New, and remains searchable after completion. Empty mappings and later state changes do not remove history. Application Steps do not need projection-only Attribute locks.

Dex Web follows the same rule for editable fields: only `SetAttributes` calls that modify an Action condition source include the complete mapping. An Action definition is a stable contract for an active Flow. A changed definition is evaluated on a later source write or a new Flow. Removing or renaming a permission does not clear existing history.

Permission history is discovery data, not authorization evidence or proof that an Action remains eligible. Every Action RPC rechecks current business state. Hosted callers authorize the RPC against the trusted permission set.

## Validation

Run:

```bash
dexcli visualize path/to/flow.go \
  --schema-version 2.0 \
  --json \
  --out /tmp/flow-fdg-v2.json
```

Require the JSON graph to report `valid: true`. Treat diagnostics for missing or repeated directives, mismatched keys/types, non-read-only views, invalid typed Action registration, invalid Action inputs, or unsupported editable fields as blocking defects.

Write these JSON files into the persistent `--flow-rendering-dir` of the user-facing `dexcli dev` stack as soon as the first graph renders, and start that stack immediately rather than after verification (see [Stage 3](../SKILL.md#stage-3-design-and-implement-the-flow)). Isolated test stacks render their own copies.

Validate every Flow file. The template's `scripts/check-fdg-v2.sh` visualizes only `internal/process/flow.go` (template `v0.2.1`). With several Flows, such as a parent and its SubFlows, run the analyzer on each Flow source, write every JSON into the `--flow-rendering-dir` directory, and fail when any graph is invalid or reports an unexpected diagnostic.

The template check fails on any diagnostic, including warnings. While the application deliberately tests an uncommitted local connector `replace`, `connector_release_required` on those Connector Steps is the only acceptable diagnostic. Record it as the release blocker, do not weaken the committed check, and require a diagnostic-free run after pinning the release.

## FDG 2.0 analyzer rules

A Flow that compiles, runs, and passes real-Dex tests can still fail `dexcli visualize --schema-version 2.0`. These rules were observed with Dex CLI v0.13.8:

| Code | Severity | Rule |
| --- | --- | --- |
| `hidden_dex_decision` | error | Every `Execute` returns its own Dex decisions. A helper that returns `*dex.StepDecision`, such as `router.enterStage(ctx, stage)`, hides the transition. Helpers may only compute inputs or record state. |
| `connector_factory_step_type` | error | A Connector factory `StepType` is a non-empty compile-time string. A helper that builds `slack.NewPostThreadReplyStep(...)` from a parameter fails, and every `sdkgo.StepRef` to it then reports `unknown_step_target`. |
| `dynamic_type_name` | error | `GetFlowType` and `GetStepType` return a string literal or constant. |
| `v2_view_rpc` | error | The Flow defines `GetDexSummary` and `GetDexDisplay` and registers both as RPCs. |
| `v2_view_rpc_output` | error | Each view returns one `map[string]any` literal whose keys are exactly the declared `dex:field` keys. A map built in a loop "omits declared field". |
| `v2_directive` | error | `value-type` matches the Go type: an unnamed slice Attribute is `array` (`string-array` for `[]string`), not `json`. An optional `dex:input` (`required:false`) is a pointer field such as `*string`. |
| `unused_resource` | warning | Each declared Attribute has at least one direct `Get` or `Set` call with `ctx` inside a Step or RPC method of the Flow file. Access only inside helpers, including passing the handle as an argument, counts as unused. |
| `v2_start_input` | warning | Every start input field can drive a form; `map[string]any` cannot. This also applies to a Flow started only as a SubFlow. |
| `connector_release_required` | warning | A Connector Step resolves to an exact official released module without a local replacement. It is unavoidable while testing a local connector. |

Keep decisions explicit in the method body. A helper computes, and the method decides: `input, err := prepareReview(ctx)`, return the error when it is non-nil, then `return dex.GoTo(ReviewStep{}, input), nil`.
