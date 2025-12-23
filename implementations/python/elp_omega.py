import hmac
import hashlib
import base64
import time
import uuid
import threading
import re
from enum import Enum
from typing import Tuple, Dict, Any

class Reality(Enum):
    PRIME = "PRIME"
    MIRROR = "MIRROR"
    SHADOW = "SHADOW"

class EntangledLogicOmegaV5:
    """
    PROTOCOLO ELP-Ω v5 — ZECKENDORF-LIKE TRIPLE-REALITY
    Implementação em Python focada em Defesa Ativa da Vortex Development.
    """
    def __init__(self, secret: bytes, max_age_ms: int = 300000, max_failures: int = 5):
        self._secret = secret
        self.max_age_ms = max_age_ms
        self.max_failures = max_failures
        self._used_nonces: Dict[str, float] = {}
        self._failures: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def is_valid_zeckendorf_mask(self, mask: int) -> bool:
        """Verifica a restrição de não-adjacência (Bitwise Zeckendorf)."""
        if mask < 0:
            return False
        return (mask & (mask >> 1)) == 0

    def compute_seal(self, mask: int, context: str, timestamp: int, path: str, nonce: str) -> str:
        """Gera o selo HMAC-SHA256 para validação da integridade."""
        payload = f"{mask}|{context}|{timestamp}|{path}|{nonce}"
        h = hmac.new(self._secret, payload.encode('utf-8'), hashlib.sha256)
        return base64.b64encode(h.digest()).decode('utf-8')

    def process_request(self, req: Dict[str, Any], real_data: str, fingerprint: str) -> Tuple[str, Reality]:
        """
        Processa a requisição e decide a Realidade de resposta.
        """
        mask = req.get('mask', 0)
        seal = req.get('seal', '')
        context = req.get('context', '')
        timestamp = req.get('timestamp', 0)
        path = req.get('path', '')
        nonce = req.get('nonce', '')

        # 1. Validação de Máscara (Zeckendorf)
        if not self.is_valid_zeckendorf_mask(mask):
            return self.generate_shadow(real_data, context, path), Reality.SHADOW

        # 2. Check de Freshness (Timestamp)
        now_ms = int(time.time() * 1000)
        if not (0 <= (now_ms - timestamp) <= self.max_age_ms):
            return self.sanitize(real_data), Reality.MIRROR

        # 3. Validação do Selo (HMAC)
        expected_seal = self.compute_seal(mask, context, timestamp, path, nonce)
        if not hmac.compare_digest(seal, expected_seal):
            return self._handle_failure(fingerprint, real_data, context, path)

        # 4. Anti-Replay (Nonce)
        with self._lock:
            if nonce in self._used_nonces:
                return self.generate_shadow(real_data, context, path), Reality.SHADOW
            self._used_nonces[nonce] = time.time()

        return f"PRIME_REALITY: {real_data}", Reality.PRIME

    def _handle_failure(self, fingerprint: str, real_data: str, context: str, path: str) -> Tuple[str, Reality]:
        with self._lock:
            now = time.time() * 1000
            record = self._failures.get(fingerprint, {"count": 0, "first": now})
            
            if now - record["first"] > 3600000: # Janela de 1 hora
                record = {"count": 1, "first": now}
            else:
                record["count"] += 1
            
            self._failures[fingerprint] = record
            if record["count"] > self.max_failures:
                return self.generate_shadow(real_data, context, path), Reality.SHADOW
            return self.sanitize(real_data), Reality.MIRROR

    def sanitize(self, data: str) -> str:
        """Mascaramento de PII (Mirror Reality)."""
        data = re.sub(r'\d', '*', data)
        data = re.sub(r'(?i)senha[:=]\s*[^\s,;]+', 'senha=********', data)
        return data

    def generate_shadow(self, real_data: str, context: str, path: str) -> str:
        """Gera dados falsos determinísticos (Shadow Reality)."""
        seed = f"SHADOW|{path}|{context}|STABILITY|{len(real_data)}"
        h = hmac.new(self._secret, seed.encode('utf-8'), hashlib.sha256)
        vault_id = base64.urlsafe_b64encode(h.digest()[:8]).decode('utf-8').rstrip('=')
        return f"SHADOW_VAULT_ID:{vault_id}:DATA_ENCRYPTED"