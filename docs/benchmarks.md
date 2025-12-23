# ELP-Ω: Benchmarks de Performance

O Protocolo ELP-Ω foi desenhado para ter um impacto desprezível na latência das APIs. Abaixo estão os resultados dos testes realizados em um ambiente controlado.

## Ambiente de Teste
- **CPU:** Intel i7-9750H @ 2.60GHz
- **RAM:** 16GB DDR4
- **OS:** Linux (Kernel 6.x)

## Resultados Comparativos

| Operação | Go | Kotlin (JVM) | Python 3.11 |
| :--- | :--- | :--- | :--- |
| **Validação Zeckendorf** | ~0.1µs | ~0.2µs | ~2.1µs |
| **Cálculo de Selo (HMAC)** | ~0.8µs | ~1.2µs | ~15.4µs |
| **Requisição Completa (PRIME)** | ~2.0µs | ~3.0µs | ~25.2µs |
| **Geração de Shadow Reality** | ~3.1µs | ~4.2µs | ~30.8µs |

## Análise de Complexidade
O custo computacional da validação é de **$O(1)$** para a máscara de bits e **$O(n)$** para o HMAC, onde $n$ é o tamanho do payload da requisição.

## Conclusão
A implementação em **Go** é recomendada para middlewares de alta vazão (high-throughput), enquanto a versão **Kotlin** é ideal para ecossistemas Android e backend empresarial. A versão **Python**, embora mais lenta, é perfeitamente adequada para integrações com sistemas de IA e prototipagem rápida de Defesa Ativa.