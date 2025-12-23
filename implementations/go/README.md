# ELP-Ω Go Implementation

High-performance Go implementation of the Entangled Logic Protocol.

## Installation
```bash
go get github.com/yourusername/elp-omega/implementations/go
```

## Quick Start
```go
package main

import (
    "fmt"
    "time"
    elp "github.com/yourusername/elp-omega/implementations/go"
)

func main() {
    engine := elp.NewELP([]byte("your-secret-key"))
    
    // Build Fibonacci mask (non-adjacent)
    mask := 1 | (1 << 3) // READ (bit 0) + ADMIN (bit 3)
    
    req := elp.SecureRequest{
        ZeckendorfMask: mask,
        Context:        "dashboard",
        Timestamp:      time.Now().UnixMilli(),
        Path:           "/api/data",
        Nonce:          "unique-uuid",
    }
    req.Seal = engine.ComputeSeal(req)
    
    result, reality := engine.ProcessRequest(req, "REAL_DATA", "client-ip")
    fmt.Printf("Reality: %v, Result: %s\n", reality, result)
}
```

## Testing
```bash
go test -v ./...
go test -race ./...
go test -cover ./...
```

## Benchmarks
```bash
go test -bench=. -benchmem
```

## Performance

| Operation | Time | Allocations |
|-----------|------|-------------|
| HMAC Seal | ~800ns | 1 alloc |
| Fibonacci Check | ~50ns | 0 alloc |
| Full Request (PRIME) | ~2µs | 3 allocs |

## Documentation

See [GoDoc](https://pkg.go.dev/github.com/yourusername/elp-omega/implementations/go)