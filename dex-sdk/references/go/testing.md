# Testing Go applications

Prefer integration tests against a real Dex Server. Unit tests can verify pure helpers, but mocks cannot prove registration, serialization, durable waits, Worker replacement, retry exhaustion, or terminal behavior.

## Harness

Run `dexcli dev`, start the application Worker, and create a Client from the same Registry and BlobCache. Give every test a unique Flow ID. Bound setup, calls, polling, and cleanup with `context.WithTimeout`.

[Pinned integration source](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/go/integ/main_test.go)
<!-- dex-source: examples/go/integ/main_test.go -->
```go
func integrationContext(t *testing.T) context.Context {
	t.Helper()
	ctx, cancel := context.WithTimeout(context.Background(), time.Minute)
	t.Cleanup(cancel)
	return ctx
}
```

```bash
cd examples/go
make e2eTests
```

## Required scenarios

1. Start, wait, and assert output plus terminal status.
2. Stop a Worker after a durable boundary; replace it with identical definitions and prove resumption.
3. Fail Execute until retry exhaustion; assert terminal failure or configured recovery.
4. Publish Channel data before/during the wait; assert consumption, deletion, and RPC idempotency.
5. Restart across a Timer and prove it fires without sleeps in the test.
6. Write/read Stream frames using resume tokens.
7. Test graceful completion, force completion, failure, cancellation, timeout-handler, and uncompleted/dead-end behavior separately.

Use `require.Eventually` or Client long polls, never fixed sleeps for convergence. On deadline, report Flow/run IDs, summary, and relevant history. Do not assert scheduler ordering between parallel Steps; assert business invariants. Generate unique entity/map instances when sharing an Attribute Store.
