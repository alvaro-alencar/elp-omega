# Análise de Segurança: Protocolo ELP-Ω

Este documento detalha as garantias de segurança e a resistência do Protocolo ELP-Ω contra vetores de ataque comuns.

## 1. Modelo de Ameaças e Mitigações

| Vetor de Ataque | Mecanismo de Proteção | Descrição Técnica |
| :--- | :--- | :--- |
| **Força Bruta no Selo** | HMAC-SHA256 | Utiliza uma chave secreta de 256 bits (keyspace de 2^256), tornando a falsificação computacionalmente inviável. |
| **Ataques de Replay** | Validação de Nonce | Cada requisição possui um identificador único (nonce) que é armazenado temporariamente. Requisições duplicadas são enviadas para a SHADOW reality. |
| **Ataques de Tempo** | Comparação em Tempo Constante | A validação do selo utiliza algoritmos que evitam fugas de informação baseadas no tempo de processamento. |
| **Escala de Privilégios** | Restrição de Zeckendorf | A assinatura topológica das máscaras (bits não-adjacentes) impede a ativação arbitrária de permissões sem quebrar a regra matemática. |
| **Roubo de Token/Sessão** | Expiração por Timestamp | As requisições têm uma janela de validade (default: 5 min). Tokens antigos resultam em MIRROR reality. |

## 2. A Defesa Ativa: Triple-Reality
Ao contrário de sistemas que apenas bloqueiam acessos (revelando a presença de segurança), o ELP-Ω utiliza a **decepção determinística**:
- **Shadow Reality:** Em caso de ataque confirmado (violação de bitmask ou replay), o sistema gera dados falsos mas consistentes.
- **Impacto Psicológico:** O atacante acredita ter tido sucesso, desperdiçando recursos na análise de dados sintéticos enquanto a equipa de defesa monitoriza o comportamento.

## 3. Recomendações de Implementação
- **Rotação de Segredos:** Recomenda-se a rotação da chave HMAC a cada 30 dias.
- **Armazenamento de Nonces:** Para ambientes de alta escala, deve utilizar-se uma base de dados em memória (como Redis) em vez de armazenamento local.