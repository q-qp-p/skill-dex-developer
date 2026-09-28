# Dex Skills bundle baselines

Use these immutable release tags when the loaded Skill needs to inspect the
reference sources packaged with this Dex Skills release. Project dependencies
and lockfiles remain authoritative for application code.

```text
DEX_BASELINE=sdk-go/v0.13.1
DEX_SERVER_BASELINE=server/v0.13.2
DEX_CLI_BASELINE=cli-v0.13.8
TEMPLATE_BASELINE=v1.6.1
CONNECTOR_LIBRARY_BASELINE=connectors/slack/v0.9.0
```

These values mirror the release metadata at the Dex Skills repository root.
The package validator rejects any drift between the two copies.
