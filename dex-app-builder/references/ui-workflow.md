# Application surface workflow

Use this only after discovery completes the management UI capability mapping.
Design Summary RPC, Display RPC, Action RPC, Indexed Attribute, Work Queue, and
permission coverage before selecting a mode. Needing an admin or management
interface does not by itself justify Custom UI; that mode requires a recorded
Dex Web v2 capability gap.

## No custom UI

Dex Web owns every process-management interaction. Adapt the template to keep:

- a non-business Hello World React page;
- the Go HTTP server and OpenAPI source;
- locally generated Go server interfaces and TypeScript client;
- one `GetApplicationInfo` operation used by the page;
- generation, build, and smoke-test commands.

Remove process state, management operations, Action/Attribute proxy endpoints,
dashboards, forms, mock lifecycle state, Mock Controls, fixtures, and related
tests. The shell must not present approval, display, status, list, search,
detail, retry, or escalation controls.

Retain a webhook only when it is confirmed integration ingress. An external
provider webhook belongs to its dedicated Connector Trigger. An internal
system may use the generic HTTP webhook connector.

Do not require mock approval for the inert shell. Verify that the generated
client calls `GetApplicationInfo`, the production build passes, and no
management route remains. Remove mock-server routes, lifecycle state, Mock
Controls, mock launch scripts, and mock E2E. If custom behavior is requested
later, follow the workflow below before connecting it to production.

## Custom UI

Enter this mode only for the unsupported interaction named in the confirmed
management UI capability mapping. Keep operations already covered by Dex Web v2
on its native Run, Work Queue, detail, Action, edit, timeline, and graph
surfaces.

### 1. Low-fidelity static checkpoint

Agree only on the information architecture needed to unblock backend design:

- role-specific entry pages and ordinary link navigation;
- necessary list, detail, create, action, and completion pages;
- labels, inputs, buttons, and placeholder regions on each page;
- which Dex Web v2 surfaces remain available to maintainers.

Implement those pages as static markup in the template React/Vite frontend.
React remains the rendering shell, but this checkpoint has no hooks or
application state, API imports, generated-client calls, local storage, timers,
mock lifecycle, Mock Controls, or provider behavior. Use no images, generated
art, custom icons, animation, branding, gradients, or decorative effects. Keep
CSS neutral and minimal. Inputs and buttons are inert; use ordinary links or
link-styled buttons only to demonstrate navigation between directly openable
page URLs.

Run `npm --prefix web run dev` on a stable local port and verify that every
page URL renders. Give the user a page inventory with each name, purpose, and
direct URL. Ask for explicit confirmation of the page set, navigation, fields,
and actions. Do not ask the user to approve colors, typography, imagery,
responsive refinements, dynamic states, or production behavior at this point.

### 2. Contract and backend design

After the static checkpoint is confirmed, design the Flow, Connector
capabilities, and application OpenAPI contract together. Map every approved UI
action to an application operation backed by a Flow start, typed RPC, query, or
confirmed ingress. Define authentication and permission enforcement,
idempotency, asynchronous status, validation, response and error shapes, retry,
and terminal outcomes.

OpenAPI describes the application's business boundary. It must not expose Dex
Steps, Channels, Attributes, connection credentials, or other runtime internals.
Update `openapi/openapi.yaml` and run `make generate` before implementing HTTP
handlers. The Go backend implements the generated server interfaces, and the
browser later consumes the generated TypeScript client. Do not hand-write
parallel transport types.
The generated directories are ignored local build artifacts. Regenerate them in the workspace, but never edit or commit them.

Implement and verify the Go Flows and required Connectors before returning to
dynamic frontend work. A missing public Connector capability follows the
Connector Contributor workflow and remains subject to its authorization and
release requirements.

### 3. Integration and durable verification

When the Go application boundary and its real Dex and Connector paths run,
replace the wireframe's inert controls with generated TypeScript client calls.
Add the confirmed loading, validation, empty, success, failure, retry, recovery,
and terminal behavior. The browser calls the application API; it never imports
a Dex client or accesses raw Dex primitives.

Use component-level mocks of the generated client for isolated loading,
validation, empty, failure, retry, and terminal states. If a browser-only edge
case cannot be triggered economically through the real application, use
request interception inside that Playwright test only. Do not add an
application-level mock API, a second Go business backend, product mock routes,
or user-visible Mock Controls. Prove waits, RPCs, retries, Worker replacement,
provider effects, and terminal behavior with the real Dex and Connector end-to-end path; mock evidence cannot substitute for it.

Do not claim application-level UI controls provide platform RBAC. A permission
selector filters work; it does not grant permission. Enforce identity-to-
permission mapping at the trusted application boundary. Keep credentials and
provider secrets server-side.

### 4. Visual polish

Only after the real end-to-end journey passes may the UI add imagery, custom
icons, branding, animation, refined typography, decorative styling, and
responsive fine-tuning. Preserve the generated client boundary and confirmed
behavior. Then rerun frontend component tests, the real end-to-end journey,
accessibility checks, and the production build.
