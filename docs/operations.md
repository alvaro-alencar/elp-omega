# ELP-Ω: Manual de Operações e Monitoria

Este documento descreve as rotinas necessárias para manter a integridade da Defesa Ativa e como interpretar os sinais do sistema.

## 1. Monitoria Estratégica (Prompt para IA)
Utilize o prompt abaixo em sua ferramenta de análise de logs (ou envie para o modelo de IA da Vortex) para identificar padrões de ataque.

> **Prompt: Analista de Segurança ELP-Ω**
> "Atua como o monitor de segurança do Protocolo ELP-Ω. Analisa os logs de entrada e identifica padrões onde a `SHADOW_REALITY` foi acionada. Classifica os incidentes em:
> 1. **Violação de Adjacência:** Tentativa provável de injeção de privilégios via Fibonacci.
> 2. **Replay Attack:** Tentativa de reutilização de nonce detetada.
> 3. **Seal Mismatch:** Falha crítica de autenticação ou tentativa de brute-force no HMAC.
> 
> Para cada alerta, gera um resumo determinístico do `fingerprint` do atacante e sugere se o IP deve ser movido para uma lista de observação ou se a semente da Shadow Reality deve ser rotacionada."

## 2. Rotinas de Manutenção
Para garantir que o "labirinto" de sombras continue eficaz, siga este calendário:

- **A cada 30 dias:** Rotacionar o `SECRET_KEY` (Chave Mestra HMAC).
- **A cada 15 dias:** Alterar a `STABILITY_SEED` (Semente da Shadow Reality). Isso muda os dados falsos que o atacante recebe, impedindo que ele mapeie a simulação a longo prazo.
- **Semanalmente:** Auditar logs de `MIRROR_REALITY` para identificar utilizadores legítimos com problemas de sincronização de relógio (Timestamp drift).

## 3. Resposta a Incidentes
Ao detetar um pico de acessos em `SHADOW_REALITY`:
1. Não bloqueie o IP imediatamente (deixe-o gastar recursos na sombra).
2. Monitorize se o atacante altera o comportamento ao receber os dados falsos.
3. Se o ataque persistir, altere o mapeamento dos bits de Fibonacci (ex: READ passa do Bit 0 para o Bit 2).