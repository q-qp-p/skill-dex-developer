# Contributing

This repository publishes one plugin with three root-level skills:

- `dex-sdk` owns public Dex SDK implementation guidance and its Core and
  language references.
- `dex-app-builder` owns the business-first product workflow and platform-only
  constraints. It links to `dex-sdk` instead of copying SDK references.
- `dex-connector-contributor` is the thin bootstrap for official
  connector-library work. It resolves the checkout and then follows that
  repository's rules, while linking to `dex-sdk` Core/Go when needed.

Keep every retained reference reachable from its skill entrypoint. Connector
Contributor intentionally has no supporting references because the target
repository owns that guidance. Do not add a `plugins/` wrapper, a backend
companion skill, or duplicated Core/Go handbooks.

## Pin source authority

`DEX_BASELINE` pins exact SDK excerpts. Language code fences must be contiguous
excerpts from runnable examples, SDK tests, or SDK READMEs at that release, with
the existing visible source link and `dex-source` marker.

`DEX_SERVER_BASELINE` pins the released Server required by App Builder.
`DEX_CLI_BASELINE` pins the released local tooling and embedded Web v2/FDG 2.0
implementation. The Server release embeds the same Dex Web source for hosted
environments.
`TEMPLATE_BASELINE` pins the published release of the only supported
application template. Refresh any baseline deliberately and review all affected
guidance.

The scheduled **Update template baseline** workflow discovers a newer stable
template release, validates that it no longer vendors project-local skills,
bumps the plugin patch version and manifests, and opens a pull request. Its
merge publishes a matching Dex Skills release; Superverse then advances both
exact release pins together in its own reviewed pull request.

## Validate a change

Run from the repository root:

```bash
python3 script/check-package.py
python3 script/check-reference-sources.py --dex-root /path/to/dex-sdk-baseline
python3 script/check-upstream-baselines.py \
  --dex-root /path/to/dex-cli-baseline \
  --template-root /path/to/dex-template-basic-process
python3 /path/to/skill-creator/scripts/quick_validate.py dex-sdk
python3 /path/to/skill-creator/scripts/quick_validate.py dex-app-builder
python3 /path/to/skill-creator/scripts/quick_validate.py dex-connector-contributor
```

Also validate the Codex, Claude Code, and Cursor manifests with their current
client tooling and smoke-test that one plugin install exposes exactly the three
expected skills. Confirm App Builder and Connector Contributor resolve the
sibling `dex-sdk` Go handbook without copied references, and that Connector
Contributor routes implementation and acceptance to the target repository's
current instructions.

## Version and release

Every change under `dex-sdk/`, `dex-app-builder/`, or
`dex-connector-contributor/` updates `VERSION` and
`CHANGELOG.md`. Keep every plugin and marketplace manifest on that exact
version where the format supports a version.

- Increment PATCH for corrections and clarifications.
- Increment MINOR for new product workflows, languages, patterns, or other
  backward-compatible capabilities.
- Increment MAJOR for incompatible plugin or skill identity changes.

After a pull request lands on `main`, the Release workflow validates the full
package and creates `v<version>` from the matching changelog section. If the tag
already exists, the workflow skips release creation.
