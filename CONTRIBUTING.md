# Contributing to ELP-Ω

First off, thank you for considering contributing! 🎉

## Code of Conduct

Be respectful, inclusive, and constructive. This is a welcoming space for everyone.

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, language version, etc.)

### Suggesting Features

Open an issue with:
- Use case description
- Proposed solution
- Alternative approaches considered

### Submitting Code

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feature/amazing-feature`
3. **Make changes**: Follow coding standards
4. **Test**: Ensure all tests pass
5. **Commit**: `git commit -m 'Add amazing feature'`
6. **Push**: `git push origin feature/amazing-feature`
7. **Pull Request**: Open a PR with clear description

## Development Setup

### Go
```bash
cd implementations/go
go mod download
go test ./...
```

### Kotlin
```bash
cd implementations/kotlin
./gradlew test
```

## Coding Standards

### Go
- Follow [Effective Go](https://golang.org/doc/effective_go)
- Run `gofmt` before committing
- Add tests for new features
- Document public APIs

### Kotlin
- Follow [Kotlin Style Guide](https://kotlinlang.org/docs/coding-conventions.html)
- Use meaningful variable names
- Add KDoc for public functions
- Maintain test coverage > 80%

## Commit Message Format
```
type(scope): brief description

Detailed explanation (optional)

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement

**Examples:**
```
feat(go): add metrics collection
fix(kotlin): prevent nonce collision
docs(readme): update quick start guide
```

## Testing

All contributions must include tests:
```go
// Go example
func TestZeckendorfValidation(t *testing.T) {
    elp := NewELP([]byte("test"))
    // Valid: non-adjacent bits
    assert.True(t, elp.isValidZeckendorfMask(0b1001))
    // Invalid: adjacent bits
    assert.False(t, elp.isValidZeckendorfMask(0b0011))
}
```
```kotlin
// Kotlin example
@Test
fun `should reject adjacent Fibonacci permissions`() {
    val elp = EntangledLogicOmega(secretProvider = { "test".toByteArray() })
    // Should throw exception for adjacent indices
    assertThrows<IllegalArgumentException> {
        elp.maskBuilder().read().write().build()
    }
}
```

## Documentation

Update relevant docs:
- `README.md` for user-facing changes
- `docs/` for architecture/design changes
- Inline comments for complex logic

## Questions?

Open a discussion or reach out: **opensource@vortex.dev**

---

Thank you for contributing! 🌀