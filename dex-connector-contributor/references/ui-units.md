# Configuration UI units

Connector UI units are small reusable React TypeScript components composed by
Dex Web v2 for one Connector Step or Trigger binding configuration. They are
not Dex primitives and never receive credentials.

Read [connector configuration guidance](configuration-guidance.md) before
authoring a unit. Every rendered field needs provider-specific provenance and
blank behavior; use a verified claim or read-only picker instead of free text
when the provider can supply the value.

## Manifest and generated contract

Declare Studio Host API range `>=0.2.0 <0.3.0`, the setup entrypoint, exact
backend capability allowlist, provider commands, mock scenarios, and reusable
units in `connector.yaml`. Each unit has a stable lower-camel ID, generated Go
constant, named typed ports, description, and only the backend capabilities it
needs.

Dex Web composes static `ConnectorConfigurationUI` declarations from the Flow.
The SDK public types at the immutable baseline are:

<!-- connector-source: sdkgo/configuration_ui.go -->
```go
type ConnectorConfigurationUI struct {
    // Units lists reusable UI units in application composition order.
    Units []ConnectorUIUnit `json:"units" yaml:"units"`
}

// ConnectorUIUnit is one reusable unit from a Connector release's Studio unit
// catalog. Bindings connect the unit's named ports to configuration JSON paths.
type ConnectorUIUnit struct {
    // ID is the stable application-local identity of this unit use.
    ID string `json:"id" yaml:"id"`
    // UnitID identifies a unit in the connector's released UI catalog.
    UnitID string `json:"unitId" yaml:"unitId"`
    // Label is the application-facing unit label.
    Label string `json:"label" yaml:"label"`
    // Description explains how to choose or obtain the configured value.
    Description string `json:"description" yaml:"description"`
    // Required reports whether the application must configure this unit.
    Required bool `json:"required" yaml:"required"`
    // Bindings map unit ports to application-owned configuration paths.
    Bindings []ConnectorUIBinding `json:"bindings" yaml:"bindings"`
}

// ConnectorUIBinding maps one Connector UI unit port to an RFC 6901 JSON
// Pointer in the application-owned configuration object.
type ConnectorUIBinding struct {
    // Port names an input or output declared by the released unit.
    Port string `json:"port" yaml:"port"`
    // JSONPointer is an RFC 6901 path into application configuration.
    JSONPointer string `json:"jsonPointer" yaml:"jsonPointer"`
}
```

Source: [Connector configuration UI types at the immutable baseline](https://github.com/superdurable/dex-connectors-library/blob/connectors/slack/v0.11.0/sdkgo/configuration_ui.go).

Use generated unit and port constants rather than string copies. Every binding
maps one named port to an RFC 6901 JSON Pointer in the application-owned
configuration object. Keep declarations compile-time literal so the FDG 2.0
analyzer can validate the exact release's unit and port catalog.

## Host API 0.2 boundary

The iframe runs with an opaque origin. It communicates only through the
nonce-bound Host API 0.2 message protocol. It may request declared commands,
save its scoped non-secret configuration, and report bounded content height.
It does not fetch provider APIs directly, read connection files, receive stored
credential values, or choose arbitrary URLs.

Provider commands are a connector-release allowlist. The host injects the named
credential, permits HTTPS only, applies declared fixed/query/body mappings,
bounds redirects and responses, and rejects secret reflection. The UI handles
coded host/provider errors without logging sensitive response bodies.

Operation configuration is stored separately in non-secret
`use-configurations.json`. Load the connector store once at application
startup, then call `LoadOperationConfiguration[T]` with connector, connection,
operation, Flow type, and Step type identity. Use the returned `.Value` only
when mapping application state to provider input. Configuration changes require
an application restart; credential replacement remains visible to running
provider calls.

The released Slack Flow demonstrates generated constants and JSON Pointer
composition:

<!-- connector-source: connectors/slack/examples/thread-approval/flow/workflow.go -->
```go
ConfigurationUI: sdkgo.ConnectorConfigurationUI{Units: []sdkgo.ConnectorUIUnit{{
    ID: "completionText", UnitID: slack.UIUnitTextInput, Label: "Completion reply", Required: true,
    Description: "Enter the Slack message posted to the thread after the configured approval reply arrives.",
    Bindings:    []sdkgo.ConnectorUIBinding{{Port: slack.UITextInputPortText, JSONPointer: "/text"}},
}}},
```

Source: [Slack operation configuration composition at the immutable baseline](https://github.com/superdurable/dex-connectors-library/blob/connectors/slack/v0.11.0/connectors/slack/examples/thread-approval/flow/workflow.go).

## UI/UX acceptance

Test the unit inside Dex Web **Connections**, not only in Storybook or a direct
iframe. Verify:

- every example authorization, operation, and Trigger field is enumerated;
- provider start links, exact page paths, format, units, secrecy, and blank
  behavior are visible where the user needs them;
- safe manifest defaults render as parenthetical guidance without duplicated
  literal values in descriptions;
- verified claims and read-only picker outputs replace derivable free text;
- authorization and reauthorization;
- loading, empty, validation, expired/revoked, provider error, retry, and
  success states;
- keyboard and screen-reader labels, focus recovery, and responsive layout;
- bounded `connector.frame.resize` behavior without scroll traps;
- stable provider IDs displayed with human-readable labels and manual-ID
  fallback where appropriate;
- no credential, token, secret, authorization header, or provider secret body
  appears in iframe messages, DOM, logs, snapshots, or artifacts;
- saved configuration loads after Dex Web restart and takes effect after the
  application restarts.

Run unit tests and a production UI build. Also run manifest code generation,
FDG validation, local release override testing, and a real Connections setup
against the exact release metadata.
