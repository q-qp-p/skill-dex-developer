# Build, test, and handoff

## Implementation loop

Use the basic-process template's stable commands. Change `openapi/openapi.yaml`,
then regenerate; never hand-edit generated Go or TypeScript clients. The
generated directories exist only as ignored local build outputs. Never stage,
commit, or include them in a pull request.

The public command surface is `make bootstrap`, `make generate`,
`make check-fdg-v2`, `make test-unit`, `make test-integration`,
`make test-e2e`, `make build`, `make dev`, and `make check`. Build, test, and
development targets regenerate before compilation; `make check` generates only
once. Do not restore `make check-generated`, `make mock`, or
`make test-mock-e2e`.

Keep the template release's `go.mod`, `go.sum`, npm lockfile, Go toolchain,
Dex Server/CLI baselines, generators, and Make targets unchanged unless the
user explicitly requested the corresponding stack or dependency change. A
newer `DEX_BASELINE` in the skill repository is not an application upgrade
instruction.

For **No custom UI**, reduce OpenAPI to `GetApplicationInfo` plus confirmed
integration ingress, regenerate both clients locally, and remove
process-management routes, mock-server routes, mock lifecycle code, Mock
Controls, mock launch scripts, and mock E2E. Verify the Hello World page
through the generated client. Do not run a mock approval checkpoint for an
inert shell.

For **Custom UI**, use `npm --prefix web run dev` for the low-fidelity static
checkpoint and verify only that each direct page URL and navigation path renders.
Do not introduce a mock server, model lifecycle states, generate visual assets,
or polish the surface before the page inventory is confirmed.
The approved discovery artifact must name the Dex Web v2 capability gap that
requires each custom management surface. Keep management operations covered by
Summary RPC, Display RPC, Action RPC, Indexed Attributes, Work Queue, editable
fields, timeline, or graph inspection out of the custom backend and UI.

During Flow and Connector design, finalize `openapi/openapi.yaml`, run
`make generate`, and implement the generated Go server interfaces before wiring
the generated TypeScript client into the UI. Run real Dex and Connector
integration and E2E before visual polish. After the contract exists, use
component-level mocks of the generated client for difficult UI states. Permit
test-local Playwright request interception only for a browser-only edge case;
do not add an application-level mock server, second Go business backend,
product mock route, or user-visible Mock Controls. Run the narrowest relevant
check after each edit batch. Before handoff run the repository's full
`make check`, which generates once and then covers real Dex integration and
E2E, FDG 2.0 validation, frontend tests, and the production build. After visual
polish, rerun component tests and real E2E.

Before installing a database, cache, ORM, or separate read model, review the
storage decision matrix and name the exact query, concurrency, transaction, or
analytics requirement that Dex Attributes, AttributeMaps, indexes/search,
typed RPCs, partitioning/chunking, blob storage, and Attribute Store projection
cannot satisfy. Remove an unneeded dependency when Dex meets the requirement.
When external storage is justified, test its declared authority boundary,
projection/synchronization lag, retry behavior, outage handling, and
reconciliation instead of treating a successful happy-path write as proof.

Treat component mocks and intercepted browser responses as UI evidence only.
They cannot establish Dex durability, Worker replacement, Timer, RPC, retry,
provider, or application E2E semantics.

Show Dex Web early. Once the first Flow graph renders, keep one user-facing `dexcli dev` stack running with a persistent `--flow-rendering-dir`, stable ports, and persistent state, and give the user its URL before continuing. Then keep implementing and testing against isolated test stacks. Do not wait until verification passes to start it, and do not let test scripts reuse or stop it. Report its URL again at handoff.

## Baselines and local CLI

Do not advance the template pins during ordinary application work. If the user
explicitly requests a template-stack upgrade, advance these pins together;
`internal/templatecontract/contract_test.go` hard-codes the template's own
release values, so changing only some of them fails `make check`:

- `DEX_SERVER_BASELINE` and `DEX_CLI_BASELINE`;
- the `github.com/superdurable/dex/sdk-go` requirement in `go.mod`;
- the expectations in the template contract test.

