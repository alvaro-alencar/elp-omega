import time
import hmac
import random
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
# Ajuste o import conforme sua estrutura de pastas
from elp_omega import EntangledLogicOmegaV5

class ElpOmegaMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        self.security_engine = EntangledLogicOmegaV5(secret=secret_key.encode())

    async def dispatch(self, request: Request, call_next):
        # 1. Extração
        mask = int(request.headers.get("X-ELP-Mask", -1))
        seal = request.headers.get("X-ELP-Seal", "")
        timestamp = int(request.headers.get("X-ELP-Timestamp", 0))
        nonce = request.headers.get("X-ELP-Nonce", "")
        path = request.url.path
        context = request.method 
        
        # Variável de decisão
        is_shadow_candidate = False

        # 2. Validações em Cascata (Fail Fast vs Fail Silent)
        
        # A. Validação Zeckendorf (Topológica)
        if not self.security_engine.is_valid_zeckendorf_mask(mask):
            is_shadow_candidate = True
        
        # B. Validação Timestamp (Freshness - 5 min tolerance)
        now_ms = int(time.time() * 1000)
        if not is_shadow_candidate:
             # Tolerância ajustada para 5 minutos (300000ms)
             if abs(now_ms - timestamp) > 300000: 
                 is_shadow_candidate = True

        # C. Validação HMAC (Integridade)
        if not is_shadow_candidate:
            expected_seal = self.security_engine.compute_seal(mask, context, timestamp, path, nonce)
            # compare_digest evita Timing Attacks na comparação de strings
            if not hmac.compare_digest(seal, expected_seal):
                is_shadow_candidate = True

        # D. Validação Nonce (Anti-Replay)
        if not is_shadow_candidate:
            if nonce in self.security_engine._used_nonces:
                is_shadow_candidate = True
            else:
                # Armazena o nonce (Em produção, use Redis com TTL)
                self.security_engine._used_nonces[nonce] = now_ms

        # 3. Decisão de Realidade
        if is_shadow_candidate:
            return self._serve_shadow_reality(context, path, nonce)

        # 4. Prime Reality (Acesso Concedido)
        # O processamento real acontece aqui
        response = await call_next(request)
        return response

    def _serve_shadow_reality(self, context, path, nonce):
        """
        Entrega a realidade simulada.
        O objetivo é imitar o tempo de resposta da Prime Reality (que agora tem um sleep de 10-50ms).
        """
        # Gera o payload falso mas realista (Bancário)
        shadow_payload = self.security_engine.generate_shadow("STRUCT", context, path, nonce)
        
        # JITTERING ESTRATÉGICO:
        # A Prime Reality demora entre 10ms e 50ms (simulado no endpoint).
        # A Shadow Reality deve demorar algo parecido para ser indistinguível.
        # Vamos configurar para 15ms a 60ms.
        latency = random.uniform(0.015, 0.060) 
        time.sleep(latency)

        # Retorna 200 OK.
        # NÃO incluímos headers reveladores.
        return JSONResponse(
            content=shadow_payload,
            status_code=200
        )