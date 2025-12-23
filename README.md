# ELP-Ω: Zeckendorf Security Middleware

> **"Pare de bloquear ataques. Comece a gerenciar realidades."**

![Build Status](https://img.shields.io/badge/build-passing-success?style=for-the-badge&logo=github-actions)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=for-the-badge)
![License](https://img.shields.io/badge/license-Proprietary-blue?style=for-the-badge)
![Author](https://img.shields.io/badge/architect-%C3%81lvaro_Alencar-orange?style=for-the-badge)

---

## ⚡ Quick Start: Proteja sua API em 5 Minutos

Não reescreva seu código. Adicione o **ELP-Ω Middleware** e ganhe proteção imediata contra Replay Attacks, Scrapers e API Abuse.

### Python (FastAPI / Starlette)
```python
from fastapi import FastAPI
from implementations.python.elp_middleware import ElpOmegaMiddleware

app = FastAPI()

# 1. Ative o Campo de Força Lógico
# Qualquer requisição que viole a Topologia de Zeckendorf receberá uma resposta falsa (Shadow Reality).
app.add_middleware(ElpOmegaMiddleware, secret_key="SUA_CHAVE_MESTRA_AQUI")

@app.get("/dados-sensiveis")
def read_data():
    return {"status": "safe", "data": "Este endpoint está blindado."}
```

### TypeScript (Express / Node.js)
```typescript
import express from 'express';
import { elpOmegaMiddleware } from './implementations/typescript/elpMiddleware';

const app = express();

// 2. Plug & Play Security
app.use(elpOmegaMiddleware('SUA_CHAVE_MESTRA_AQUI'));

app.get('/api/financeiro', (req, res) => {
    res.json({ saldo: 1000000 });
});
```

---

## 🛡️ O Que é o ELP-Ω?

**ELP-Ω (Omega)** é um protocolo de segurança algorítmica que substitui firewalls binários (Allow/Deny) por uma **Arquitetura de Tripla Realidade**.

Utilizando o **Teorema de Zeckendorf**, o protocolo valida a integridade da requisição em tempo constante $O(1)$, verificando a adjacência de bits na máscara de permissão.

| Se o atacante... | O Firewall tradicional faz... | O ELP-Ω faz... |
| --- | --- | --- |
| **Tenta escalar privilégios** | Bloqueia (403 Forbidden) | **SHADOW Reality:** Retorna "200 OK" com dados falsos gerados matematicamente. |
| **Tenta um Replay Attack** | Bloqueia ou falha | **SHADOW Reality:** O atacante recebe um hash válido que não descriptografa nada. |
| **Tem conexão instável** | Falha (Timeout/Error) | **MIRROR Reality:** Entrega dados sanitizados (LGPD safe) para manter a UX. |

---

## 🚀 Benchmarks e Performance

O ELP-Ω foi desenhado para **APIs Críticas** e **Sistemas de Alta Vazão** (High-Throughput). O impacto na latência é desprezível comparado a validações de banco de dados ou WAFs tradicionais.

| Operação | ELP-Ω (Go) | ELP-Ω (Python) | JWT Standard |
| --- | --- | --- | --- |
| **Validação Lógica** | **~0.1µs** | ~2.1µs | ~50µs |
| **Geração de Shadow Payload** | **~3.1µs** | ~30.8µs | N/A (Apenas bloqueia) |
| **Overhead Total** | **< 5µs** | < 1ms | ~2-10ms |

> *Dados baseados em testes em Intel i7-9750H. Veja o [relatório completo](docs/benchmarks.md).*

---

## 🎯 Casos de Uso Reais

### 1. Setor Bancário (Pix & Open Finance)

* **Desafio:** Atacantes capturam requisições válidas e tentam reenviá-las (Replay Attack) para duplicar transações.
* **Solução ELP:** A verificação de `Nonce` integrada ao cálculo de Zeckendorf detecta a duplicata em nanossegundos e envia o atacante para a **Shadow Reality**, onde a transação *parece* ter ocorrido, mas nenhum dinheiro é movido.

### 2. Saúde Digital (Prontuários Eletrônicos)

* **Desafio:** Médicos em áreas rurais com 4G instável frequentemente têm requisições corrompidas ou timestamps dessincronizados.
* **Solução ELP:** Em vez de bloquear o médico (Denial of Service), o sistema ativa a **Mirror Reality**, entregando o prontuário visualizável mas mascarando dados sensíveis (CPF, Endereço), garantindo o atendimento sem violar a LGPD.

### 3. Governo e Defesa (Anti-Scraping)

* **Desafio:** Bots varrem portais de transparência ou APIs públicas buscando vulnerabilidades.
* **Solução ELP:** Ao detectar padrões de varredura (máscaras de bits sequenciais), o ELP alimenta o bot com dados infinitos e sintéticos, envenenando o banco de dados do atacante (Data Poisoning).

---

## ⚔️ Veja o Ataque em Ação

O repositório inclui um script de demonstração que simula um atacante tentando violar o sistema.
```bash
# Execute a simulação
python demo_attack.py
```

**Saída Esperada:**
```text
[*] ENVIANDO: Máscara 101 (Válida) -> REALIDADE: PRIME (Dados Reais)
[*] ENVIANDO: Máscara 110 (Violação Zeckendorf) -> REALIDADE: SHADOW (Dados Falsos)
[!] ENGANO BEM SUCEDIDO: O atacante recebeu um SHADOW_VAULT_ID e acredita ter roubado dados.
```

---

## 📐 Fundamentação Matemática: O Teorema de Zeckendorf

A segurança do protocolo repousa sobre o **Teorema de Zeckendorf**, que afirma que qualquer número inteiro positivo pode ser representado de forma única como a soma de números de Fibonacci não-consecutivos.

O protocolo usa essa propriedade para criar máscaras de permissão topologicamente seguras. Diferente de bitmasks comuns onde qualquer bit pode ser ativado, o ELP-Ω força a **regra de não-adjacência**:

$$F_n = F_{n-1} + F_{n-2}$$

A validação da máscara $M$ segue uma lógica booleana estrita:

$$(M \ \& \ (M \gg 1)) == 0$$

Se esta operação resulta em verdadeiro (0), a máscara é topologicamente válida. Qualquer outro valor indica uma tentativa de Escalação de Privilégios ou Ataque de Bit-Flipping, acionando imediatamente as contramedidas de Shadow Reality.

---

## 🔮 Arquitetura de Tripla Realidade (Defesa Ontológica)

O sistema não rejeita conexões suspeitas; ele as gerencia através de camadas de realidade, esgotando recursos do atacante ao aprisioná-lo em ambientes simulados.

### 1. PRIME REALITY (A Verdade)

**Condição:** Máscara Zeckendorf Válida + Assinatura HMAC Intacta + Timestamp Fresco + Nonce Único

**Resultado:** O sistema entrega dados reais, descriptografados e operacionais

**Alvo:** Usuários legítimos e sistemas autenticados

### 2. MIRROR REALITY (Degradação Elegante)

**Condição:** Falha menor de integridade temporal (clock drift) ou erros de formatação não-maliciosos

**Resultado:** O sistema entrega dados sanitizados/mascarados (ex: CPF: ***-**-1234)

**Propósito:** Manter a usabilidade (UX) em redes instáveis sem expor o núcleo sensível

### 3. SHADOW REALITY (O Labirinto Determinístico)

**Condição:** Violação da Regra de Zeckendorf, falha no HMAC ou detecção de Replay Attack

**Resultado:** O sistema gera, em tempo real, um payload sintético estruturalmente indistinguível dos dados reais, mas com valores gerados matematicamente derivados de uma "Semente de Estabilidade"

**Efeito Tático:** O atacante acredita ter violado o sistema e continua tentando decifrar dados que, ontologicamente, não existem. Isso transforma defesa em ofensa passiva (honeypot dinâmico).

> **Nota de Segurança:** A implementação inclui *Jittering* (atraso aleatório artificial) na geração da Shadow Reality. Isso mitiga ataques de canal lateral (Timing Attacks), tornando o tempo de resposta indistinguível de uma requisição processada na Prime Reality.

## ⚠️ Modelo de Ameaças (Threat Model)

O ELP-Ω atua na Camada de Aplicação (L7). É crucial entender seu escopo:

- Protege contra: Enumeration Attacks, ID Scraping, Replay Attacks e Fuzzing de API.

- Não substitui: Criptografia de transporte (TLS/SSL) nem proteção contra DDoS Volumétrico (L3/L4).

- Requisito Crítico: A segurança depende inteiramente do segredo da SECRET_KEY. Recomendamos rotação periódica via HSM ou Vault.
---

## 📦 Instalação e Testes

O projeto é poliglota. Você pode rodar a suíte de testes completa via Docker:
```bash
docker-compose up --build
```

Isso validará as implementações em **Go, Rust, Python, Kotlin e TypeScript** simultaneamente.

### Implementações Disponíveis

| Linguagem | Paradigma | Aplicação Recomendada | Status |
| --- | --- | --- | --- |
| **Go** | Concorrente | Microservices de Alta Performance / Fintech Core | ✅ Estável |
| **Rust** | Sistema/Seguro | Sistemas Embarcados / Nós Blockchain | ✅ Estável |
| **Python** | Dinâmica | Data Science / Pipelines de IA / Prototipagem | ✅ Estável |
| **Kotlin** | Híbrida | Backend JVM / Armazenamento Seguro Android | ✅ Estável |
| **TypeScript** | Event-Driven | Serverless Functions (AWS Lambda) / Node.js | ✅ Estável |

Todas as implementações compartilham vetores de teste unificados, garantindo que um token gerado em Python seja perfeitamente validado em Rust.

---

## ⚖️ Sobre o Autor e a Pesquisa

**Álvaro Alencar**  
*Advogado, Desenvolvedor de Software e Pesquisador*

O ELP-Ω nasceu da necessidade de preencher a lacuna entre **Segurança Jurídica** (exigida pela LGPD/GDPR) e **Segurança Técnica**. Enquanto o Direito exige proteção de dados, a Engenharia frequentemente falha ao oferecer apenas barreiras estáticas.

Esta pesquisa propõe que a verdadeira proteção de dados sensíveis deve ser **Ontológica**: os dados não devem "existir" para observadores não autorizados.

---

## 🔗 Links

* **Documentação:** [Arquitetura Técnica & Operações](docs/architecture.md)
* **Paper de Pesquisa:** [Segurança Ontológica: Uma Abordagem Filosófica para Ciberdefesa](docs/ontological-security.md)
* **Matemática:** [Prova da Restrição de Zeckendorf](docs/fibonacci-constraint.md)
* **Contato:** ac.alvaro@gmail.com

---

## 📄 Licença e Modelo Comercial

Este projeto opera sob um modelo de Licenciamento Dual (Dual Licensing):

Comunidade & Acadêmico (Open Core): O núcleo de validação matemática (Zeckendorf Constraint) é livre para uso em pesquisas e projetos não-comerciais sob a licença Apache 2.0.

Enterprise (Commercial): O uso em ambientes de produção corporativa requer uma licença comercial da Vortex Development.

© 2025 Álvaro Alencar. Todos os direitos reservados.

---

**Construído com rigor matemático. Implantado com intenção estratégica.**