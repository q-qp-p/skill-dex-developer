# Dex Web v2 and FDG 2.0

Baselines: Dex Server `v0.13.2`, Dex CLI `v0.13.8`, and Dex Go SDK `v0.13.1`. Both Server and CLI embed Web v2, including permission-based Work Queue, cumulative permission history, trusted-header enforcement, dynamic definition sources, embedded reverse-proxy mounts, local Flow starts, and local setup for Connector operations, Trigger bindings, and configuration UI units.

Web v2 is Go-only. Validate every Flow with the v2 analyzer and never fall back to v1.

## Run and Work Queue surfaces

Dex Web derives its experience from:

- indexed Attributes for list and search columns;
- `GetDexSummary` for additional read-only list fields;
- `GetDexDisplay` for run detail fields;
- Step groups and explanations for the run timeline;
- waits on Channels/ChannelMaps for actionable human work;
- eligible Action RPCs for operator operations.

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

## Connections mode

In loopback **dexcli dev**, `/v2/connections` groups Connector Steps and Trigger bindings by connector ID and static connection name. It shows the exact module version, dependent Flows, Steps, operations, and bindings, plus **Missing**, **Ready**, **Expired**, **Conflict**, or **Unsupported** status. The Step drawer links the same identity to its setup page.

Automatic setup requires an operation-specific factory from an exact official released module, a static `ConnectionName`, and no local module replacement. Different module versions for one connector/name key are a blocking conflict. Generic factories and unsupported dependencies still render the Flow but cannot write credentials.

For connector development only, `dexcli dev` accepts
`--connector-release-override connector-id=artifact-directory`. Use an artifact
built from the same local connector source and display the visible **Local
override** status. Do not treat an override as a published release or commit it
as an application dependency.

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
