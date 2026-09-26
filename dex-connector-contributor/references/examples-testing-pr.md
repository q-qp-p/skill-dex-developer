# Examples, testing, and PR

## Connector-local example

Add a runnable example inside a new connector or when adding a major capability.
Extend an existing example when it already represents the provider journey.
Keep production package APIs separate from example-only business state.

With a Trigger, demonstrate the actual source, binding configuration, durable
pre-ack delivery, typed Flow start and/or typed RPC routing, application filter,
duplicate handling, restart replay, Query/Mutation usage, and explicit recovery
for uncertain writes.

Without a Trigger:

1. define a typed Flow that uses the operation-specific factory;
2. expose a valid static `ConnectionName` and any configuration UI;
3. generate strict FDG 2.0 with `valid: true`;
4. configure the connection in Dex Web v2;
5. select the healthy Worker and use **Start Flow** with schema-valid JSON;
6. inspect the Run through terminal completion or an explicit recovery path.

Start Flow is a local-selector development feature, not an authentication
boundary or substitute for a production Trigger.

Before the first Start Flow attempt, apply the shared
[Start Flow requirements](../../dex-app-builder/references/dex-web-v2.md#start-flow):
FDG JSON in `--flow-rendering-dir`, explicit `GetFlowType` and `GetStepType`
names, a start Step with `WaitFor`, and `GetDexSummary`/`GetDexDisplay`.

The compatibility gate copies each `examples/**/flow/` directory into a fresh
consumer module that requires only the connector module. That package must
compile on its own, and exactly one of its files may contain `GetSteps(`
(observed at connectors `main` `d975226`).

For a repeatable check, drive the same start through the headless Dex Web
endpoints in the shared reference. A placeholder local connection record
pointing at the deterministic fake provider reaches **Ready** without real
secrets (Dex CLI v0.13.8). It proves setup and routing, not live provider
behavior.

## Verification matrix

Run narrow tests while iterating, then all applicable checks:

```bash
GOWORK=off go test -race ./...
GOWORK=off go vet ./...
npm ci
npm test
npm run build
```

Run those Go commands from every changed module. Then run the repository's
codegen, registry, catalog, and release-matrix checks; the connector's real Dex
integration target; strict FDG 2.0 analysis; `make test-dex-compat-current`;
and root `make check`.

Prerequisites observed at connectors `main` `d975226` with Dex CLI v0.13.8:

- `make test-integration` runs `go test -tags=integration`, so integration
  files need `//go:build integration`; they read the Dex address from
  `DEX_FLOW_SERVICE_ADDRESS`.
- Isolate each local stack with `dexcli dev` flags `-dex-port`, `-web-port`,
  `-sqlite-db-filename`, `-connector-config-dir`, and `-blob-store-dir`.
- `make test-dex-compat-current` needs Python 3.11.4 or later (`tarfile`
  extraction with `filter=`) and a CA bundle reachable through
  `SSL_CERT_FILE`.
- When local Go is newer than the Go that built dexcli, set
  `GOTOOLCHAIN=go1.24.0` for the compatibility gate. Otherwise the consumer
  `go.mod` records the newer version (Go 1.27 wrote `go 1.27.1`) and dexcli
  rejects every example.

Integration tests use a real Dex Server for Step retries, Attribute/Stream
registration, transitions, uncertainty, Trigger redelivery, RPCs, and Worker
replacement. Poll with deadlines and useful diagnostics; never use a fixed
sleep as correctness proof. `Worker.Stop` drains in-flight handlers, so it
cannot simulate a crash during a provider call; run the Worker as a subprocess
and SIGKILL it.

### Pre-release verification

Dex Web automatic setup accepts only an exact official released module. Before
release, exercise Connections and Start Flow with
`dexcli dev --connector-release-override` and an artifact built by
`connectorctl release-artifact` from the same source, or resolve pre-release
versions only inside a temporary `GOMODCACHE`. Never resolve an unreleased
real version, such as the declared next `connectors/<name>/vX.Y.Z` served from
a local proxy, into the default module cache: later builds on that machine
silently use that copy or fail checksum verification.
`make test-dex-compat-current` is safe because it uses synthetic
`v0.0.<digest>` versions.

## Live provider tests

Run provider live tests only with dedicated safe credentials and bounded test
resources. Never paste credentials into a prompt, command line, fixture, log,
Flow value, or PR. If live credentials are unavailable, keep deterministic fake
provider coverage and list the exact live behavior as unverified in the PR.

- **Exact scopes:** a connector that requires an exact scope set treats a
  broader token as a mismatch. The GitHub connector requires exactly
  `read:user user:email`, so a general `gh` token with `repo` selects
  `insufficientScope`. Obtain a dedicated token with exactly the declared
  scopes, or name the unverified behavior.
- **Paid APIs:** first run an unbilled authentication probe, such as an
  unknown model that returns 404 `providerRejected`, then one tiny billed
  call. Report billing failures, such as HTTP 402 `RESOURCE_EXHAUSTED`,
  explicitly instead of treating them as connector defects.

## Four acceptance scenarios

1. **Operation-only connector:** the example generates valid FDG 2.0, is
   configured in Connections, and runs from Dex Web **Start Flow**.
2. **Trigger:** real Flow start and typed RPC delivery work across duplicate
   delivery and restart recovery.
3. **UI units:** manifest/codegen, Host API 0.2, provider command brokering,
   JSON Pointer composition, persistence, restart loading, and all visual states
   pass.
4. **SDK gap:** local joint verification succeeds, but the committed work is
   split into an SDK PR/release followed by an exact-version connector PR.

## PR handoff

Before publication, review the diff for generated drift, secrets, local
replacements, pseudo-versions, unrelated modules, and release version accuracy.
Create one clean commit using the repository scope. Push and open a
ready-for-review PR that includes:

- provider documentation or official SDK basis;
- public capability and stable identities;
- branches, retry, idempotency, uncertainty, Trigger acknowledgement, and UI
  security decisions that apply;
- example run evidence;
- every test command and result;
- provider live-test coverage or explicit omission;
- module version and any prerequisite SDK release.

## Publish and monitor CI

Use `gh` directly. Codex users who have an `$opr` workflow may use it for the
same steps.

1. Push the topic branch with `git push -u origin <branch>` to the user's fork,
   or to the official remote on the verified maintainer path.
2. Open a ready-for-review PR (no `--draft`):
   `gh pr create --repo superdurable/dex-connectors-library --base main --head <fork-owner>:<branch> --title "<scope>: <subject>" --body-file <file>`.
   On the maintainer path pass `--head <branch>`.
3. Attach the PR URL to the task and watch its checks with
   `gh pr checks <number> --repo superdurable/dex-connectors-library --watch`.
4. On failure, read `gh run view <run-id> --repo superdurable/dex-connectors-library --log-failed`,
   fix in-scope failures, rerun the matching local check, amend the commit,
   push with `git push --force-with-lease`, and watch again. Add a new commit
   instead of amending once review has started. Report out-of-scope or
   infrastructure failures instead of masking them.
5. Stop when every required check passes. Leave review and merge to the
   repository maintainers unless the user explicitly authorizes more.
