# Versioning Go applications

## Check first

```bash
go list -m github.com/superdurable/dex/sdk-go
go list -m -json github.com/superdurable/dex/sdk-go
```

The selected SDK source is authoritative. Baseline snippets are evidence only for the pinned Dex commit.

## Server protocol compatibility

The Go Worker obtains its diagnostic artifact version from Go build information. On startup it calls `GetServerInfo`, negotiates the highest common protocol, synchronizes Attribute indexes, and then binds WorkerService. A missing RPC, invalid interval, or disjoint interval fails startup before the listener opens. Upgrade a legacy Server first; stop running Workers before a breaking Server upgrade because they do not renegotiate.

## Default Flow and Step type names

Use the SDK's default package-qualified Go type names. Embed `dex.FlowDefaults` and the appropriate Step defaults; do not add custom `GetFlowType` or `GetStepType` implementations for new or not-yet-production definitions, display labels, naming style, or speculative future refactors.

The only exception is an unavoidable Go type or package rename for a Flow or Step already deployed to production, where its previously registered durable identity must remain unchanged. In that case, override only the affected method and return the exact existing production type string as a literal or constant. Identify that persisted string from the deployed registration or real executions before editing. Do not substitute the new Go name or change the persisted type identity as part of the rename. Preserve an existing production override when it already owns that identity.

Dex Web or FDG metadata mismatch is not a reason to override every type. Compare generated metadata with the SDK's registered defaults and diagnose the analyzer/SDK version or metadata issue. When the production-rename exception applies, verify an old execution resumes on the renamed Worker before rollout.

## Open-Flow compatibility

An open Flow can resume on new Worker code. Preserve Flow type, reachable Step type strings, registered schemas, and decodable payloads. Do not rename a Step as a refactor. Add a new Flow/Step type for incompatible behavior and route new starts there.

Additive fields with defaults are usually safer. Removing registered Steps, changing state types, repurposing enum values, or changing retry/terminal invariants is risky.

## Rollout

Deploy a Worker able to serve old and new runs, then move traffic deliberately. Updating a process does not replace durable execution state.

[Pinned runnable source](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/primitives/flow/controller.go)
<!-- dex-source: examples/go/primitives/flow/controller.go -->
```go
func rerouteActiveFlow(ctx context.Context, client *sdk.Client, flowID string) error {
	return client.UpdateFlowConfig(ctx, flowID, sdk.FlowConfig{
		WorkerTarget: &sdk.WorkerTarget{Address: "worker-canary:8803"},
	})
}
```

Choose ID reuse and already-started behavior as product semantics. Test active and closed prior runs. Before rollout, start representative Flows on old code, stop at durable boundaries, replace the Worker, and complete them on new code. Include maps, Channels, Timer, RPC, retry, and timeout handler.
