# ELP-Ω: Implementação Python (Vortex Development)

Esta pasta contém a lógica do **Entangled Logic Protocol** em Python, otimizada para integração com APIs (Flask, FastAPI, Django).

## 🧪 Como testar
Execute o comando abaixo na pasta raiz deste diretório:
`python test_elp_omega.py`

## 🛡️ Segurança Ontológica
Esta implementação utiliza `threading.Lock` para garantir que o controle de nonces e falhas seja seguro em ambientes multi-thread.