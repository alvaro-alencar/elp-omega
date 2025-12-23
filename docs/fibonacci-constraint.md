# A Restrição de Zeckendorf no ELP-Ω

O ELP-Ω utiliza uma implementação prática do **Teorema de Zeckendorf** para garantir a integridade das máscaras de permissão.

## 1. O Princípio da Não-Adjacência
O Teorema de Zeckendorf afirma que todo o número inteiro positivo pode ser representado de forma única como a soma de números de Fibonacci não-consecutivos. 

No ELP-Ω, cada bit da máscara corresponde a um índice na sequência de Fibonacci:
- PermRead = Index 0 (Fib 1)
- PermWrite = Index 1 (Fib 2)
- PermExec = Index 2 (Fib 3)
- PermAdmin = Index 3 (Fib 5)

## 2. Implementação Bitwise
Para validar se um utilizador não ativou permissões "vizinhas" (o que indicaria uma tentativa de brute-force de bits), utilizamos uma operação bitwise de custo O(1):

```go
// Se o bit n e o bit n+1 estiverem ativos, o resultado será != 0
isValid := (mask & (mask >> 1)) == 0