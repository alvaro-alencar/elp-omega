import uvicorn
from fastapi import FastAPI
import sys
import os

# --- CORREÇÃO DO PATH ---
# Garante que o Python encontre os módulos na pasta implementations
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "implementations", "python"))

# Importação do Middleware
from elp_middleware import ElpOmegaMiddleware 

app = FastAPI()

# ATIVANDO O ELP-OMEGA
# A chave deve ser a mesma que está no demo_attack.py
app.add_middleware(ElpOmegaMiddleware, secret_key="SUA_CHAVE_MESTRA_AQUI")

@app.get("/api/v1/resource")
async def sensitive_data():
    # Simulamos um pequeno processamento real de banco de dados (10ms a 50ms)
    # para que a Prime Reality não seja instantânea demais (0ms), o que seria suspeito.
    import time
    import random
    time.sleep(random.uniform(0.010, 0.050))
    
    return {
        "data": {
            "secret": "DADOS SECRETOS DO BANC0 CENTRAL",
            "balance": 1000000.00,
            "status": "verified"
        },
        # Removemos o campo 'reality' explicito para manter o Stealth Mode
        # O atacante deve inferir pelo conteúdo
    }

if __name__ == "__main__":
    print("🛡️  SISTEMA DE DEFESA ELP-OMEGA ATIVO...")
    print("   -> Modo Stealth: ON")
    print("   -> Ouvindo em http://127.0.0.1:8000")
    
    # Otimização: Usamos 127.0.0.1 em vez de localhost para evitar delay de DNS IPv6
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")