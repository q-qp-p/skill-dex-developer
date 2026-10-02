# Build, test, and handoff

For write/read boundaries, follow the shared [SDK consistency matrix](../../dex-sdk/references/core/read-after-write.md). Test direct Temporal RPC reads on the first read; confirm triggered business work separately. Do not add callbacks or polling to strong paths solely because they use Signal.

## Implementation loop

Use the basic-process template's stable commands. Change `openapi/openapi.yaml`,
then regenerate; never hand-edit generated Go or TypeScript clients. The
generated directories exist only as ignored local build outputs. Never stage,
commit, or include them in a pull request.

Read `.superverse/template.json` for the exact command surface. In a fresh
checkout, restore its locked dependencies through the declared bootstrap
command before generation or checks (normally `make bootstrap`, including
`npm --prefix web ci` and the declared Go modules). A missing generator
executable requires dependency restoration, not repeated failing builds or a
package upgrade. Reuse the installed dependencies until their manifests or
lockfiles change.

Read `.superverse/template.json` for the exact command surface. Use the declared
`checkStatic` source gate when available: regenerate the Go and TypeScript
contracts, validate every strict FDG 2.0 definition, check Go, and build the
production backend and frontend. A retained older template may require separate
`make build` and `make check-fdg-v2` commands. Preserve its declared commands;
do not invent a removed test target or hand-edit generated outputs.

A source handoff and real business acceptance are separate milestones. Default
applications do not add integration/browser test suites, mocks, fixtures, or
test-framework dependencies. The source-only template's full check covers
generation, strict FDG, formatting/modules/vet, types, and production builds.
Generate application tests only when the user explicitly requests them. When
applying an authorized source-only migration, remove inherited template test
scaffolding and synchronize commands, manifest, checker, docs, and unused
dependencies. Preserve unrelated tests in imported applications.

A hosted authoring sandbox can hand off clean, pushed, source-verified code for
Preview configuration without a private Connector key or isolated test stack.
Missing configuration does not make otherwise complete source blocked. Record
real execution as pending and complete the requested Preview/Live journey
through the host; never call compilation a provider or deployment success.
An explicitly requested executed test remains incomplete until its real
dependencies pass. Repair actual source-gate failures before handoff. This
default does not remove platform acceptance or Connector-library verification.

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
journeys before visual polish; this does not require generating an
application test suite. For explicitly requested tests, follow the repository's
real-dependency policy: no unit tests, component mocks, fake providers, or
intercepted API responses in the template. Trigger cases through actual APIs,
or record the unverified invariant. Check both production artifacts after an
API change; a successful Go compile does not prove that the frontend's generated
imports still exist. Run relevant source checks after each edit batch and keep
the requested real acceptance result separate from source readiness.

Before installing a database, cache, ORM, or separate read model, review the
storage decision matrix and name the exact query, concurrency, transaction, or
analytics requirement that Dex Attributes, AttributeMaps, indexes/search,
typed RPCs, partitioning/chunking, blob storage, and Attribute Store projection
cannot satisfy. Remove an unneeded dependency when Dex meets the requirement.
When external storage is justified, test its declared authority boundary,
projection/synchronization lag, retry behavior, outage handling, and
reconciliation instead of treating a successful happy-path write as proof.

Only actual dependency calls establish Dex durability, Worker replacement,
Timer, RPC, retry, provider or application E2E behavior.

For standalone development, show Dex Web early. Once the first Flow graph renders, keep one user-facing `dexcli dev` stack running with a persistent `--flow-rendering-dir`, stable ports, and persistent state, and give the user its URL before continuing. Continue implementation and source checks; use isolated test stacks only for explicitly requested automated tests, and never let them reuse or stop the user's stack. Do not wait until verification passes to start it. Report its URL again at handoff. In a platform with native Studio management,
use that existing surface and authenticated Go backend instead; Dex engine Pods
need only `api,interpreter`. Do not start a second management server or infer that
this platform boundary removes standalone Dex Web support.

## Baselines and local CLI

Do not advance the template pins during ordinary application work. If the user
explicitly requests a template-stack upgrade, advance these pins together;
the template's static contract checker records its own release values, so changing only some of them fails `make check`:

- `DEX_SERVER_BASELINE` and `DEX_CLI_BASELINE`;
- the `github.com/superdurable/dex/sdk-go` requirement in `go.mod`;
- the expectations in the template static contract checker.

Do not add or update a project-local skill submodule. The coding-agent host
supplies the immutable Dex Skills release independently from the application
template.

Template scripts call `dexcli` from `PATH` and do not check its version. Run `dexcli version` first and require at least `v0.14.0`. When upgrading the global CLI would break other projects pinned to older Servers, install a project-local CLI and put its directory first on `PATH` for the template commands; `scripts/check-fdg-v2.sh` also honors `DEXCLI`.

Validate every Flow file, not only the template's `internal/process/flow.go`; see [Dex Web v2 validation](dex-web-v2.md#validation).

## Durable verification

