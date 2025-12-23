# A Restrição de Zeckendorf no ELP-Ω

O ELP-Ω utiliza uma implementação prática do **Teorema de Zeckendorf** para garantir a integridade das máscaras de permissão.

## 1. O Princípio da Não-Adjacência
O Teorema de Zeckendorf afirma que todo número inteiro positivo pode ser representado de forma única como a soma de números de Fibonacci não-consecutivos ($F_i$ onde $i \ge 2$).

No ELP-Ω, cada bit da máscara corresponde a um índice na sequência de Fibonacci:
- Index 0: Fib(1) = 1 (PERM_READ)
- Index 1: Fib(2) = 2 (PERM_WRITE)
- Index 2: Fib(3) = 3 (PERM_EXEC)
- Index 3: Fib(5) = 5 (PERM_ADMIN)

## 2. Implementação Bitwise O(1)
Para validar se um usuário tentou burlar o sistema ativando permissões "vizinhas" (o que indicaria tentativa de escalada de privilégios), utilizamos uma operação bitwise extremamente performática:

```go
// Se o bit n e o bit n+1 estiverem ativos, o resultado será != 0
isValid := (mask & (mask >> 1)) == 0