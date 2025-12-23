# ELP-Ω Kotlin Implementation

Kotlin/JVM implementation optimized for Android and server-side applications.

## Installation

### Gradle (Kotlin DSL)
```kotlin
dependencies {
    implementation("dev.vortex:elp-omega-kotlin:1.0.0")
}
```

### Gradle (Groovy)
```groovy
dependencies {
    implementation 'dev.vortex:elp-omega-kotlin:1.0.0'
}
```

## Quick Start
```kotlin
import dev.vortex.elpomega.EntangledLogicOmegaV5
import java.util.UUID

fun main() {
    val elp = EntangledLogicOmegaV5(
        secretProvider = { "your-secret-key".toByteArray() }
    )
    
    // Build mask with DSL
    val mask = elp.maskBuilder()
        .read()
        .admin()
        .secure()
        .build()
    
    val req = EntangledLogicOmegaV5.SecureRequest(
        zeckendorfMask = mask,
        seal = computeSeal(), // compute HMAC
        context = "user-dashboard",
        timestamp = System.currentTimeMillis(),
        path = "/api/data",
        nonce = UUID.randomUUID().toString()
    )
    
    val result = elp.processRequest(req, "REAL_DATA", "client-fp")
    println(result)
    
    elp.close() // Important: cleanup resources
}
```

## Android Usage
```kotlin
class SecureRepository(context: Context) {
    private val elp = EntangledLogicOmegaV5(
        secretProvider = { 
            // Fetch from Android Keystore
            KeyStoreManager.getSecret(context)
        },
        maxAgeMs = 300_000L
    )
    
    suspend fun fetchSecureData(): String = withContext(Dispatchers.IO) {
        val req = buildRequest()
        elp.processRequest(req, realData, getFingerprint())
    }
    
    fun cleanup() {
        elp.close()
    }
}
```

## Testing
```bash
./gradlew test
./gradlew test --tests "*ZeckendorfTest"
```

## Metrics
```kotlin
val metrics = elp.getMetrics()
println("Successful requests: ${metrics["successful_requests"]}")
println("Shadow triggers: ${metrics["reality.shadow"]}")
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| HMAC Seal | ~1.2µs | On Pixel 7 Pro |
| Fibonacci Check | ~0.2µs | Pure CPU |
| Full Request | ~3µs | Including validation |

## Documentation

See [KDoc](https://yourusername.github.io/elp-omega/kotlin/)