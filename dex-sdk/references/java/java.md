# Java handbook

Use this page first for Java application work. Then load the topic page that matches the task. The [baseline build](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/java/build.gradle) uses `io.superdurable:dex-sdk:0.13.0`, Spring Boot, and JDK 17 or newer. The application's Gradle or Maven lockfile remains authoritative.

## Project shape

Keep Flow and Step types in application packages, expose them as Spring beans, build one `Registry` from every Flow bean, and share one disk `BlobCache` between the `Worker` and `Client`. Inject business dependencies through constructors. Parameterized Step inputs are not supported directly; use a concrete holder class or an array.

The official example layout separates `products/`, `patterns/`, `primitives/`, and `shared/`. A smaller service normally needs `flows/`, `steps/`, `model/`, and a bootstrap/configuration class.

## Connector runtime support

The Connector local JSON loader and generated `NewLocalConnection` API are Go-only. Do not invent a Java loader or deserialize Dex Web's credential file into Flow state. For a Java application, keep provider credentials behind an application-owned secret/runtime adapter until an official Java Connector SDK exposes the same contract.

## Minimal Flow

[Pinned runnable source](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/java/src/main/java/io/superdurable/dex/primitives/flow/ExampleFlow.java)
<!-- dex-source: examples/java/src/main/java/io/superdurable/dex/primitives/flow/ExampleFlow.java -->
```java
@Component
public class ExampleFlow implements Flow<Integer> {
    public static final Attribute<String> status = Attribute.define("status", String.class);
    public static final Channel<Void> notify = Channel.define("notify", Void.class);

    private final ExampleStep exampleStep = new ExampleStep();
    private final Finish finishStep = new Finish();

    @Override
    public StepList<Integer> getSteps() {
        return StepList.startStep(exampleStep).otherSteps(finishStep);
    }

    @Override
    public PersistenceSchema getPersistenceSchema() {
        return PersistenceSchema.of(status, notify);
    }
```

A Flow returns its complete Step registry once. The first Step input type must match `Flow<I>`. All persisted definitions belong in `getPersistenceSchema()`.

[Pinned Step source](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/java/src/main/java/io/superdurable/dex/primitives/flow/ExampleFlow.java)
<!-- dex-source: examples/java/src/main/java/io/superdurable/dex/primitives/flow/ExampleFlow.java -->
```java
final class ExampleStep implements Step<Integer> {
    @Override
    public Class<Integer> getInputType() {
        return Integer.class;
    }

    @Override
    public Wait waitFor(final Context context, final Integer input) {
        status.set(context, "running");
        return Wait.skipImmediately();
    }

    @Override
    public StepDecision execute(final Context context, final Integer input) {
        return StepDecision.goTo(Finish.class, input + 1);
    }
}
```

## Registry, Worker, and Client

[Pinned bootstrap source](https://github.com/superdurable/dex/blob/sdk-go/v0.13.1/examples/java/src/main/java/io/superdurable/dex/config/DexConfig.java)
<!-- dex-source: examples/java/src/main/java/io/superdurable/dex/config/DexConfig.java -->
```java
@Bean
public Registry registry(final List<Flow<?>> flows) {
    return new Registry(new ArrayList<Flow<?>>(flows));
}

@Bean(destroyMethod = "close")
public BlobCache blobCache(
        @Value("${dex.blob-cache-dir}") final String blobCacheDir) {
    return BlobCache.open(new BlobCacheConfig(blobCacheDir, 1L << 30));
}
```

Create the Worker before the Client so the Client can use `worker.getWorkerTarget()`. Start the blocking Worker on a managed thread and close Worker, Client, and BlobCache during application shutdown. Do not create a cache per request.

Add `io.superdurable:dex-sdk:<resolved-version>` to Gradle or Maven. Application adapters call the injected Client to start a registered Flow, invoke typed RPC stubs for Flow-owned state, wait for Attribute matches, or wait for terminal status.

## Run locally

```bash
dexcli dev
cd examples/java
./gradlew bootRun
```

Use `./run-integration-tests.sh` for the official application suite. Defaults connect to `localhost:8801`; configure the server address, Worker bind/target, and cache directory with the example environment variables.

## Continue reading

- [Primitives](primitives.md) for application building blocks.
- [Patterns](patterns.md) before selecting a Flow shape.
- [Errors](error-handling.md) before writing Client, admission, RPC, cleanup, wait, or external Stream boundaries.
- [Testing](testing.md) before declaring durable behavior complete.
- [Data](data-handling.md), [observability](observability.md), and [versioning](versioning.md) for production behavior.
- [Gotchas](gotchas.md) and [advanced features](advanced-features.md) for constraints that are easy to miss.
