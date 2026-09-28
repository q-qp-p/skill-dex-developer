# Product discovery

Do not start implementation until the product owner confirms the business model.

## Stack checkpoint

Classify the repository before proposing a language or installing anything. A
repository containing only a README, license, or editor files is effectively
empty and defaults to the exact stack in the release named by
`TEMPLATE_BASELINE`. Record the template release as the stack decision; do not
offer TypeScript, Node, another SDK language, or a freshly selected dependency
set as equivalent defaults.

Only an explicit user request can replace the template stack for a new
application. Before accepting that request, explain that Dex App Builder, Dex AI
Platform, strict FDG 2.0, and the current Connector SDK use the template's Go
backend. A requested non-Go backend becomes a standalone `dex-sdk` project
without Connector SDK support, not a modified App Builder default.

## Role, operation, and permission matrix

Capture at least:

| Actor | Goal | Can start | Can view | Actions and permissions | Can maintain |
| --- | --- | --- | --- | --- | --- |
| Process maintainer | Own process definition and policy | product-specific | all required operational state | recovery/configuration Actions with explicit permissions | definitions and integrations |
| Manager or operator | Review and resolve work | optional | assigned or scoped runs | approve, reject, edit, retry, or escalate with one permission per Action | no code by default |
| Terminal user | Request or participate | usually their request | their relevant status | supply requested information with an explicit permission when exposed as an Action | no |
| External system | Trigger or exchange data | Trigger capability | query only when required | typed integration Action or event | no |

Replace generic labels with domain names. Record which operations require authentication, authorization, audit, or a reason. Keep roles and permissions separate: a role can hold several permissions, and several roles can share one permission.

## Lifecycle questions

Confirm:

- business identity and unique Flow ID source;
- start trigger and duplicate-start behavior;
- typed start input and completion output;
- happy path and terminal business outcomes;
- human decisions, required fields, deadlines, reminders, and escalation;
- retryable provider failures versus business rejection;
- unknown external mutation outcomes and query-first reconciliation;
- cancellation, recovery, cleanup, and operator intervention;
- searchable/indexed fields and detailed display fields;
- sensitive data that must not enter IDs, logs, Streams, or generated artifacts.

## Storage decision

Default each durable fact to Dex before proposing an external dependency.
Capture a storage decision matrix:

| Fact or collection | Owning Flow/business identity | Reads and writes | Volume/contention | Dex primitive and access path | Proven external-store gap |
| --- | --- | --- | --- | --- | --- |
| Process state | Process Flow ID | Step and Action updates, status/detail reads | product-specific | typed Attribute plus RPC/index when needed | normally none |
| Keyed or growing records | Stable domain/entity owner | exact lookup, bounded page, independent mutation | product-specific | partitioned or chunked AttributeMap with exact loads and locks | only a confirmed query or contention limit |
| Shared domain facts | Stable domain/entity Flow | reused by several process/API paths | product-specific | one owner with typed application operations | cross-Flow reuse alone is not a gap |

Do not select PostgreSQL, another database, a cache, an ORM, or a shadow read
model merely because data must persist. Dex already provides durable
Attributes, AttributeMaps, indexes/search, locks, exact instance loading, blob
offload, and optional Attribute Store projections. An Attribute Store
projection still introduces an external database; use it only for a confirmed
query gap, and prefer its server-managed projection over application dual
writes when Dex remains authoritative. Require an external store only for a
specific unsupported need such as complex/ad-hoc indexes, full-text or vector
search, high-concurrency access to one hot record, relational joins or
multi-record transactions, or large analytical scans. Record the exact
operation, expected scale/SLO, authority, synchronization, failure, and
reconciliation design. “We may need it later” is not evidence.

## Management UI capability mapping

Business process products commonly need a management interface. Design that
interface through Dex Web v2 first. For each management operation, define its
Indexed Attributes, Summary RPC fields, Display RPC fields, Action RPC input and
metadata, condition, and permission before deciding that a custom surface is
necessary.

| Management need | Dex Web v2 capability |
| --- | --- |
| List and filter business records | Model each record as a Run, expose supported search criteria as Indexed Attributes, and return additional list fields from the Summary RPC. |
| Inspect one record | Return detail fields and UI slots from the Display RPC. |
| Perform a business operation | Register an RPC with Action metadata, a typed input form, current-state condition, and one required permission. |
| Find assigned or actionable work | Use Work Queue permission history for discovery; opening a Run rechecks current Action eligibility. |
| Change simple business fields | Declare editable scalar Attributes in the Display RPC. |
| Inspect progress and failures | Use the Run timeline, Step graph, execution details, and recovery information. |

Record this mapping as a discovery artifact. If a need is fully covered, keep
it in Dex Web v2 even when another need requires Custom UI. If it is not
covered, name the exact missing interaction and its user. A general desire for
an admin portal, dashboard, management backend, or branded shell is not a
capability gap.

## UI-mode decision

Make the UI-mode decision only after completing the management UI capability
mapping and designing the Summary RPC, Display RPC, Action RPCs, Indexed
Attributes, and permissions.

Choose **No custom UI** when those surfaces satisfy operators and maintainers.
Keep only the template's non-business Hello World/OpenAPI architecture for
future evolution. Confirm whether the existing host supplies authentication,
role-to-permission mapping, project/tenant isolation, and a trusted reverse
proxy. Those controls may still be required, but they are not a second process
management backend.

Choose **Custom UI** only for a recorded Dex Web v2 capability gap, such as a
participant-facing journey, a fundamentally different navigation model, domain
visualization, or a complex interaction the platform does not provide. Record
which requirement forces the custom surface.
The first UI checkpoint confirms only the necessary pages, navigation, fields,
and actions through a low-fidelity static wireframe. It does not authorize an
interactive mock, visual system, imagery, animation, or other polish before the
Flow, Connector, and OpenAPI contract are designed.

## Connector decision

Create a connector capability matrix for every Trigger, Query, Mutation, and
integration UI. Start from the canonical published catalog at
`https://superdurable.github.io/dex-connectors-library/catalog.yaml`. For a
public external product, match each need to an exact released connector
capability—not merely a connector name—then verify the complete contract in the
component tag's immutable `connector.yaml`. Record the catalog URL, connector
ID, capability kind and name, version/tag, immutable manifest URL, and reuse or
gap decision.

If the published catalog or immutable release manifest cannot be verified,
stop connector-dependent implementation and report the blocker. A missing
connector, operation, Trigger, or UI unit with a documented API or official SDK
becomes a `dex-connector-contributor` work item and production release blocker;
it is not permission to install the provider SDK or write local integration
code.

Mark a service internal only when the organization owns and controls it. Ask
whether an internal connector library already exists, whether this application
should contribute to it, and whether the user wants to establish one with the
unified Connector SDK when none exists. Record who owns that decision. Use the
generic HTTP connector only for a controlled internal service when the user
does not choose a reusable internal connector capability.

## Confirmation artifact

Before code, provide:

1. the role/operation/permission matrix;
2. a numbered lifecycle with decisions and terminal outcomes;
3. the management UI capability mapping, including proposed Summary, Display,
   Action, Indexed Attribute, Work Queue, and permission contracts;
4. the confirmed **No custom UI** or **Custom UI** mode and any recorded Dex Web
   v2 capability gap;
5. proposed Flow, Step, state, message, timer, RPC, and connector boundaries;
6. the storage decision matrix and any evidence-backed external-store gap;
7. connector capability reuse, public fork/PR, internal-library decision, and
   release status;
8. unresolved tradeoffs.

Ask for explicit confirmation. A casual discussion response is not approval to implement.
