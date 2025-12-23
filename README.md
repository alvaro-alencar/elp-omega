# ELP-Ω: Entangled Logic Protocol - Omega

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Go](https://img.shields.io/badge/Go-1.21+-00ADD8?logo=go)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9+-7F52FF?logo=kotlin)
![Security](https://img.shields.io/badge/security-hardened-green)

*A cryptographic security architecture that uses triple-reality shifting and Fibonacci constraints to detect and deceive attackers while protecting real systems.*

[Features](#features) • [Quick Start](#quick-start) • [Architecture](#architecture) • [Implementations](#implementations) • [Benchmarks](#benchmarks) • [Contributing](#contributing)

</div>

---

## 🌀 What is ELP-Ω?

**ELP-Ω** (Entangled Logic Protocol - Omega) is a novel security architecture that combines:

- **Fibonacci Constraint Validation** (Zeckendorf-inspired non-adjacency)
- **HMAC-SHA256 Authentication** (AWS Signature V4-like)
- **Triple-Reality Response System** (Prime, Mirror, Shadow)
- **Deterministic Shadow Data Generation** (confuses attackers)
- **Anti-Replay Protection** (nonce validation)
- **Rate Limiting** (gradual degradation)

### Traditional Security vs ELP-Ω
```
┌─────────────────────────────────────────┐
│ TRADITIONAL:                            │
│ ❌ Valid   → 200 OK (real data)         │
│ ❌ Invalid → 403 Forbidden (obvious)    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ELP-Ω:                                  │
│ ✅ Valid   → 200 OK (PRIME reality)     │
│ ⚠️  Expired → 200 OK (MIRROR reality)   │
│ 🎭 Attack  → 200 OK (SHADOW reality)    │
└─────────────────────────────────────────┘
```

**Attackers receive fake data that LOOKS real, wasting their time while you monitor.**

---

## ✨ Features

### 🔒 **Fibonacci Permission System**
Uses non-adjacent bit positions (Zeckendorf theorem) to detect forced privileges:
```kotlin
// Valid: READ (1) + ADMIN (5) = indices 0 and 3 (non-adjacent)
val mask = 0b1001  // ✅ Valid

// Invalid: READ (1) + WRITE (2) = indices 0 and 1 (adjacent)
val mask = 0b0011  // ❌ Triggers SHADOW reality
```

### 🎭 **Triple-Reality System**

| Reality | When | Response |
|---------|------|----------|
| **PRIME** | Valid auth + fresh request | Real data |
| **MIRROR** | Valid auth + stale timestamp | Sanitized data |
| **SHADOW** | Invalid auth or attack detected | Fake data (HMAC-generated) |

### 🛡️ **Security Features**

- ✅ **HMAC-SHA256** authentication (impossible to forge without secret)
- ✅ **Nonce anti-replay** (prevents request reuse)
- ✅ **Timestamp validation** (5-minute default window)
- ✅ **Rate limiting** (gradual degradation after failures)
- ✅ **Constant-time comparison** (prevents timing attacks)
- ✅ **Deterministic shadows** (same attack = same fake data)

---

## 🚀 Quick Start

### Go Implementation
```go
package main

import (
    "github.com/yourusername/elp-omega/implementations/go"
    "time"
)

func main() {
    elp := elpomega.NewELP([]byte("your-secret-key"))
    
    // Build valid Fibonacci mask (non-adjacent)
    mask := 1 | (1 << 3)  // READ (bit 0) + ADMIN (bit 3)
    
    req := elpomega.SecureRequest{
        ZeckendorfMask: mask,
        Context:        "user-dashboard",
        Timestamp:      time.Now().UnixMilli(),
        Path:           "/api/data",
        Nonce:          "unique-uuid",
    }
    req.Seal = elp.ComputeSeal(req)
    
    result, reality := elp.ProcessRequest(req, "REAL_DATA", "client-ip")
    // reality = RealityPrime, RealityMirror, or RealityShadow
}
```

### Kotlin Implementation
```kotlin
val elp = EntangledLogicOmegaV5(
    secretProvider = { "your-secret-key".toByteArray() }
)

// Builder pattern for masks
val mask = elp.maskBuilder()
    .read()
    .admin()
    .secure()
    .build()

val req = EntangledLogicOmegaV5.SecureRequest(
    zeckendorfMask = mask,
    seal = computedSeal,
    context = "user-dashboard",
    timestamp = System.currentTimeMillis(),
    path = "/api/data",
    nonce = UUID.randomUUID().toString()
)

val result = elp.processRequest(req, "REAL_DATA", "client-fingerprint")
```

---

## 🏗️ Architecture
```
┌─────────────────────────────────────────────────────┐
│                 CLIENT REQUEST                      │
│  (mask + seal + timestamp + nonce + context)        │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  Fibonacci Validation   │
        │  (Non-adjacent check)   │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Timestamp Check       │
        │   (Freshness)           │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   HMAC Validation       │
        │   (Seal check)          │
        └────────────┬────────────┘
                     │
        ┌────────────▼────────────┐
        │   Nonce Anti-Replay     │
        │   (Prevent reuse)       │
        └────────────┬────────────┘
                     │
     ┌───────────────┴───────────────┐
     │                               │
┌────▼────┐  ┌────────┐  ┌──────────▼──┐
│  PRIME  │  │ MIRROR │  │   SHADOW    │
│  Real   │  │ Masked │  │ Fake (HMAC) │
└─────────┘  └────────┘  └─────────────┘
```

For detailed architecture, see [docs/architecture.md](docs/architecture.md)

---

## 📊 Benchmarks

| Operation | Go | Kotlin | Python |
|-----------|-----|--------|--------|
| **HMAC Computation** | ~0.8µs | ~1.2µs | ~15µs |
| **Fibonacci Validation** | ~0.1µs | ~0.2µs | ~2µs |
| **Full Request (PRIME)** | ~2µs | ~3µs | ~25µs |
| **Full Request (SHADOW)** | ~3µs | ~4µs | ~30µs |

*Tested on: Intel i7-9750H, 16GB RAM*

See [docs/benchmarks.md](docs/benchmarks.md) for detailed results.

---

## 🛠️ Implementations

### Production-Ready
- ✅ **Go** - High-performance server implementation
- ✅ **Kotlin** - Android/JVM implementation with lifecycle management

### Coming Soon
- 🔜 **Python** - Flask/FastAPI integration
- 🔜 **Rust** - Ultra-performance embedded systems
- 🔜 **JavaScript/TypeScript** - Node.js/Deno implementation

---

## 🔬 Security Analysis

### Threat Model

| Attack Vector | Protection |
|---------------|------------|
| **Brute-force seal** | HMAC-SHA256 (2^256 keyspace) |
| **Replay attacks** | Nonce validation |
| **Timing attacks** | Constant-time comparison |
| **Privilege escalation** | Fibonacci constraint |
| **Token theft** | Timestamp expiration |

See [docs/security-analysis.md](docs/security-analysis.md) for full analysis.

---

## 📖 Documentation

- [Architecture Overview](docs/architecture.md)
- [Fibonacci Constraint Math](docs/fibonacci-constraint.md)
- [Triple-Reality Concept](docs/triple-reality.md)
- [Security Analysis](docs/security-analysis.md)
- [Performance Benchmarks](docs/benchmarks.md)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

### Development Setup
```bash
# Clone repository
git clone https://github.com/yourusername/elp-omega.git
cd elp-omega

# Run tests (Go)
cd implementations/go
go test -v ./...

# Run tests (Kotlin)
cd implementations/kotlin
./gradlew test
```

---

## 📜 License

This project is licensed under the **MIT License** - see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

Inspired by:
- **Unix file permissions** (bitwise operations)
- **AWS Signature V4** (HMAC authentication)
- **Honeypot technology** (deception techniques)
- **Zeckendorf's theorem** (Fibonacci uniqueness)

---

## 📧 Contact

**Author:** Álvaro Alencar  
**Email:** [ac.alvaro@gmail.com]  
**LinkedIn:** [https://www.linkedin.com/in/adv-dev-alvaroalencar/]  
**WhatsApp:** [+55 (38) 9 9991-4890]

---

<div align="center">

**If you find this project useful, please ⭐ star it on GitHub!**

Made with 🌀 by the Vortex Development team

</div>