package elpomega

import (
	"encoding/base64"
	"strings"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestZeckendorfValidation(t *testing.T) {
	elp := NewELP([]byte("test-secret"))

	// 9 = 1001 (Ok)
	assert.True(t, elp.isValidZeckendorfMask(9), "Read + Admin deve ser válido")
	// 3 = 0011 (Fail - Adjacente)
	assert.False(t, elp.isValidZeckendorfMask(3), "Read + Write deve ser inválido")
}

func TestPrimeRealityFlow(t *testing.T) {
	secret := []byte("vortex-secret")
	elp := NewELP(secret)

	req := SecureRequest{
		ZeckendorfMask: 9,
		Context:        "ctx",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api",
		Nonce:          "unique-123",
	}
	req.Seal = elp.ComputeSeal(req)

	result, reality := elp.ProcessRequest(req, "DATA", "fp")
	
	assert.Equal(t, RealityPrime, reality)
	assert.Contains(t, result, "PRIME_REALITY")
}

func TestShadowRealityOnReplay(t *testing.T) {
	elp := NewELP([]byte("secret"))
	req := SecureRequest{
		ZeckendorfMask: 9,
		Context:        "ctx",
		Timestamp:      time.Now().UnixMilli(),
		Path:           "/api",
		Nonce:          "replay-nonce",
	}
	req.Seal = elp.ComputeSeal(req)

	// 1ª vez: OK
	elp.ProcessRequest(req, "DATA", "fp")
	
	// 2ª vez: Replay -> Shadow
	res2, r2 := elp.ProcessRequest(req, "DATA", "fp")
	assert.Equal(t, RealityShadow, r2)
	assert.Contains(t, res2, "SHADOW_VAULT_ID")
}

func TestShadowFormat(t *testing.T) {
	elp := NewELP([]byte("s"))
	shadow := elp.generateShadow("d", "c", "p")
	
	// Verifica se é URL Safe Base64
	_, err := base64.RawURLEncoding.DecodeString(shadow)
	assert.NoError(t, err)
	assert.False(t, strings.Contains(shadow, "+"))
}