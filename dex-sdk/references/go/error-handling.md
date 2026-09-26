# Go error handling

## Error layers

Application errors from WaitFor, Execute, RPC, and timeout handlers drive configured retry/recovery. Typed Client errors describe Dex outcomes. Context/transport errors describe caller cancellation or connectivity. Keep these layers distinct.

Use `errors.As` for `*dex.FlowNotFoundError`, `*dex.FlowNotActiveError`, `*dex.FlowAlreadyStartedError`, `*dex.LongPollTimeoutError`, `*dex.RequestTimeoutError`, and `*dex.FlowUncompletedError`. Durable Step and Attribute waits never expose transport long-poll expiry; they reattach with the effective Request ID and preserve the total `RequestTimeout` budget. `RequestTimeoutError` means that caller-visible budget expired, not that the Flow or accepted durable Update failed. `InternalHandlerTimeout` rollover is transparent. Keep `ServiceError.SubStatus` for diagnostics; never parse strings.

Every concrete remote Client error unwraps to `*dex.ServiceError`; local definition, value-mapping, argument, and programming errors do not. Use `errors.As(err, &serviceError)` only at a narrow boundary whose policy intentionally treats every remote Dex outcome the same. Ordinary domain logic should continue matching the concrete error type it can decide.

For an idempotent start, set one stable `StartFlowOptions.RequestID` and configure `AlreadyStarted: &dex.AlreadyStartedOptions{IgnoreError: true}` only when a retry of that same logical request may attach to the existing run. A remaining `*dex.FlowAlreadyStartedError` means a different Request ID owns the Flow ID. Treat it as a domain conflict unless the coordinator contract deliberately redirects the command to that existing Flow. Another service error can leave acceptance unknown; retry with the same identities or read owning domain state, never a dedicated start-deduplication table.

For an explicitly best-effort external `Client.WriteStream`, an `errors.As` match on `*dex.ServiceError` may be logged with sanitized identity and discarded. Otherwise return the error. Context operations inside a handler, including Stream writes, must still return or wrap their error so Dex owns retry and recovery.

## Retry ownership

Return an error when Step options should decide retry. Use `dex.RetryAfter` only when the application knows a meaningful delay. Never add an in-memory retry loop around Step work; it disappears with the Worker and hides attempts.

[Pinned runnable source](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/go/patterns/polling/backoff.go)
<!-- dex-source: examples/go/patterns/polling/backoff.go -->
```go
result, err := step.service.AttemptExternalAPICall("Poll for BackoffPollingFlow")
if err != nil {
	return nil, dex.RetryAfter(time.Second, err)
}
return dex.GracefulComplete(result), nil
```

## Commit and recovery

Before non-idempotent external work, use an idempotency key derived from durable identity. After a successful side effect, persist the fact or move to a recovery-capable Step. A returned error permits retry from the previous boundary.

Use Execute/WaitFor failure policies for automatic recovery, operator Channels for manual recovery, and a timeout handler for Flow-deadline semantics. Compensation must be idempotent and identify the original commit.

Every Context operation can fail. Return or wrap its error; do not continue after a failed Attribute write, Channel delete, heartbeat, or Stream write as though it committed.
