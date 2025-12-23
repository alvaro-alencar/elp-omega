package main

import (
    "crypto/hmr"
    "crypto/sha256"
    "encoding/base64"
    "fmt"
    "sync"
    "sync/atomic"
    "time"
)

// Reality define as camadas de resposta do sistema
type Reality int

const (
    RealityPrime Reality = iota
    RealityMirror
    RealityShadow
)

// Constantes de Permissão (Baseadas em Fibonacci)
const (
    PermRead   = 1
    PermWrite  = 2
    PermExec   = 3
    PermAdmin  = 5
    PermSecure = 21
)

type SecureRequest struct {
    ZeckendorfMask int
    Seal           string
    Context        string
    Timestamp      int64
    Path           string
    Nonce          string
}

type EntangledLogicOmega struct {
    secret      []byte
    maxAgeMs    int64
    maxFailures int32
    usedNonces  sync.Map // map[string]int64
    failures    sync.Map // map[string]*int32
}

func NewELP(secret []byte) *EntangledLogicOmega {
    elp := &EntangledLogicOmega{
        secret:      secret,
        maxAgeMs:    300000,
        maxFailures: 5,
    }
    go elp.cleanupNonces()
    return elp
}

// isValidZeckendorfMask verifica se não há bits adjacentes (a mágica do protocolo)
func (e *EntangledLogicOmega) isValidZeckendorfMask(mask int) bool {
    if mask < 0 {
        return false
    }
    // (mask & (mask >> 1)) == 0 garante que não há bits 1 consecutivos
    return (mask & (mask >> 1)) == 0
}

func (e *EntangledLogicOmega) ProcessRequest(req SecureRequest, realData string, fingerprint string) (string, Reality) {
    // 1. Validação da Máscara (Zeckendorf Constraint)
    if !e.isValidZeckendorfMask(req.ZeckendorfMask) {
        return e.generateShadow(realData, req.Context, req.Path), RealityShadow
    }

    // 2. Freshness Check
    now := time.Now().UnixMilli()
    if now-req.Timestamp > e.maxAgeMs {
        return e.sanitize(realData), RealityMirror
    }

    // 3. HMAC Validation (Seal)
    expectedSeal := e.computeSeal(req)
    if req.Seal != expectedSeal {
        return e.handleFailure(fingerprint, realData)
    }

    // 4. Anti-Replay (Nonce)
    if _, loaded := e.usedNonces.LoadOrStore(req.Nonce, now); loaded {
        return e.generateShadow(realData, req.Context, req.Path), RealityShadow
    }

    return "PRIME_REALITY: " + realData, RealityPrime
}

func (e *EntangledLogicOmega) computeSeal(req SecureRequest) string {
    h := hmac.New(sha256.New, e.secret)
    payload := fmt.Sprintf("%d|%s|%d|%s|%s", req.ZeckendorfMask, req.Context, req.Timestamp, req.Path, req.Nonce)
    h.Write([]byte(payload))
    return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

func (e *EntangledLogicOmega) handleFailure(fp string, data string) (string, Reality) {
    val, _ := e.failures.LoadOrStore(fp, new(int32))
    countPtr := val.(*int32)
    count := atomic.AddInt32(countPtr, 1)

    if count > e.maxFailures {
        return "SHADOW_VAULT_ID:" + e.generateShadow(data, "atk", "trap") + ":ENCRYPTED", RealityShadow
    }
    return e.sanitize(data), RealityMirror
}

func (e *EntangledLogicOmega) sanitize(data string) string {
    return "[MASKED DATA] - Reality Mirror"
}

func (e *EntangledLogicOmega) generateShadow(realData, ctx, path string) string {
    h := hmac.New(sha256.New, e.secret)
    seed := fmt.Sprintf("SHADOW|%s|%s|%d", path, ctx, len(realData))
    h.Write([]byte(seed))
    return base64.RawURLEncoding.EncodeToString(h.Sum(nil)[:8])
}

func (e *EntangledLogicOmega) cleanupNonces() {
    ticker := time.NewTicker(1 * time.Hour)
    for range ticker.C {
        now := time.Now().UnixMilli()
        e.usedNonces.Range(func(key, value interface{}) bool {
            if now-(value.(int64)) > 3600000 {
                e.usedNonces.Delete(key)
            }
            return true
        })
    }
}

func main() {
    elp := NewELP([]byte("secret-key"))

    // Exemplo de máscara válida: PermRead(1) e PermAdmin(5) 
    // Bits: 1 (idx 0) e 5 (idx 3). Binário: 1001 (Sem vizinhos)
    mask := 1 | (1 << 3) 

    req := SecureRequest{
        ZeckendorfMask: mask,
        Context:        "dashboard",
        Timestamp:      time.Now().UnixMilli(),
        Path:           "/api/data",
        Nonce:          "unique-uuid-1",
    }
    req.Seal = elp.computeSeal(req)

    res, reality := elp.ProcessRequest(req, "SENHA123", "ip-127-0-0-1")
    fmt.Printf("Reality: %v | Result: %s\n", reality, res)
}