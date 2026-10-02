# Stage 4: integrate the Custom UI, verify, polish, and hand off

Read [build, test, and handoff](build-test-handoff.md). Run narrow checks while iterating, then the source gate declared by the template and all requested real acceptance scenarios. Every Flow must pass FDG 2.0 JSON analysis with `valid: true`. A source gate does not prove business execution; a missing test service must not be reported as a pass.

Default application authoring produces source without integration/browser test
suites, mock providers, fixtures, or test-framework dependencies. Generate an
application test suite only when the user requests it. Source checks and both
production builds remain required. A missing private Connector key leaves
configured execution pending; it does not block handoff of complete, checked
source to Studio Configuration. Host acceptance and Connector-library tests
have their own scope and are not removed by this application default.

For No custom UI, verify the Hello World page, `GetApplicationInfo`
generated-client call, local regeneration and compilation, production build,
absence of management routes, Dex Web actions/display, and any retained
webhook. Remove mock-server routes, lifecycle state, Mock Controls, mock launch
scripts, and mock E2E from the product; do not preserve them as dormant
scaffolding.

For Custom UI, implement the Go backend and generated TypeScript client calls
against the same OpenAPI contract. Do not wait for private provider credentials
before completing source. Implement the confirmed loading, validation, empty, success,
failure, retry, recovery, and terminal behavior. Exercise the configured real
journey without generating a separate test framework unless requested. Follow
the application repository real-dependency test policy for requested tests; do not
introduce component mocks or intercepted API responses. Report a case requiring
unavailable dependencies as incomplete, separately from source readiness.
Do not create an application-level mock server. Do not create a second Go business backend, product mock routes,
or user-visible Mock Controls.
Mock evidence never replaces real Dex durability, Connector, or application E2E evidence.

Only after the real Dex and Connector end-to-end journey passes may the Custom
UI add images, custom icons, branding, animation, refined responsive behavior,
or other visual polish. Recheck the affected real journey and production build after polishing; this does not require adding an application test suite. Do not generate or source visual assets
before this stage.

Use a real Dex Server for waits, RPCs, Channels, retries, Worker replacement, terminal behavior, Work Queue permission history, and connector boundaries. Use deadline-based convergence rather than fixed sleeps.

### Project release and hosted deployment handoff

Before platform handoff, keep `dex-app.yaml` complete and run the template's
`make superverse-release-artifacts` target. It must render every declared Flow
as valid FDG 2.0 and emit the Flow Definition bundle, connector contract,
environment contract, and exact application manifest. Treat missing, duplicate,
or diagnostic-bearing Flow Definitions as release failures.

Live Publishing is project-scoped. Select an eligible main-branch commit,
prepare its exact FDG/manifest, configure that source, build the whole application
with its frozen configuration reference, and select a successful Release to deploy.
Preview uses the current clean, pushed Sandbox commit in Build Configuration and
Preview controls, without choosing or creating a Live Release. Do
not filter commits by author or by whether an agent created them. A selected
Flow Type changes only Build or Runs inspection; Publishing has no Flow Type
deployment selector and deploys every Flow Definition in the Release.

For hosted Connector configuration, require validation against the selected
source's exact manifest/FDG and freeze the accepted revision, object version and
digest. The platform supplies trusted `DEX_PROJECT_*` references and scoped AWS
credentials; the official SDK loads and verifies the snapshot before Workers or
application goroutines start. Ordinary settings need a new build/deployment or
Preview start. Shared environment credentials take effect on the next connection
use; the SDK alone performs supported expired-credential refresh. Missing or
mismatched configuration, snapshot digest, capability or workload identity blocks
deployment. This platform management boundary does not upgrade the application
template's Go/SDK pins or require a new Dex release.

Finish with:

- confirmed business, UI-mode, permission-boundary, and connector decisions;
- implemented and verified behavior;
- connector release or fork/PR status;
- exact test evidence;
- remaining limitations and release blockers;
- a clean default-branch Git commit suitable for project-level Publishing;
- the generated Release artifact check and hosted connector readiness status
  when deployment was requested.

When the user requests deployment, use the project's canonical Publishing page
to prepare the selected Live commit, configure it, build and deploy the accepted
Release. Use Build Configuration and Preview controls for a requested Preview. Report only observed Release, configuration revision,
deployment, and E2E identities; never fabricate a deployment result.
