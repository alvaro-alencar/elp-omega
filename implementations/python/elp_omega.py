import hashlib
import hmac
import time
import random
import uuid

# Enumeração para clareza
class Reality:
    PRIME = "PRIME"
    MIRROR = "MIRROR"
    SHADOW = "SHADOW"

class EntangledLogicOmegaV5:
    def __init__(self, secret: bytes, max_age_ms: int = 300000):
        self.secret = secret
        self.max_age_ms = max_age_ms
        self._used_nonces = {} # Em prod: usar Redis com TTL
        self._lock = None # Simplificação para demo sem threading complexo

    def is_valid_zeckendorf_mask(self, mask: int) -> bool:
        """Validação Topológica O(1)"""
        return (mask & (mask >> 1)) == 0

    def compute_seal(self, mask: int, context: str, timestamp: int, path: str, nonce: str) -> str:
        """Gera assinatura HMAC-SHA256"""
        payload = f"{mask}|{context}|{timestamp}|{path}|{nonce}"
        return hmac.new(self.secret, payload.encode(), hashlib.sha256).hexdigest()

    def generate_shadow(self, real_data_structure: str, context: str, path: str, nonce: str) -> dict:
        """
        Gera um Payload Sintético Indistinguível do Real.
        Usa o nonce e o path como semente para garantir determinismo:
        Mesma entrada = Mesma mentira.
        """
        # Cria uma semente determinística baseada na requisição do atacante
        seed_str = f"{path}|{context}|{nonce}|{self.secret}"
        seed_int = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (10**8)
        
        # Configura o gerador aleatório com essa semente
        rng = random.Random(seed_int)

        # Gera dados que PARECEM reais (sem marcadores 'SHADOW')
        # Simula uma estrutura de resposta financeira padrão
        return {
            "status": "success",
            "transaction_id": str(uuid.UUID(int=rng.getrandbits(128))),
            "timestamp": int(time.time() * 1000),
            "data": {
                "account_type": rng.choice(["checking", "savings", "investment"]),
                "balance": round(rng.uniform(1000.00, 500000.00), 2),
                "currency": "BRL",
                "flags": ["verified", "secure"]
            },
            "meta": {
                "processing_time_ms": rng.randint(10, 150),
                "region": "us-east-1"
            }
        }