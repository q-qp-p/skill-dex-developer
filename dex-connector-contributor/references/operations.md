# Operations

Read the required Dex SDK Core and Go references before changing Step options,
durability, retries, Attributes, Streams, or transitions.

## Contract design

Model reads as typed Query operations and external writes as typed Mutation
operations. Classify by provider state, not by whether the call feels like a
read: a stateless call that creates no provider resource, such as generation
without storage, is a Query because retry is safe and only costs tokens. Use a
Mutation when the provider stores or changes a resource. The manifest schema
pairs `mutation` with `idempotency: required` and `query` with `none`, so a
keyless stateless call declared as a Mutation would claim idempotency the
provider does not offer.

Give every public operation stable lower-camel identity, typed input/output, a
concise provider-neutral description, and operation-specific generated
factory. Application code normally calls a factory such as
`openai.NewCreateResponseStep`; generic `sdkgo.NewQueryStep` and
`sdkgo.NewMutationStep` are advanced escape hatches.

The immutable [connector contract factory example](https://github.com/superdurable/dex-connectors-library/blob/connectors/slack/v0.11.0/docs/connector-contract.md)
shows the intended application surface:

<!-- connector-source: docs/connector-contract.md -->
```go
openai.NewCreateResponseStep(openai.CreateResponseStepConfig[Input]{
    StepType:  "GenerateSummary",
    Connection: openAIConnection,
    MapToOperationInput: mapToOperationInput,
    Completed: sdkgo.GoTo(CompletedStep{}),
})
```

One Step execution runs one operation. An operation may make a small, bounded
number of provider requests, such as a lookup before a write or pagination up
to a declared limit; some shipped operations make two to five. When the result
set is unbounded, return a next-page cursor in the typed output and let the
Flow request the next page in a later Step execution. Keep every request in
`Execute`; never call the provider from `WaitFor` or an RPC. Persist
application business context before entering the Connector Step because a
branch target receives only the current operation Result.

## Branches, retries, and uncertainty

- Declare one happy-path branch and require it.
- Mark provider rejection, not-found, invalid response, uncertainty, defect,
  and other non-happy paths `optional: true` unless the process must choose a
  different continuation.
- Remember that selecting an unwired optional branch fails the Flow after any
  configured Result Attribute commits; it is not an Execute retry.
- Return retry only when repeating the provider call is safe. Respect an
  authoritative provider delay with `RetryAfter`.
- A dispatched Mutation with an unknowable outcome selects `uncertain`. Do not
  blindly retry it. Query provider state by the idempotency or correlation key,
  then continue, compensate, or expose explicit recovery.
- Classify only facts in `Failure`; never copy authorization headers, provider
  bodies, arbitrary metadata, or secrets into it.

Default Execute durability to `async`. Use `sync` only when the operation is
more likely than not to exceed five seconds. Five seconds is the Dex SDK
[classification heuristic](../../dex-sdk/references/core/step-options.md); it
leaves margin inside the ASYNC local phase, which permits at most about seven
seconds. A long LLM generation may qualify; an ordinary HTTP call with a
30-second timeout does not.

A non-streaming provider call emits no heartbeat while it waits, so the
one-minute default heartbeat timeout fails a healthy 90-second generation. Set
the operation's `heartbeatTimeout` at least equal to `executeMethodTimeout`, or
heartbeat or stream progress during the call. A long heartbeat timeout did not
delay crash recovery in local measurements: Dex CLI v0.13.8 detected a lost
Worker connection in about two seconds. The released OpenAI `createResponse`
manifest (150-second `sync` timeout, default heartbeat, observed at connectors
`main` `d975226`) carries the same risk.

## Idempotency and bounded provider work

Use the Connector Call ID-derived idempotency key for each Mutation when the
provider supports it. Provider adaptation may change its length or alphabet,
but must not incorporate attempt, Run ID, Worker, time, or randomness. Document
provider retention and replay behavior.

Bound pagination, response size, and streamed output. Model a provider-owned
asynchronous job as separate durable steps: start Mutation, Timer or webhook
Channel, status Query, then completion. Do not turn one Execute into an
unbounded poller.

## Attributes and Streams

Configure `ResultAttribute` only when an RPC, display, audit, recovery path, or
non-adjacent consumer needs the raw Result. The transition already carries the
Result to its branch target.

Define and register every Attribute and Stream in the consuming Flow's
`GetPersistenceSchema`. A Stream is best-effort progress, never authoritative
completion. Group retry duplicates by Call ID, attempt, and sequence, and use a
durable snapshot for recovery.

## Provider tests

Test request method, URL, scopes, pagination, bounded response handling,
idempotency headers/fields, retryable failures, conclusive branches, uncertain
dispatch, redaction, and malformed responses. Use a local fake provider for
deterministic coverage. Run live tests only with dedicated safe credentials and
state exactly what remained unverified when those credentials are unavailable.
See [live provider tests](examples-testing-pr.md#live-provider-tests) for
exact-scope tokens and paid APIs.
