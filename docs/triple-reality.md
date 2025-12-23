# A Filosofia das Três Realidades (Triple-Reality)

O ELP-Ω v5 rompe com a segurança binária tradicional. Em vez de uma barreira estática, ele cria um ecossistema de respostas adaptativas baseado no nível de confiança da requisição.

## 1. PRIME Reality (A Singularidade da Verdade)
A camada **PRIME** representa o estado de integridade absoluta. 
- **Objetivo:** Entrega de dados puros para utilizadores legítimos.
- **Garantia:** Só é alcançada quando a Máscara de Zeckendorf, o Selo HMAC, o Timestamp e o Nonce são validados com sucesso.
- **Significado Teórico:** É o núcleo da "Verdade Algorítmica".

## 2. MIRROR Reality (A Verdade Fragmentada)
A camada **MIRROR** atua como uma zona de amortecimento para falhas não-críticas (ex: rede instável, relógios dessincronizados ou degradação de sessão).
- **Mecanismo:** Sanitização dinâmica via Regex.
- **Estratégia:** Em vez de negar o serviço (causando atrito), o sistema entrega uma versão "segura" dos dados.
- **Utilidade:** Previne a fuga de PII (Personally Identifiable Information) sem interromper o fluxo de trabalho do utilizador real.

## 3. SHADOW Reality (A Verdade Sintética)
A camada **SHADOW** é a peça central da nossa Defesa Ativa.
- **Mecanismo:** Geração de dados falsos determinísticos baseados em `HMAC(Secret, Seed)`.
- **Propósito:** Enganar o agressor. Ao receber dados que *parecem* reais e consistentes, o atacante entra num loop de análise de lixo (garbage analysis).
- **Vantagem Estratégica:** Transfere o custo do ataque para o agressor. Enquanto ele gasta computação a processar sombras, o sistema real permanece invisível.