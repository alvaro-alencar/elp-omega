# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

**DO NOT** open a public issue for security vulnerabilities.

Instead, please report security issues to: **security@vortex.dev**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within **48 hours** and provide a timeline for a fix.

## Security Features

ELP-Ω is designed with security in mind:

- ✅ HMAC-SHA256 authentication (256-bit keyspace)
- ✅ Constant-time comparison (timing attack resistant)
- ✅ Nonce anti-replay protection
- ✅ Timestamp validation (prevents replay)
- ✅ Rate limiting (brute-force protection)
- ✅ Fibonacci constraint (privilege escalation detection)
- ✅ Triple-reality system (attacker deception)

## Known Limitations

1. **Secret Management**: You MUST rotate secrets regularly (recommended: 30 days)
2. **Nonce Storage**: In-memory nonces are lost on restart (use Redis for production)
3. **Rate Limiting**: Per-fingerprint only (use reverse proxy for IP-based limits)

## Best Practices

### Secret Generation
```bash
# Generate strong secret (32 bytes)
openssl rand -base64 32
```

### Secret Rotation
```go
// Implement secret rotation every 30 days
secretProvider := func() []byte {
    return vault.GetCurrentSecret() // Fetch from secure vault
}
```

### Production Deployment
- Use TLS 1.3+ for all communications
- Store secrets in secure vault (AWS Secrets Manager, HashiCorp Vault)
- Enable request logging with PII redaction
- Monitor shadow reality triggers (potential attacks)
- Set up alerts for rate limit hits

## Security Audits

- **v1.0.0**: Self-audited (Dec 2024)
- External audit: Planned for Q1 2025

## Hall of Fame

We recognize security researchers who responsibly disclose vulnerabilities:

*No vulnerabilities reported yet.*

---

For urgent security matters: **security@vortex.dev**