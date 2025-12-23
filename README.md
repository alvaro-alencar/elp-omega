# ELP-Ω (Entangled Logic Protocol - Omega)

> **"A segurança não é apenas negar o acesso; é controlar a natureza da realidade para o observador."**

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-100%25-success)
![Author](https://img.shields.io/badge/architect-Álvaro_Alencar-blue)

## 🏛 O Conceito (Segurança Ontológica)

O **ELP-Ω** não é apenas um firewall ou um validador de tokens. É uma implementação algorítmica do conceito de **Segurança Ontológica**, desenvolvida como parte de uma investigação doutoral sobre a integridade e a existência de dados em ambientes hostis.

A maioria dos sistemas de segurança opera no binário: *Acesso Permitido* ou *Acesso Negado*. O ELP-Ω introduz uma terceira via: a **Realidade Simulada**.

Ao utilizar a **Teoria de Zeckendorf** (soma de números de Fibonacci não-consecutivos) para validação de permissões em tempo constante O(1), o protocolo cria um labirinto matemático onde atacantes não são apenas bloqueados — eles são exilados para uma realidade sombra.

## 📐 A Matemática: Restrição de Zeckendorf

Diferente de bitmasks tradicionais, o ELP-Ω impõe uma restrição topológica nas permissões baseada na sequência de Fibonacci:

$$F_n = F_{n-1} + F_{n-2}$$

A regra fundamental do protocolo é que **nenhum bit de permissão adjacente pode estar ativo simultaneamente**.
`mask & (mask >> 1) == 0`

Isso impede vetores de ataque comuns baseados em "privilege escalation" sequencial e cria uma assinatura digital única para cada requisição.

## 🔮 Arquitetura "Triple-Reality"

O sistema decide qual versão da realidade entregar ao usuário baseando-se na integridade criptográfica da requisição:

1.  **PRIME REALITY:** O dado real, íntegro e descriptografado. Entregue apenas quando a Máscara Zeckendorf, o Timestamp e o HMAC-SHA256 são perfeitamente válidos.
2.  **MIRROR REALITY:** Uma versão sanitizada (mascarada) dos dados. Entregue quando há uma degradação benigna (ex: latência de rede ou relógio dessincronizado), mantendo a usabilidade sem expor o núcleo.
3.  **SHADOW REALITY:** O contra-ataque. Se uma violação da regra de Zeckendorf ou um *Replay Attack* é detectado, o sistema gera dados falsos, deterministicamente calculados, que parecem reais estruturalmente, mas são ontologicamente vazios. Isso consome recursos do atacante enquanto protege o sistema.

## ⚡ Implementações Poliglotas

Este repositório contém a prova de conceito e a implementação de referência do protocolo em 5 linguagens, validando sua universalidade:

| Linguagem | Status | Foco da Implementação |
| :--- | :--- | :--- |
| **Go** | ✅ Estável | Alta performance e concorrência (Backend Core) |
| **Rust** | ✅ Estável | Segurança de memória e Zero-Cost Abstraction |
| **Python** | ✅ Estável | Integração rápida e Prototipagem (Data Science) |
| **Kotlin** | ✅ Estável | Ecossistema JVM e Android |
| **TypeScript** | ✅ Estável | Aplicações Web e Edge Computing |

Todas as implementações foram validadas via containerização Docker com 100% de aprovação nos testes unitários de lógica e criptografia.

## 👨‍💻 Sobre o Autor

**Álvaro Alencar**
*Advogado, Desenvolvedor e Pesquisador.*

Este projeto é fruto de pesquisa independente na intersecção entre Direito Digital, Filosofia da Informação e Engenharia de Software. O objetivo é demonstrar que a segurança jurídica e a segurança computacional podem convergir em protocolos matematicamente robustos.

---
© 2025 Álvaro Alencar. Todos os direitos reservados.