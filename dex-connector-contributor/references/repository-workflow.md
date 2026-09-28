# Repository workflow

Contribute through the user's GitHub fork of the official
`superdurable/dex-connectors-library` repository by default. A verified
maintainer may instead choose the [maintainer branch path](#maintainer-branch-path).
Treat the GitHub fork and the local clone as separate steps.

## Target checkout discovery

The chat's current working directory does not determine the target repository.
Before changing files, identify `superdurable/dex-connectors-library` by Git
remote identity or by a verified fork whose GitHub parent is that repository.
Do not infer identity from a directory name such as `dex-connectors-library`,
and do not treat an unrelated application checkout as the connector library.

Inspect candidates in this order:

1. a checkout or worktree already verified in the current conversation;
2. the current checkout and its registered Git worktrees;
3. Git repositories beneath the host's accessible project or workspace roots,
   including secondary project folders, without scanning unrelated private
   directories;
4. a new clone selected through the fork workflow below when no suitable local
   checkout exists.

For every candidate, inspect its remotes. Accept it only when a remote resolves
to the official repository or GitHub verifies that the remote is a fork of the
official repository. Prefer a clean checkout that no other active task uses.
Preserve all unrelated changes; when a suitable clone is busy or dirty, create
an isolated managed worktree when the host supports it, otherwise a normal Git
worktree. Do not repoint or delete an in-use clone.

Before implementation, report the exact target checkout path and the remote
identity that established it, then read the target checkout's `AGENTS.md` and
other host-native repository instructions. Instructions found in the chat's
unrelated starting repository do not prove that the Contributor skill is
missing. The installed sibling skill bundle remains the skill authority.

## Fork discovery and user handoff

Before changing files, look for an existing user-owned fork in this order:

1. reuse a fork URL already verified in the current task or conversation;
2. inspect relevant local Git remotes for a user-owned repository whose GitHub
   parent is `superdurable/dex-connectors-library`;
3. inspect the authenticated GitHub account's repositories with read-only
   GitHub tooling and verify the candidate's parent repository.

Do not guess a GitHub username or treat an arbitrary repository with the same
name as a fork. Verify its GitHub parent. Do not expose tokens or other
authentication details while inspecting remotes.

If no verified fork is found, ask whether the user has already created one. If
yes, ask for its URL when it cannot be discovered and verify the parent. If no,
ask whether the user authorizes creating a fork. After the user says yes, open
`https://github.com/superdurable/dex-connectors-library/fork` in the user's
browser and ask the user to choose the owner/name and click **Create fork**.
Do not click the creation button for the user. Pause until the user confirms
that GitHub finished creating the fork, then discover and verify its exact URL.
If the user declines, stop before implementation and report that a fork is
required for the upstream contribution workflow.

After verification, reuse the target clone selected above or clone the user's
fork. Configure the contribution checkout's remotes so:

- `origin` is the user's verified fork;
- `upstream` is `https://github.com/superdurable/dex-connectors-library`.

Do not repoint `origin` on an in-use clone that names the official repository.
Use that clone only to establish repository identity, then create a separate
clone of the verified fork for the contribution. A Git worktree shares remotes
with its parent clone, so it is not an isolation boundary for remote changes.

Fetch the latest `upstream/main`, read its `AGENTS.md`, preserve unrelated user
files, and create an isolated topic branch or managed worktree from
`upstream/main`. Name the branch by the repository's branch convention, for
example `<user>/<topic>`; do not add a tool-specific prefix.
Push only to the user's fork on this default path. Open the PR from that fork
branch to the official repository's `main`. Never replace, delete, or repoint
an in-use local clone without confirming it is safe.

## Maintainer branch path

Offer an upstream topic branch instead of a fork only when all of these hold:

1. `gh api repos/superdurable/dex-connectors-library --jq .permissions.push`
   prints `true` for the authenticated account (admin is not required);
2. the repository convention uses upstream topic branches, for example merged
   PRs from `superdurable/<user>/<topic>` in
   `git log --merges --format=%s upstream/main`;
3. the user explicitly chooses it after you explain that the branch is
   published in the official repository.

Push permission alone is not consent. On this path, clone or reuse a clone of
the official repository, branch from its latest `main` as `<user>/<topic>`,
push only that topic branch, and open the PR from it to `main`. Never push to
`main`, create tags, or push another contributor's branch. If any condition is
not met, use the fork path.

## Repository boundaries

- Keep the shared Go SDK in `sdkgo`.
- Keep every connector in its own Go module.
- Group a company's connectors below `connectors/<company>/...`.
- Make the first directory below `connectors/` equal `metadata.company`'s
  normalized company identity and provide its `logo.svg`.
- Give every connector its own `go.mod`, README, `connector.yaml`, generated Go
  file, provider tests, and any UI package.
- Register a connector directory in the sorted root `connectors.yaml` only when
  that directory is added, moved, or removed. A version-only change does not
  alter the registry.

## Manifest-first implementation

Treat `connector.yaml` as the release and code-generation source of truth for:

- company metadata and `metadata.version`;
- configuration and generated `Config`;
- auth fields and generated `Credentials`;
- Trigger, Query, Mutation, branch, retry, and execution definitions;
- operation-specific Step factories and defaults;
- Studio setup, commands, UI units, ports, and generated constants.

Run `connectorctl generate` after the manifest changes. Review generated code;
do not hand-edit it. Run the corresponding `--check` target before handoff.

Root `go test ./...` also runs `cmd/connectorctl/main_test.go`, which
hard-codes every registered connector's name and version plus every
operation's happy-path branch and durability. A version bump, new operation, or
branch or durability change fails
`TestCatalogLoadsRepositoryDirectoryRegistry` or
`TestRegisteredOperationsKeepOnlyHappyPathBranchesRequired` until you update
them in the same change (observed at connectors `main` `d975226`).

## New connector checklist

A new connector directory also updates:

- the sorted root `connectors.yaml` registry;
- the root `go.work` `use` list;
- `cmd/connectorctl/main_test.go`: connector count, names, versions,
  happy-branch map, and the `sync` durability allowlist;
- `cmd/connectorctl/catalog_test.go`: connector count;
- `docs/architecture.md` and `docs/acceptance.md`.

The release matrix is computed from the registry. There is no release-workflow
choice list to regenerate.

## Versions and release order

`metadata.version` is the connector release source of truth. Leaving it
unchanged deliberately defers a release. A declared version must equal the
latest tag or the next patch, minor, or major version; first releases use
`v0.1.0`. In v0, a new operation or configuration field is a minor bump.
Confirm the computed release with
`go run ./cmd/connectorctl release-matrix --registry connectors.yaml`.

SDK tags use `sdkgo/vX.Y.Z`. Connector tags use the module directory, for
example `connectors/slack/vX.Y.Z`. Pin only an exact published SDK tag in a
connector `go.mod`.

When discovery exposes an SDK contract gap:

1. develop SDK and connector together with `go.work` or a temporary local
   `replace`;
2. run the full connector verification against that local SDK;
3. remove the replacement;
4. open, merge, and release the SDK PR;
5. open a later connector PR pinned to the exact new SDK release.

Never publish a branch, pseudo-version, commit SHA, or replacement. Before
release, test every module with `GOWORK=off`. Connector releases run after merge
to `main`; manual release runs only recover incomplete releases and catalog
deployment.

A v0 breaking release cannot be a patch. A v1+ breaking release requires a
major-version module-path migration before release. Put the exact lowercase
token `(breaking)` in the PR title or body and final commit subject for every
public breaking change.

## PR shape

Prefer one released module per PR. Use repository commit scopes:

- `sdkgo: ...`
- `connector(<name>): ...`
- `connector(<company>/<name>): ...`
- `tooling: ...`
- `docs: ...`

The PR explains the provider public API or official SDK used, capability and
failure semantics, version change, example, tests, live-test status, security
boundary, and any follow-up release dependency. Do not merge the PR on the
user's behalf unless explicitly authorized.

## Fixed immutable reference snapshot

The public examples used by this skill are validated against the immutable
`connectors/slack/v0.9.0` repository snapshot. At that snapshot the exact
published component versions are:

- Connector SDK `sdkgo/v0.8.0`;
- Slack `connectors/slack/v0.9.0`;
- Gmail `connectors/google/gmail/v0.10.0`;
- Google Sheets `connectors/google/spreadsheet/v0.7.0`.

These are reference baselines, not permission to downgrade a repository. The
snapshot deliberately trails current releases until a reviewed baseline
refresh. For new work, inspect the official repository's current `main` and the
latest published component tag, for example
`git tag -l 'connectors/slack/v*' --sort=-v:refname | head -1`. If a required
tag is absent or its release failed, stop and report the release blocker; never
substitute a branch, pseudo-version, or commit SHA in public guidance.
