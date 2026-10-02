# Template stack authority and repository bootstrap

Inspect the repository before selecting a language, creating manifests, or
installing dependencies. Treat a repository as effectively empty when it has no
application source or build manifests, even if it contains a README, license,
editor configuration, or other project placeholders.

For an effectively empty repository, initialize the application from
`https://github.com/superdurable/dex-template-basic-process` at the exact release
recorded in the [bundle baselines](../../dex-sdk/references/core/bundle-baselines.md).
Materialize the template
inside the current repository while preserving its `.git` directory and any
intentional user files. Review collisions before writing, do not initialize or
read project-local agent-skill submodules, inspect `.superverse/template.json`,
and use `make bootstrap` as the first dependency/bootstrap command. The
installed Dex Skills release loaded by the current coding-agent host is the
only skill authority. In Superverse Coding Sandbox, the runtime supplies that
release. External developers install the released plugin in Codex, Claude Code,
Cursor, or another Agent Skills-compatible host. Never assume a fixed skill
filesystem path.

For a new or effectively empty application, `TEMPLATE_BASELINE` is the
application stack authority. Before proposing implementation, inspect that
immutable template release's `go.mod`, `go.sum`, `web/package.json`,
`web/package-lock.json`, `DEX_SERVER_BASELINE`, `DEX_CLI_BASELINE`, Makefile,
`.superverse/template.json`, and `dex-app.yaml`. Preserve their exact languages,
module and package versions, lockfiles, generated-code tools, directory layout,
and bootstrap/test commands unless the user explicitly requests a stack or
version change. Keep every Flow source and static connector connection in
`dex-app.yaml`; never put configuration values or credentials there.

In the first implementation update for an effectively empty repository, name
the pinned template release and state that its Go backend and exact dependency
pins will be used. If the template release cannot be inspected or materialized,
report that blocker; do not fall back to a self-selected stack or install any
dependencies.

`DEX_BASELINE`, `DEX_SERVER_BASELINE`, and `DEX_CLI_BASELINE` in this skill
repository pin reference documentation and capability validation. They do not
authorize upgrading an application's template-pinned dependencies or runtime
baselines. Do not select a newer Dex Go SDK independently, run an upgrade
because a registry has a newer version, or copy versions from another project.

Do not invent a new application stack for an empty repository. In particular,
do not start a TypeScript Dex backend. Do not start a Node Dex backend, create
an ad hoc npm application, infer SDK versions from a neighboring workspace, or
copy bootstrap code from another project. TypeScript is limited to the
template's optional React frontend and generated client. The Dex backend and
application-side Connector SDK integration are Go-only.

If the user explicitly requests a non-template stack or dependency upgrade,
explain the compatibility and verification consequences before editing. A
non-Go backend is outside the Dex App Builder and Dex AI Platform path and
cannot use the current Connector SDK. Route an explicitly requested standalone
non-Go Dex application through `dex-sdk`; do not imply that Go-only Connector
capabilities remain available.

When the repository already contains an application and build manifests,
preserve its intentional structure rather than silently replacing it. Compare
it with the pinned template. If it is not compatible with the Go-only platform
and Connector boundary, stop before implementation and ask whether to adopt the
template stack or continue as an explicitly requested standalone SDK project.
