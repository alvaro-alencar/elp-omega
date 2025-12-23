import requests
import hmac
import hashlib
import base64
import time
import uuid
import json

# CONFIGURAÇÃO
TARGET_URL = "http://localhost:8000/api/v1/resource" # Ajuste para sua porta (8000=Py, 3000=Node)
SECRET_KEY = b"SUA_CHAVE_MESTRA_AQUI" # Deve ser a mesma do Middleware

class ElpAttacker:
    def __init__(self, secret):
        self.secret = secret

    def generate_headers(self, mask, context="GET", path="/api/v1/resource", nonce=None, timestamp=None, bad_sig=False):
        """Gera headers compatíveis com o protocolo ELP-Ω"""
        ts = int(time.time() * 1000) if timestamp is None else timestamp
        n = str(uuid.uuid4()) if nonce is None else nonce
        
        # Payload para assinatura
        payload = f"{mask}|{context}|{ts}|{path}|{n}"
        
        # Gera assinatura (HMAC)
        h = hmac.new(self.secret, payload.encode('utf-8'), hashlib.sha256)
        sig = base64.b64encode(h.digest()).decode('utf-8')

        if bad_sig:
            sig = "A" * len(sig) # Assinatura corrompida

        return {
            "X-ELP-Mask": str(mask),
            "X-ELP-Seal": sig,
            "X-ELP-Timestamp": str(ts),
            "X-ELP-Nonce": n
        }

    def attack(self, scenario_name, mask, bad_sig=False, replay_headers=None):
        print(f"\n--- [CENÁRIO: {scenario_name}] ---")
        
        if replay_headers:
            headers = replay_headers
            print(f"[*] REPLAY: Reutilizando headers antigos (Nonce: {headers['X-ELP-Nonce']})")
        else:
            headers = self.generate_headers(mask, bad_sig=bad_sig)
            # Verifica bitwise se a máscara é válida (só para log visual)
            is_valid = (mask & (mask >> 1)) == 0
            status_str = "VÁLIDA (Zeckendorf)" if is_valid else "INVÁLIDA (Bit Adjacente)"
            print(f"[*] ENVIANDO: Máscara {bin(mask)} -> {status_str}")

        try:
            # Tenta acessar a API
            start = time.time()
            response = requests.get(TARGET_URL, headers=headers)
            latency = (time.time() - start) * 1000
            
            data = response.json()
            reality = data.get('reality', 'DESCONHECIDO')
            payload = data.get('data', '')

            # ANÁLISE DO RESULTADO
            color = "\033[92m" if reality == "PRIME" else "\033[91m" # Verde/Vermelho
            reset = "\033[0m"
            
            print(f"[*] STATUS HTTP: {response.status_code}")
            print(f"[*] REALIDADE DETECTADA: {color}{reality}{reset}")
            print(f"[*] PAYLOAD RECEBIDO: {payload[:60]}...")
            print(f"[*] LATÊNCIA PERCEBIDA: {latency:.2f}ms")
            
            if reality == "SHADOW":
                print("\033[93m[!] ENGANO BEM SUCEDIDO: O atacante recebeu dados falsos.\033[0m")
                
            return headers # Retorna headers para usar em testes de replay

        except Exception as e:
            print(f"[!] ERRO DE CONEXÃO: {e}")
            print("Dica: Verifique se o servidor Middleware está rodando.")

# --- EXECUÇÃO DOS TESTES ---
if __name__ == "__main__":
    attacker = ElpAttacker(SECRET_KEY)
    
    # 1. O CIDADÃO MODELO (Acesso Legítimo)
    # Máscara 5 (Binário 101) -> Bits não adjacentes. OK.
    attacker.attack("USUÁRIO LEGÍTIMO", mask=5) 

    # 2. O SCRIPT KIDDIE (Violação Topológica)
    # Máscara 6 (Binário 110) -> Bits adjacentes! Viola Zeckendorf.
    # O Middleware deve barrar IMEDIATAMENTE e jogar para SHADOW.
    attacker.attack("VIOLAÇÃO MATEMÁTICA (ZECKENDORF)", mask=6)

    # 3. O FALSIFICADOR (Assinatura Inválida)
    # Máscara válida (5), mas chave errada.
    attacker.attack("ASSINATURA FORJADA", mask=5, bad_sig=True)

    # 4. O REPLAY ATTACK (Cópia de Requisição)
    # Pega uma requisição válida e tenta enviar de novo.
    valid_headers = attacker.generate_headers(mask=5)
    print("\n--- [PREPARANDO REPLAY] ---")
    print("Enviando requisição original...")
    requests.get(TARGET_URL, headers=valid_headers) # Primeira vez (ok)
    
    # Segunda vez (deve falhar por Nonce duplicado)
    attacker.attack("ATAQUE DE REPLAY", mask=5, replay_headers=valid_headers)