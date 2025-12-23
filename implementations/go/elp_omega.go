package elp_omega

import (
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"hash/fnv"
	"math/rand"
	"sync"
	"time"
)

type Reality string

const (
	Prime  Reality = "PRIME"
	Mirror Reality = "MIRROR"
	Shadow Reality = "SHADOW"
)

type EntangledLogicOmega struct {
	secret      []byte
	maxAgeMs    int64
	usedNonces  map[string]int64
	mu          sync.Mutex
}

func New(secret string) *EntangledLogicOmega {
	return &EntangledLogicOmega{
		secret:     []byte(secret),
		maxAgeMs:   300000,
		usedNonces: make(map[string]int64),
	}
}

func (e *EntangledLogicOmega) IsValidZeckendorfMask(mask uint32) bool {
	return (mask & (mask >> 1)) == 0
}

func (e *EntangledLogicOmega) ComputeSeal(mask uint32, context string, timestamp int64, path, nonce string) string {
	payload := fmt.Sprintf("%d|%s|%d|%s|%s", mask, context, timestamp, path, nonce)
	h := hmac.New(sha256.New, e.secret)
	h.Write([]byte(payload))
	return hex.EncodeToString(h.Sum(nil))
}

// GenerateShadow cria dados bancários falsos baseados em seed determinística
func (e *EntangledLogicOmega) GenerateShadow(context, path, nonce string) map[string]interface{} {
	// Cria seed determinística
	seedStr := fmt.Sprintf("%s|%s|%s", path, context, nonce)
	h := fnv.New64a()
	h.Write([]byte(seedStr))
	seed := h.Sum64()

	r := rand.New(rand.NewSource(int64(seed)))

	// Dados sintéticos
	balance := 1000.0 + r.Float64()*(500000.0-1000.0)
	accType := "checking"
	if r.Float64() > 0.5 {
		accType = "savings"
	}

	return map[string]interface{}{
		"status":         "success",
		"transaction_id": fmt.Sprintf("tx-%d", r.Int63()), // Simplificado
		"timestamp":      time.Now().UnixMilli(),
		"data": map[string]interface{}{
			"account_type": accType,
			"balance":      balance,
			"currency":     "BRL",
			"flags":        []string{"verified", "secure"},
		},
		"meta": map[string]interface{}{
			"processing_time_ms": r.Intn(140) + 10,
			"region":             "sa-east-1",
		},
	}
}

// CheckReplay verifica nonces
func (e *EntangledLogicOmega) CheckReplay(nonce string) bool {
	e.mu.Lock()
	defer e.mu.Unlock()
	
	if _, exists := e.usedNonces[nonce]; exists {
		return true // É Replay
	}
	e.usedNonces[nonce] = time.Now().UnixMilli()
	return false
}