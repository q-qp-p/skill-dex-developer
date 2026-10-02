# Dex Skills bundle baselines

Use these immutable release tags when the loaded Skill needs to inspect the
reference sources packaged with this Dex Skills release. Project dependencies
and lockfiles remain authoritative for application code.

```text
DEX_BASELINE=sdk-go/v1.2.1
DEX_SERVER_BASELINE=server/v1.3.0
DEX_CLI_BASELINE=cli-v1.4.2
TEMPLATE_BASELINE=v1.9.4
```

These values mirror the release metadata at the Dex Skills repository root.
The package validator rejects any drift between the two copies.

The SDK API baseline is v1.2.1 across Go, Python, TypeScript, Java, and Rust.
The example dependency manifests retained at this source tag still select SDK
v0.13.0; they are source examples, not the API-version authority for the v1.2.1
error names. For a new project, select the released SDK version deliberately.
For an existing project, inspect its installed SDK and lockfile before applying
precise syntax or changing dependencies.
