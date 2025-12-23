import time
import json
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
# Importamos a classe original que você já criou
from elp_omega import EntangledLogicOmegaV5, Reality

class ElpOmegaMiddleware(BaseHTTPMiddleware):
    """
    ELP-Ω Middleware para FastAPI.
    Intercepta todas as requisições para validar a Realidade Ontológica.
    
    Estratégia:
    1. SHADOW: Retorna 200 OK com dados falsos imediatamente (Short-circuit).
       Isso protege o backend de processamento inútil (Anti-DoS).
    2. MIRROR: Marca o request para sanitização posterior ou avisa o backend.
    3. PRIME: Permite passagem transparente.
    """
    def __init__(self, app, secret_key: str):
        super().__init__(app)
        # Inicializa o motor lógico com a chave secreta
        self.security_engine = EntangledLogicOmegaV5(secret=secret_key.encode())

    async def dispatch(self, request: Request, call_next):
        # 1. Extração de Metadados dos Headers
        # O cliente deve enviar os parâmetros do ELP nos headers HTTP
        mask = int(request.headers.get("X-ELP-Mask", -1))
        seal = request.headers.get("X-ELP-Seal", "")
        timestamp = int(request.headers.get("X-ELP-Timestamp", 0))
        nonce = request.headers.get("X-ELP-Nonce", "")
        
        # O contexto e path são derivados da própria requisição
        path = request.url.path
        context = request.method 
        
        # Construímos o objeto de análise para o motor
        req_params = {
            'mask': mask,
            'seal': seal,
            'context': context,
            'timestamp': timestamp,
            'path': path,
            'nonce': nonce
        }

        # 2. Pré-Validação (Sem os dados reais ainda)
        # Usamos uma string vazia como 'real_data' apenas para testar a intenção/permissão
        # O 'fingerprint' pode ser o IP do cliente
        client_ip = request.client.host
        
        # A lógica aqui é sutil: Validamos a "Forma" (Topology), não o Conteúdo ainda.
        # Se a máscara for inválida (Bitwise Zeckendorf), já caímos na Shadow Reality.
        if not self.security_engine.is_valid_zeckendorf_mask(mask):
            # ESTRATÉGIA DE DEFESA ATIVA:
            # Retornamos 200 OK (sucesso falso) com payload sintético.
            # Não chamamos 'call_next(request)', ou seja, o servidor real NÃO trabalha.
            shadow_payload = self.security_engine.generate_shadow("DUMMY_DATA_FOR_SHADOW", context, path)
            return JSONResponse(
                content={"data": shadow_payload, "reality": "SHADOW"},
                status_code=200 
            )

        # 3. Execução da Rota Real (Se passou na barreira topológica)
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Adiciona header de diagnóstico (opcional, bom para debug)
        response.headers["X-ELP-Latency"] = str(process_time)
        
        # Nota: Para implementação completa do MIRROR (sanitização), 
        # precisaríamos interceptar o corpo da resposta aqui. 
        # Por enquanto, focamos na barreira de entrada (PRIME vs SHADOW).
        
        return response

# --- Como usar este código no seu servidor principal ---
# from fastapi import FastAPI
# app = FastAPI()
# app.add_middleware(ElpOmegaMiddleware, secret_key="SUA_CHAVE_MESTRA_AQUI")