This section guides requested runtime acceptance, not a requirement to generate
test scaffolding in every application. Use the host's real Preview/Live path
when available. SDK and Connector contributors retain their own verification
requirements. Use a real Dex Server when behavior crosses a Client, Worker,
wait, RPC, Channel, Timer, Stream, retry, provider, or process boundary.

Cover:

- start and typed terminal output;
- duplicate start/request behavior and [StartFlow-first ordering](../../dex-sdk/references/core/testing.md#startflow-ordering-and-retry-identity), with reconciliation reads confined to relevant error branches;
- durable wait and Worker replacement;
- accepted-start responses without defensive identity/Attribute rereads, and [durable downstream start recovery](../../dex-sdk/references/core/testing.md#downstream-start-recovery) with no dependent API-side second start;
- Action eligibility, valid action, duplicate/late action, and terminal rejection;
- role-to-permission mapping, unauthorized Action rejection, and multi-permission work discovery at the application boundary;
- concurrent Action-source writes without projection-only locks and cumulative permission history after state changes and completion;
- retry and exhausted-recovery behavior;
- provider idempotency and unknown-outcome reconciliation;
- summary/display reads before, during, and after terminal completion;
- terminal-readable entity snapshots through typed `Get*` RPCs after closure, following the SDK's [terminal entity read scenario](../../dex-sdk/references/core/testing.md#terminal-entity-reads) and [terminal read RPC rule](../../dex-sdk/references/core/error-handling.md#terminal-read-rpc-rule);
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
- every top-level Flow is justified by its authoritative owner,
  retention/cleanup, independent waits or Timers, and terminal lifecycle;
- parallel work remains in Steps by default, and every SubFlow has concrete
  evolution evidence, rejected Step/batching/RPC alternatives, a defined
  parent-child lifecycle, and explicit user confirmation;
- temporary validation, failure, and expiry state cannot pollute a long-lived
  authoritative Attribute or AttributeMap owner;
- the authorization model starts with `admin`, keeps Action permissions
  granular, and justifies every additional role with a distinct authenticated
  membership and visibility or operation boundary;
- the confirmed UI mode is recorded;
- the management UI capability mapping was completed before the UI-mode
  decision and designs Summary, Display, Action, Indexed Attribute, Work Queue,
  and permission coverage;
- every Custom UI surface names a specific remaining Dex Web v2 capability gap;
- a No custom UI shell contains no business controls or management routes;
- a Custom UI has an approved static page inventory, navigation, fields, and
  actions before backend work, with no early visual-polish artifacts;
- its OpenAPI contract was designed with the Flow and Connector boundaries,
  both generated clients and production bundles reproduce locally, neither generated directory is
  tracked, and the Go HTTP boundary implements the generated server interfaces;
- its dynamic UI uses only the generated TypeScript client, and visual polish
  followed a passing real Dex and
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
- for standalone local configuration, the displayed connection path and
  **DEX_CONNECTOR_CONFIG_FILE** launch command work after a Dex Web restart;
  for project-scoped configuration, exact snapshot and credential versions
  survive management-host and Worker replacement without exposing secrets;
- `dex-app.yaml` lists every Release Flow source and static connector
  connection, including its exact published `modulePath`, without configuration
  values or secrets; local source validators and generated artifacts preserve
  the same deployment schema;
- `make superverse-release-artifacts` emits a valid FDG 2.0 bundle, connector
  contract, environment contract, and exact application manifest;
- Live Publishing accepts an eligible main-branch commit regardless of author,
  prepares its exact FDG/manifest, configures that source and builds the whole
  application with a frozen configuration reference before deployment; a Flow
  Type is never the deployment unit. Preview uses the current clean pushed
  Sandbox source through Build Configuration and Preview controls;
- a hosted deployment pins a READY connector configuration revision, exact S3
  object version, and digest, and fails closed when any identity mismatches;
- hosted bootstrap uses the official `projectconfig.LoadFromEnvironment` with
  trusted `DEX_PROJECT_*` scope, canonical key, exact version/digest and scoped
  AWS identity; it never substitutes latest, a mounted configuration file or
  a credential broker. Resolve/apply application environment before Workers
  start, and keep provider tokens entirely inside the official SDK boundary;
- requested acceptance for known token expiry, concurrent calls, credential rotation,
  lost exchange responses and Worker restart records actual results or explicit
  gaps, without recreating the released Connector's test suite in the app;
  retries join an admitted exchange and only an immutable result authorizes
  recovery. Unknown expiry or an unclassified 401 never triggers refresh;
- connector fork/PR status and any release blocker are explicit;
- no `go.work`, local `replace`, branch, pseudo-version, or commit SHA remains
  in the production dependency graph;
- the repository has a clean, reviewable commit;
- limitations and unimplemented integrations are explicit.

For a requested Dex AI Platform deployment, record the observed project URL,
source commit, Release ID, configuration revision, deployment identity, and
real E2E result. Never substitute local mocks or an image-only build for those
identities, and never invent an upload command, URL, or success result.
