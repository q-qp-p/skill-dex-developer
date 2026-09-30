# TypeScript error handling

## Worker handler failures

Throw or reject when the method attempt must fail. Configure `waitForRetry` and `executeRetry` independently and route exhausted failures with `WaitForFailure` or `ExecuteFailure`. A recovery Step reads `context.recoveryError` and must be registered in the Flow's StepList.

Do not catch and return a success decision merely to suppress retry. That commits staged mutations. External calls are outside the Dex commit, so use stable idempotency keys and compensation for ambiguous outcomes.

## Client failures

Catch exported SDK error classes such as `FlowAlreadyStartedError`, `FlowNotFoundError`, `FlowNotActiveError`, and `RequestTimeoutError`. Durable Step and Attribute waits never expose transport long-poll expiry; they reattach with the effective Request ID and preserve the total `requestTimeoutMs` budget. `RequestTimeoutError` means that caller-visible budget expired, not that the Flow or accepted durable Update failed. `internalHandlerTimeoutMs` rollover is transparent. For lower-level cases, `DexServiceError` exposes the gRPC code and diagnostic detail. Do not compare human-readable detail for normal control flow when a typed error exists.

Concrete remote Client errors extend `DexServiceError`; local definition, value-mapping, argument, and programming errors do not. In a `catch` block, keep the value `unknown` and narrow with `instanceof`. Catch `DexServiceError` only at a boundary whose policy intentionally treats every remote Dex outcome the same; ordinary domain logic should match the concrete exported class it can decide.

When the API promises a critical operation has completed, follow the shared [required business milestone rule](../core/error-handling.md#wait-for-a-required-business-milestone): after start success or matching-request deduplication, call `Client.waitForAttributeMatch` or `Client.waitForStepCompletion` for the committed condition or the specific persistence Step execution. Publish that condition only after the business effect commits. Bound the wait; timeout does not undo acceptance or prove the operation failed. An acceptance-only response needs no wait.

For an idempotent start, set one stable `StartFlowOptions.requestId` and `ignoreAlreadyStarted: true` only when a retry of that same logical request may attach to the existing run. A remaining `FlowAlreadyStartedError` means a different Request ID owns the Flow ID. Treat it as a domain conflict unless the coordinator contract deliberately redirects the command to that existing Flow. Another `DexServiceError` can leave acceptance unknown; retry with the same identities or read owning domain state, never a dedicated start-deduplication table.

For an explicitly best-effort external `client.writeStream`, log sanitized identity and discard only an `instanceof DexServiceError` failure. Rethrow other values so codec, definition, and programming defects remain visible.

[Pinned example error classification](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/typescript/src/service-errors.ts)
<!-- dex-source: examples/typescript/src/service-errors.ts -->
```typescript
export function isFlowAlreadyStarted(error: unknown): boolean {
  return error instanceof DexServiceError && error.code === grpcAlreadyExists;
}

export function isFlowMissingOrInactive(error: unknown): boolean {
  return error instanceof DexServiceError && error.code === grpcNotFound;
}
```

The runnable examples use code classification only where one service code intentionally combines missing and inactive outcomes. Prefer exported concrete errors in new application code.

## Async discipline

Await every Client call. If a fire-and-forget call is intentional, attach rejection handling and document ownership. Let Express/Koa/Fastify error middleware translate expected application errors; do not erase `cause`, Flow ID, or method context.

## Recovery checklist

- Bound retries so recovery can run.
- Persist compensation facts before risky effects.
- Make each effect and compensation retry-safe.
- Log Flow ID, Run ID, StepExecution ID, method, attempt, and original cause.
- Treat cancellation as a request, not proof the remote effect stopped.
- Test failure before commit, after external success, during replacement, and after terminal Flow status.
