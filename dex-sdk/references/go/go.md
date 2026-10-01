# Go handbook

The SDK API reference uses the [released v1.2.1 baseline](../core/bundle-baselines.md); the source examples' older dependency pins below remain factual and do not define the current error API.

Use this page first for a Go application. It describes the application boundary and points to focused pages; always check the version selected by `go.mod` and `go.sum`.

## Version and source authority

The [baseline module](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/go.mod) uses `github.com/superdurable/dex/sdk-go v0.13.0`. Before editing an existing project, run `go list -m github.com/superdurable/dex/sdk-go` and inspect that SDK version. If it differs from the baseline, installed source wins. Identify the inspected module-cache path, vendored path, or immutable tag/commit before presenting exact syntax. If no version-matched source is available, give only the version-independent Flow model and request that source; do not adapt baseline snippets speculatively. Pinned sources show known-good shapes, not a promise that every version has the same surface.

## Project shape and local run

Keep Flow and Step definitions in application packages, compose them in one registry package, and create one shared Registry and BlobCache for Client and Worker. Inject business services into Flow constructors. The official example layout is `products/`, `patterns/`, `primitives/`, `registry/`, `shared/`, and `cmd/server/`.

```bash
dexcli dev
cd examples/go
make bins
./dex-samples
```

Defaults use Dex at `localhost:8801`, a Worker listener at `127.0.0.1:8803`, and HTTP at `127.0.0.1:8080`. `DEX_WORKER_TARGET` is the address advertised to Dex and can differ from the bind address.

## Local Connector configuration

Official Go connectors can load the Dex Web development store with `localconfig.LoadFromEnvironment`. Create each generated connection with `NewLocalConnection(store, "connection-name")`, and set the same static `ConnectionName` on every operation-specific factory config. Start the application with **DEX_CONNECTOR_CONFIG_FILE** set to the absolute path shown by Dex Web.

Configuration is captured when the store loads. Credentials are reread for each provider call, so reauthorization does not require a restart; configuration changes do. Keep generated secret values outside Flow state and logs.

Connector Step branch targets receive only the current generated result alias. Query aliases resolve to `sdkgo.QueryResult[OUT]`; Mutation aliases resolve to `sdkgo.MutationResult[OUT]`. `MapToOperationInput` is a pure mapping from the current application Step input into provider input; it has no error result, and the application input is not present in the operation result. Persist business context with an application Step and Attribute before the Connector call, then reload it in success, failure, RPC, and recovery Steps. Use `Annotations` for graph group and explanation metadata; do not use it for visual styling.

`ResultAttribute` is optional for every Query and Mutation. Omit it when only the branch target needs the operation result. Configure and register the precisely typed Attribute when an RPC, display, audit, recovery operator, or another path must read the raw result outside the transition chain.

Provider-neutral Triggers run outside Steps. Give each generated Trigger factory a static binding name, then pass an application-owned target. `NewDexFlowTriggerTarget` takes the typed Flow, a `TriggerFilter`, a stable `FlowIDResolver`, and a `FlowInputMapper`. `NewDexRPCTriggerTarget` takes the application's typed RPC, a filter, the same identity resolver, and an `RPCInputMapper`; no string RPC name is configured.

The filter runs before identity resolution, input mapping, or any Dex call. Return false to consume an event that does not satisfy the application's channel, sender, message, tenant, authorization, routing-field, or other domain rule. Filter, resolver, and mapper callbacks are deterministic, side-effect-free pure functions without error results. A blank or invalid resolved Flow ID is an application defect. Provider binding matchers reduce traffic but do not replace this application admission boundary.

For RPC delivery, register the application's bound method with application-owned `dex.RPCOptions`, then pass that method directly to `NewDexRPCTriggerTarget`. The application decides whether stable provider event IDs need deduplication, stores only bounded domain state, and locks only the business state or effect that must commit atomically.

