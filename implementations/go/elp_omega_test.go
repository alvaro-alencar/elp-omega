package elpomega

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestZeckendorfValidation(t *testing.T) {
	elp := NewELP([]byte("test-secret"))

	tests := []struct {
		name  string
		mask  int
		valid bool
	}{
		{"valid non-adjacent 1001", 0b1001, true},
		{"valid non-adjacent 10001", 0b10001, true},
		{"invalid adjacent 11", 0b11, false},
		{"invalid adjacent 110", 0b110, false},
		{"valid single bit", 0b1, true},
		{"valid zero", 0, true},
		{"invalid negative", -1, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result := elp.isValidZeckendorfMask(tt.mask)
			assert.Equal(t, tt.valid, result)
		})
	}
}

func TestHMACAuthentication(t *testing.T) {
	secret := []byte("super-secret-key")
	elp := NewELP(secret)

	req := SecureRequest{
		ZeckendorfMask: 1,
		Context:        "test",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api/test",
		Nonce:          "test-nonce-123",
	}

	// Compute valid seal
	req.Seal = elp.computeSeal(req)

	// Should succeed
	result, reality := elp.ProcessRequest(req, "REAL_DATA", "test-client")
	assert.Equal(t, RealityPrime, reality)
	assert.Contains(t, result, "PRIME_REALITY")

	// Tamper with seal
	req.Seal = "invalid-seal"
	result, reality = elp.ProcessRequest(req, "REAL_DATA", "test-client")
	assert.NotEqual(t, RealityPrime, reality)
	assert.NotContains(t, result, "REAL_DATA")
}

func TestNonceReplayProtection(t *testing.T) {
	elp := NewELP([]byte("secret"))

	nonce := "replay-test-nonce"
	req := SecureRequest{
		ZeckendorfMask: 1,
		Context:        "test",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api/test",
		Nonce:          nonce,
	}
	req.Seal = elp.computeSeal(req)

	// First request: should succeed
	result1, reality1 := elp.ProcessRequest(req, "DATA", "client")
	assert.Equal(t, RealityPrime, reality1)

	// Second request with same nonce: should fail (replay)
	result2, reality2 := elp.ProcessRequest(req, "DATA", "client")
	assert.Equal(t, RealityShadow, reality2)
	assert.NotEqual(t, result1, result2)
}

func TestTimestampExpiration(t *testing.T) {
	elp := NewELP([]byte("secret"))

	// Expired timestamp (1 hour ago)
	oldTime := time.Now().Add(-1 * time.Hour).UnixMilli()
	req := SecureRequest{
		ZeckendorfMask: 1,
		Context:        "test",
		Timestamp:      oldTime,
		Path:           "/api/test",
		Nonce:          "test-nonce",
	}
	req.Seal = elp.computeSeal(req)

	result, reality := elp.ProcessRequest(req, "SENSITIVE_DATA", "client")
	assert.Equal(t, RealityMirror, reality)
	assert.NotContains(t, result, "SENSITIVE_DATA")
}

func TestRateLimiting(t *testing.T) {
	elp := NewELP([]byte("secret"))
	elp.maxFailures = 3

	fingerprint := "attacker-ip"

	// Simulate multiple failed attempts
	for i := 0; i < 5; i++ {
		req := SecureRequest{
			ZeckendorfMask: 1,
			Context:        "test",
			Timestamp:      time.Now().UnixMilli(),
			Path:           "/api/test",
			Nonce:          string(rune(i)), // Different nonce each time
			Seal:           "INVALID_SEAL",
		}

		result, reality := elp.ProcessRequest(req, "DATA", fingerprint)

		if i < 3 {
			// First 3 failures: MIRROR
			assert.Equal(t, RealityMirror, reality)
		} else {
			// After threshold: SHADOW
			assert.Equal(t, RealityShadow, reality)
			assert.Contains(t, result, "SHADOW_VAULT_ID")
		}
	}
}

func TestDeterministicShadowData(t *testing.T) {
	elp := NewELP([]byte("secret"))

	req := SecureRequest{
		ZeckendorfMask: 0b11, // Invalid: adjacent bits
		Context:        "test",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api/test",
		Nonce:          "test",
	}
	req.Seal = elp.computeSeal(req)

	// Generate shadow data twice
	result1, _ := elp.ProcessRequest(req, "REAL_DATA", "client")
	
	// Reset nonce to allow second request
	req.Nonce = "test2"
	req.Seal = elp.computeSeal(req)
	result2, _ := elp.ProcessRequest(req, "REAL_DATA", "client")

	// Shadow data should be deterministic (same for same inputs)
	assert.Equal(t, result1, result2)
}

func BenchmarkHMACComputation(b *testing.B) {
	elp := NewELP([]byte("benchmark-secret"))
	req := SecureRequest{
		ZeckendorfMask: 1,
		Context:        "bench",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api/bench",
		Nonce:          "bench-nonce",
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = elp.computeSeal(req)
	}
}

func BenchmarkZeckendorfValidation(b *testing.B) {
	elp := NewELP([]byte("secret"))
	mask := 0b1001

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = elp.isValidZeckendorfMask(mask)
	}
}

func BenchmarkFullRequestPrime(b *testing.B) {
	elp := NewELP([]byte("secret"))
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		req := SecureRequest{
			ZeckendorfMask: 1,
			Context:        "bench",
			Timestamp:      time.Now().UnixMilli(),
			Path:           "/api/bench",
			Nonce:          string(rune(i)),
		}
		req.Seal = elp.computeSeal(req)
		elp.ProcessRequest(req, "DATA", "client")
	}
}