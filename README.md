# ELP-Ω: Zeckendorf Access Control Framework

![License](https://img.shields.io/badge/License-Apache%202.0%20%2B%20Commercial-blue)
![Version](https://img.shields.io/badge/Version-1.0.0-important)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue)

> **"Defesa cibernética através da indistinguibilidade ontológica."**

ELP-Ω (Omega) é um middleware de segurança de aplicação (L7) desenhado para proteger APIs críticas contra reconhecimento, scraping e ataques de repetição.

Ao contrário de firewalls tradicionais que bloqueiam ameaças (entregando status 403 Forbidden), o ELP-Ω utiliza uma arquitetura de **Realidade Sombras (Shadow Reality)**. Ataques detectados recebem respostas `200 OK` contendo dados sintéticos matematicamente gerados, indistinguíveis dos reais, prendendo o atacante num ciclo de análise falso.

A validação de integridade ocorre em tempo constante $O(1)$ utilizando o **Teorema de Zeckendorf** (restrição de adjacência de bits) combinado com criptografia HMAC.

---

## ⚡ Quick Start: Proteja a sua API

### Python (FastAPI)
```python
from fastapi import FastAPI
from implementations.python.elp_middleware import ElpOmegaMiddleware

app = FastAPI()
# Ativa o modo Stealth: Violações recebem dados bancários falsos
# A chave mestra deve ser mantida em segredo absoluto (HSM/Vault)
app.add_middleware(ElpOmegaMiddleware, secret_key="SUA_CHAVE_MESTRA")
```

### TypeScript (Express.js)
```typescript
import { elpOmegaMiddleware } from './implementations/typescript/elpMiddleware';
// Plug & Play protection
app.use(elpOmegaMiddleware('SUA_CHAVE_MESTRA'));
```

---

## ⚠️ Modelo de Ameaças (Threat Model)

O ELP-Ω atua na **Camada de Aplicação**. É crucial entender o seu escopo operacional para implantação segura:

✅ **Protege contra:** 
- Enumeration Attacks
- ID Scraping  
- Replay Attacks
- Fuzzing de API

🛡️ **Mitiga:**
- Timing Attacks (através de Jittering Aleatório na Shadow Reality)

🚫 **Não substitui:**
- Criptografia de transporte (TLS/SSL)
- Proteção contra DDoS Volumétrico (L3/L4)

🔐 **Requisito Crítico:** A segurança depende inteiramente do segredo da `SECRET_KEY`. Recomendamos rotação periódica.

---

## 🔮 Arquitetura: Stealth & Indistinguibilidade

O sistema gere o acesso através de **camadas de realidade**. O objetivo não é apenas negar o acesso, mas negar a informação de que o acesso foi negado.

### 1. **PRIME REALITY** (A Verdade)
- **Condição:** Máscara Zeckendorf Válida + HMAC Correto + Nonce Único
- **Resultado:** Dados reais são entregues
- **Latência:** Processamento natural da aplicação (ex: 20ms - 100ms)

### 2. **MIRROR REALITY** (Degradação Graciosa)
- **Condição:** Falha menor de integridade temporal (clock drift) ou erros de formatação não-maliciosos
- **Resultado:** O sistema entrega dados sanitizados/mascarados (ex: CPF: `***-**-1234`)
- **Propósito:** Manter a usabilidade (UX) em redes instáveis sem expor o núcleo sensível

### 3. **SHADOW REALITY** (O Engano)
- **Condição:** Violação topológica, Assinatura inválida ou Replay
- **Resultado:** Payload sintético determinístico (mesma requisição gera sempre a mesma mentira)

#### 🔥 **Stealth Tech:**
- **Payload Realista:** Gera JSONs estruturalmente idênticos aos reais (ex: dados bancários, perfis de utilizador)
- **Jittering:** Introduz latência artificial variável para mimetizar operações de base de dados, mitigando ataques de análise estatística de tempo
- **Sem Marcadores:** Não há headers ou campos indicando "Shadow"

---

## 📐 Fundamentação Matemática

A segurança do protocolo repousa sobre o **Teorema de Zeckendorf**, que afirma que qualquer número inteiro positivo pode ser representado de forma única como a soma de números de Fibonacci não-consecutivos.

---

**Fórmula de Recorrência de Fibonacci:**  
`Fₙ = Fₙ₋₁ + Fₙ₋₂`

**Restrição de Adjacência Zeckendorf (validação bitwise):**  
`(M & (M >> 1)) = 0`

Onde `M` é a máscara de permissões binária, `&` é AND bitwise, e `>> 1` é deslocamento à direita de 1 bit.

---

Essa propriedade permite validação bitwise em **O(1)**, garantindo que permissões conflitantes (bits adjacentes) sejam matematicamente impossíveis.

---

## 🚀 Performance

Desenhado para **Sistemas de Alta Vazão (High-Throughput)**. O impacto na latência é desprezível comparado a operações de I/O.

| Linguagem | Validação Lógica | Geração Shadow | Overhead Total |
|-----------|------------------|----------------|----------------|
| Go        | ~0.1µs           | ~3.1µs         | < 10µs         |
| Rust      | ~0.08µs          | ~2.5µs         | < 5µs          |
| Python    | ~2.1µs           | ~30.8µs        | < 0.5ms        |

*Dados baseados em benchmarks em Intel i7. Veja relatório completo.*

---

## 🎯 Casos de Uso Reais

### 1. **Setor Bancário (Pix & Open Finance)**
- **Desafio:** Atacantes capturam requisições válidas e tentam reenviá-las (Replay Attack)
- **Solução ELP:** A verificação de Nonce integrada ao cálculo de Zeckendorf deteta a duplicata e envia o atacante para a Shadow Reality, onde a transação parece ter ocorrido, mas nenhum dinheiro é movido

### 2. **Saúde Digital (Prontuários Eletrónicos)**
- **Desafio:** Médicos em áreas rurais com 4G instável frequentemente têm requisições com timestamps dessincronizados
- **Solução ELP:** Em vez de bloquear o médico (Denial of Service), o sistema ativa a Mirror Reality, entregando o prontuário visualizável mas mascarando dados sensíveis

### 3. **Anti-Scraping Governamental**
- **Desafio:** Bots varrem portais de transparência procurando vulnerabilidades
- **Solução ELP:** Ao detetar padrões de varredura, o ELP alimenta o bot com dados infinitos e sintéticos, envenenando a base de dados do atacante (Data Poisoning)

---

## 🔗 Links e Recursos

- 📚 [**Documentação Técnica**](https://link.com) - Arquitetura & Operações
- 📄 [**Paper Académico**](https://link.com) - Segurança Ontológica: Uma Abordagem Filosófica
- 🧮 [**Matemática**](https://link.com) - Prova da Restrição de Zeckendorf
- 🛡️ [**Análise de Segurança**](https://link.com) - Threat Model & Attack Vectors

---

## 📄 Licença e Modelo Comercial

Este projeto opera sob um modelo de **Licenciamento Dual (Dual Licensing)**:

- **Comunidade & Académico (Open Core):** O núcleo de validação matemática (Zeckendorf Constraint) é livre para uso em pesquisas e projetos não-comerciais sob a licença **Apache 2.0**
- **Enterprise (Commercial):** O uso em ambientes de produção corporativa, incluindo o Shadow Reality Generator, requer uma **licença comercial**

---

© 2025 Álvaro Alencar. Todos os direitos reservados.