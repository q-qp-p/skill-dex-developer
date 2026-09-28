# Triggers

A Trigger is a long-running ingress adapter. It normalizes a provider event and
delivers it at least once to an application-owned typed target; it is not a
provider call performed by a Flow.

## Provider source contract

- Preserve a provider-stable event ID and occurrence time.
- Validate signatures or transport identity before accepting an event.
- Separate reusable connection credentials from binding matcher
  configuration.
- Call `PrepareTriggerDelivery` before acknowledging a matched provider event.
- Persist matched local delivery in a binding-specific inbox, replay it after
  restart, and remove it only after Dex accepts delivery.
- Document acknowledgement, retry, ordering, duplication, reconnect, and crash
  recovery behavior.

Do not let a source mutate Dex primitives directly. The source exposes a typed
provider-neutral event and calls a `TriggerTarget`.

## Application-owned routing

The application owns the final pure `TriggerFilter`, Flow ID resolution, and
typed input mapping. Provider matchers reduce traffic but are not the business
admission boundary. Filter tenant, channel, sender, text, authorization, and
required routing fields before resolving a Flow ID or calling Dex.

Choose a typed target:

- `NewDexFlowTriggerTarget` with a typed Flow and `FlowInputMapper` for root
  starts. The SDK derives the start Request ID from the provider event ID, and
  the resolved Flow ID owns root-event deduplication.
- `NewDexRPCTriggerTarget` with a registered bound RPC method and
  `RPCInputMapper` for an existing Flow. The application owns RPC options,
  bounded redelivery state, and locks for the exact business state or effect
  that must commit atomically.

Never configure a raw RPC-name string and never force an application RPC to
accept the provider event type.

The released Slack example wires both target forms in one durable runner:

<!-- connector-source: connectors/slack/examples/thread-approval/main.go -->
```go
triggerRunner, err := slack.NewLocalMessageTriggerRunner(store, threadapproval.ConnectionName, slack.LocalMessageTriggerRunnerConfig{
    ChannelThreadCreatedRoutes: []slack.LocalChannelThreadCreatedTriggerRoute{{
        BindingName: threadapproval.StartTriggerBinding,
        Target: sdkgo.NewDexFlowTriggerTarget(
            client, flow, startTriggerFilter, threadapproval.ResolveFlowID, threadapproval.MapToFlowInput,
            sdkgo.WithTriggerLogger(bindingLogger(
                logger, slack.ChannelThreadCreatedTriggerDefinition.Trigger.TriggerName, threadapproval.StartTriggerBinding,
            )),
        ),
    }},
    ThreadReplyCreatedRoutes: []slack.LocalThreadReplyCreatedTriggerRoute{{
        BindingName: threadapproval.ReplyTriggerBinding,
        Target: sdkgo.NewDexRPCTriggerTarget(
            client, flow.ReceiveThreadReply, replyTriggerFilter, threadapproval.ResolveFlowID,
            threadapproval.MapToReceiveThreadReplyInput,
            sdkgo.WithTriggerLogger(bindingLogger(
                logger, slack.ThreadReplyCreatedTriggerDefinition.Trigger.TriggerName, threadapproval.ReplyTriggerBinding,
            )),
        ),
    }},
}, slack.WithLogger(logger))
```

Source: [Slack thread approval runner at the immutable baseline](https://github.com/superdurable/dex-connectors-library/blob/connectors/slack/v0.11.0/connectors/slack/examples/thread-approval/main.go).

## Required verification

Exercise real Flow-start delivery, typed RPC delivery, irrelevant-event
consumption, duplicate event delivery, process restart before and after
provider acknowledgement, binding isolation, invalid configuration, and
transport reconnect. Prove the root start is deterministic and RPC dedup state
is bounded. Use deadline-based convergence rather than fixed sleeps.