Do not add or update a project-local skill submodule. The coding-agent host
supplies the immutable Dex Skills release independently from the application
template.

Template scripts call `dexcli` from `PATH` and do not check its version. Run `dexcli version` first and require at least `v0.14.0`. When upgrading the global CLI would break other projects pinned to older Servers, install a project-local CLI and put its directory first on `PATH` for the template commands; `scripts/check-fdg-v2.sh` also honors `DEXCLI`.

Validate every Flow file, not only the template's `internal/process/flow.go`; see [Dex Web v2 validation](dex-web-v2.md#validation).

## Durable verification

Use a real Dex Server when behavior crosses a Client, Worker, wait, RPC, Channel, Timer, Stream, retry, provider, or process boundary.

Cover:

- start and typed terminal output;
- duplicate start/request behavior;
- durable wait and Worker replacement;
- Action eligibility, valid action, duplicate/late action, and terminal rejection;
- role-to-permission mapping, unauthorized Action rejection, and multi-permission work discovery at the application boundary;
- concurrent Action-source writes without projection-only locks and cumulative permission history after state changes and completion;
- retry and exhausted-recovery behavior;
- provider idempotency and unknown-outcome reconciliation;
- summary/display reads before, during, and after terminal completion;
- connector Trigger Flow/RPC routing and correlation when used.
- RPC-to-Connector-Step routing when an application RPC requests provider work;
- application integration against any uncommitted local connector `replace`,
  plus the matching connector module's provider and real-Dex tests.

For a No custom UI application, also assert that no approval, display, status,
list, search, detail, retry, escalation, Action-proxy, or Attribute-proxy HTTP
route remains. Test each retained webhook independently from Dex Web management.

Use deadline-based polling and report Flow IDs and status on failure. Do not hide or skip a failing check.

## Handoff

Ensure:

- `superverse.yaml` and `.superverse/template.json` remain valid;
- application dependencies, runtime baselines, lockfiles, and commands still
  match the pinned template unless an explicit user-approved deviation is
  recorded;
- the confirmed UI mode is recorded;
- the management UI capability mapping was completed before the UI-mode
  decision and designs Summary, Display, Action, Indexed Attribute, Work Queue,
  and permission coverage;
- every Custom UI surface names a specific remaining Dex Web v2 capability gap;
- a No custom UI shell contains no business controls or management routes;
- a Custom UI has an approved static page inventory, navigation, fields, and
  actions before backend work, with no early visual-polish artifacts;
- its OpenAPI contract was designed with the Flow and Connector boundaries,
  both generated clients reproduce locally, neither generated directory is
  tracked, and the Go HTTP boundary implements the generated server interfaces;
- its dynamic UI uses only the generated TypeScript client, UI mocks exist only
  in test processes, and visual polish followed a passing real Dex and
  Connector end-to-end journey;
- secrets are absent from files, logs, generated values, and archives;
- dependencies and released connector versions are pinned;
- every connector capability matrix records the canonical published catalog,
  exact capability name and kind, component tag, and immutable manifest URL;
- every public-provider boundary reuses an available released connector
  capability or records the contributor PR and release blocker;
- every internal-service boundary records the existing/new internal connector
  library decision or the reason generic HTTP remains appropriate;
- each configurable Connector Step has a static connection name matching its generated Connection;
- each Connector Step branch receives only its current operation result, while application Attributes retain domain context;
- every Connector factory uses pure `MapToOperationInput` and graph-only `Annotations`;
- each Connector Trigger binding has a static binding name, application-owned Flow ID resolver, and typed target;
- the displayed local connection path and **DEX_CONNECTOR_CONFIG_FILE** launch command work after a Dex Web restart;
- connector fork/PR status and any release blocker are explicit;
- no `go.work`, local `replace`, branch, pseudo-version, or commit SHA remains
  in the production dependency graph;
- the repository has a clean, reviewable commit;
- limitations and unimplemented integrations are explicit.

Dex AI Platform upload is not available yet. State that the repository is ready for future import only when no connector release blocker remains. Do not invent an upload command, deployment URL, or success result.