Use the released [Slack example](https://github.com/superdurable/dex-connectors-library/tree/connectors/slack/v0.11.0/connectors/slack/examples/thread-approval) and [Gmail example](https://github.com/superdurable/dex-connectors-library/tree/connectors/google/gmail/v0.13.0/connectors/google/gmail/examples/thread-reply) as exact integration references. Their modules pin the exact Connector SDK releases they support.

## Hosted configuration and recovery boundary

Use the [Core native project configuration contract](../core/operations.md#native-hosted-project-configuration)
for Server v1.3.0. Keep project scope and credentials behind the supported runtime
boundary; a browser, Flow input, or ordinary Attribute cannot select secret
storage. The Go Connector SDK has the released project configuration package;
that capability does not create equivalent APIs in every Dex SDK language.
For recovery after a Worker fix, preserve the original resource and Flow ID,
reconcile external effects, and use an explicitly authorized, recorded Step
boundary as described in [safe recovery](../core/operations.md#safe-recovery).

## Dex Web v2 management metadata

The current FDG 2.0 management-interface analyzer reads Go source. Go Flow
definitions can publish Indexed Attribute presentation, Summary and Display RPC
fields, Action metadata, typed Action forms, conditions, permissions, groups,
explanations, and user-string `capture:qr-code` hints. Validate that metadata
with the v2 analyzer. This source-analysis capability is not currently available
for Java, Python, TypeScript, or Rust Flow definitions.

## Minimal Flow

Declare schema at package scope, embed defaults, register Step types, and return a decision from every Execute method. Keep SDK-derived Flow and Step type names; do not implement `GetFlowType` or `GetStepType` except for the [required production-rename case](versioning.md#default-flow-and-step-type-names).

[Pinned runnable source](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/primitives/flow/workflow.go)
<!-- dex-source: examples/go/primitives/flow/workflow.go -->
```go
var (
	Status = dex.DefineAttribute[string]("status")
	Notify = dex.DefineChannel[dex.None]("notify")
)

type ExampleFlow struct {
	dex.FlowDefaults
}

func NewExampleFlow() *ExampleFlow {
	return &ExampleFlow{}
}

func (*ExampleFlow) GetSteps() []dex.StepDef {
	return []dex.StepDef{
		dex.DefineStartStep(ExampleStep{}),
		dex.DefineStep(Finish{}),
	}
}
```

Use `dex.None` for nil-only input/output and concrete structs for durable payloads.

A no-wait Step embeds the input-typed default and returns a durable decision:

[Pinned runnable source](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/primitives/flow/workflow.go)
<!-- dex-source: examples/go/primitives/flow/workflow.go -->
```go
type Finish struct {
	dex.StepDefaultsNoWaitFor[int]
}

func (Finish) Execute(ctx dex.Context, input int) (*dex.StepDecision, error) {
	if err := Status.Set(ctx, "done"); err != nil {
		return nil, err
	}
	return dex.GracefulComplete(input + 1), nil
}
```

## Registry, Worker, and Client

Construct every Flow once, then pass the same definitions into the Registry used by Worker and Client. See the [registry](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/registry/registry.go) and [bootstrap](https://github.com/superdurable/dex/blob/sdk-go/v1.2.1/examples/go/cmd/server/dex/dex.go). Controllers start with `client.StartFlow(ctx, flow, flowID, input, options)` and retain the run ID for diagnostics.

## Route by task

- Syntax/state semantics: [primitives](primitives.md)
- Application shape: [patterns](patterns.md)
- Real-server verification: [testing](testing.md)
- Client boundary design and retry ownership, before implementation: [error handling](error-handling.md)
- Persistence/maps/Streams: [data handling](data-handling.md)
- Histories/progress: [observability](observability.md)
- Open-Flow compatibility: [versioning](versioning.md)
- Go traps: [gotchas](gotchas.md)
- Locks/loading/heartbeat/cancellation: [advanced features](advanced-features.md)

## Completion checklist

Confirm every Step type and persistent definition is registered, errors are returned, Client calls have deadlines, tests use unique IDs and a real Dex Server, and application code does not depend on Dex Server internals.
