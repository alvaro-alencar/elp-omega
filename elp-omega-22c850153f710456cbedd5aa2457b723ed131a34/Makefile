.PHONY: test-go test-kotlin test-python test-ts test-rust test-all

# Testes individuais
test-go:
	@echo "🌀 Testando implementação Go..."
	cd implementations/go && go test ./...

test-kotlin:
	@echo "🌀 Testando implementação Kotlin..."
	cd implementations/kotlin && ./gradlew test

test-python:
	@echo "🌀 Testando implementação Python..."
	python3 implementations/python/test_elp_omega.py

test-ts:
	@echo "🌀 Testando implementação TypeScript..."
	cd implementations/typescript && npm test

test-rust:
	@echo "🌀 Testando implementação Rust..."
	cd implementations/rust && cargo test

# Comando mestre para CI/CD
test-all: test-go test-kotlin test-python test-ts test-rust
	@echo "✅ Todas as realidades do ELP-Ω estão estáveis!"

# Ajuda
help:
	@echo "Comandos disponíveis:"
	@echo "  make test-all    - Executa testes em todas as linguagens"
	@echo "  make test-go     - Testa apenas a versão Go"
	@echo "  make test-python - Testa apenas a versão Python"