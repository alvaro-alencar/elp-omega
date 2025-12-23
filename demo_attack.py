#!/usr/bin/env python3
"""
ELP-Ω Security Testing Suite
Demonstra vetores de ataque e comportamento das três realidades.
Autor: Álvaro Alencar (refatorado por Claude)
"""

import requests
import hmac
import hashlib
import base64
import time
import uuid
import json
import statistics
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

# ==================== CONFIGURAÇÃO ====================
TARGET_URL = "http://localhost:8000/api/v1/resource"
SECRET_KEY = b"SUA_CHAVE_MESTRA_AQUI"
TIMING_SAMPLES = 20  # Número de amostras para análise estatística

# ==================== CORES ANSI ====================
class Colors:
    PRIME = "\033[92m"      # Verde
    SHADOW = "\033[91m"     # Vermelho
    MIRROR = "\033[93m"     # Amarelo
    INFO = "\033[94m"       # Azul
    BOLD = "\033[1m"
    RESET = "\033[0m"

# ==================== CLASSES DE DADOS ====================
@dataclass
class AttackResult:
    scenario: str
    mask: int
    mask_binary: str
    is_valid_mask: bool
    http_status: int
    reality: str
    payload_preview: str
    latency_ms: float
    headers_used: Dict[str, str]
    success: bool
    notes: str = ""

class RealityType(Enum):
    PRIME = "PRIME"
    SHADOW = "SHADOW"
    MIRROR = "MIRROR"
    UNKNOWN = "UNKNOWN"

# ==================== ANALISADOR ELP-Ω ====================
class ElpAnalyzer:
    """Analisa resultados e detecta anomalias"""
    
    @staticmethod
    def is_zeckendorf_valid(mask: int) -> bool:
        """Valida a Restrição de Zeckendorf: bits não podem ser adjacentes"""
        return (mask & (mask >> 1)) == 0
    
    @staticmethod
    def analyze_timing(latencies: List[float]) -> Dict:
        """Análise estatística de timing (detecção de jittering)"""
        if len(latencies) < 2:
            return {"mean": latencies[0] if latencies else 0, "stddev": 0}
        
        return {
            "mean": statistics.mean(latencies),
            "median": statistics.median(latencies),
            "stddev": statistics.stdev(latencies),
            "min": min(latencies),
            "max": max(latencies),
            "range": max(latencies) - min(latencies)
        }
    
    @staticmethod
    def detect_data_pattern(payload: str) -> str:
        """Tenta detectar se dados são reais ou sintéticos"""
        # Heurísticas simples (em produção, seria ML-based)
        indicators = []
        
        if "shadow" in payload.lower():
            indicators.append("Marcador de Shadow explícito")
        
        # Verifica padrões repetitivos (dados sintéticos tendem a ter padrões)
        if len(set(payload)) < len(payload) * 0.3:
            indicators.append("Alta repetição de caracteres")
        
        # Verifica entropia (dados reais têm mais entropia)
        entropy = len(set(payload)) / len(payload) if payload else 0
        if entropy < 0.4:
            indicators.append(f"Baixa entropia ({entropy:.2f})")
        
        return " | ".join(indicators) if indicators else "Padrão normal"

# ==================== GERADOR DE ATAQUES ====================
class ElpAttacker:
    def __init__(self, secret: bytes):
        self.secret = secret
        self.nonce_history: List[str] = []
        self.results: List[AttackResult] = []
    
    def generate_headers(
        self, 
        mask: int, 
        context: str = "GET", 
        path: str = "/api/v1/resource",
        nonce: Optional[str] = None,
        timestamp: Optional[int] = None,
        corrupt_signature: bool = False,
        corrupt_timestamp: bool = False
    ) -> Dict[str, str]:
        """Gera headers do protocolo ELP-Ω"""
        
        ts = timestamp if timestamp else int(time.time() * 1000)
        n = nonce if nonce else str(uuid.uuid4())
        
        # Corrupcões intencionais para testes
        if corrupt_timestamp:
            ts = ts - (1000 * 60 * 10)  # 10 minutos no passado
        
        # Payload para HMAC
        payload = f"{mask}|{context}|{ts}|{path}|{n}"
        
        # Geração de assinatura
        h = hmac.new(self.secret, payload.encode('utf-8'), hashlib.sha256)
        sig = base64.b64encode(h.digest()).decode('utf-8')
        
        if corrupt_signature:
            # Corrompe apenas 1 byte para simular bit-flip
            sig_bytes = base64.b64decode(sig)
            corrupted = bytearray(sig_bytes)
            corrupted[0] ^= 0xFF  # XOR no primeiro byte
            sig = base64.b64encode(bytes(corrupted)).decode('utf-8')
        
        headers = {
            "X-ELP-Mask": str(mask),
            "X-ELP-Seal": sig,
            "X-ELP-Timestamp": str(ts),
            "X-ELP-Nonce": n
        }
        
        self.nonce_history.append(n)
        return headers
    
    def execute_attack(
        self,
        scenario: str,
        mask: int,
        **header_kwargs
    ) -> Optional[AttackResult]:
        """Executa um cenário de ataque e registra resultado"""
        
        is_valid = ElpAnalyzer.is_zeckendorf_valid(mask)
        headers = self.generate_headers(mask, **header_kwargs)
        
        # Log visual
        mask_bin = bin(mask)
        status = f"{Colors.PRIME}VÁLIDA{Colors.RESET}" if is_valid else f"{Colors.SHADOW}INVÁLIDA{Colors.RESET}"
        print(f"\n{Colors.BOLD}[ATAQUE: {scenario}]{Colors.RESET}")
        print(f"  Máscara: {mask} ({mask_bin}) -> {status}")
        
        try:
            start = time.perf_counter()
            response = requests.get(TARGET_URL, headers=headers, timeout=5)
            latency = (time.perf_counter() - start) * 1000
            
            data = response.json()
            reality = data.get('reality', 'UNKNOWN')
            payload = str(data.get('data', ''))
            
            # Coloração baseada na realidade
            reality_color = {
                "PRIME": Colors.PRIME,
                "SHADOW": Colors.SHADOW,
                "MIRROR": Colors.MIRROR
            }.get(reality, Colors.INFO)
            
            print(f"  HTTP Status: {response.status_code}")
            print(f"  Realidade: {reality_color}{reality}{Colors.RESET}")
            print(f"  Latência: {latency:.2f}ms")
            print(f"  Payload: {payload[:80]}...")
            
            # Análise adicional
            pattern = ElpAnalyzer.detect_data_pattern(payload)
            if pattern != "Padrão normal":
                print(f"  {Colors.INFO}[ANÁLISE] {pattern}{Colors.RESET}")
            
            result = AttackResult(
                scenario=scenario,
                mask=mask,
                mask_binary=mask_bin,
                is_valid_mask=is_valid,
                http_status=response.status_code,
                reality=reality,
                payload_preview=payload[:100],
                latency_ms=latency,
                headers_used=headers,
                success=(reality == "PRIME")
            )
            
            self.results.append(result)
            return result
            
        except requests.exceptions.ConnectionError:
            print(f"  {Colors.SHADOW}[ERRO] Servidor não acessível{Colors.RESET}")
            print(f"  Dica: Execute o servidor middleware primeiro")
            return None
        except Exception as e:
            print(f"  {Colors.SHADOW}[ERRO] {e}{Colors.RESET}")
            return None
    
    def timing_attack_analysis(self, mask: int, samples: int = TIMING_SAMPLES):
        """Análise estatística de timing para detectar jittering"""
        print(f"\n{Colors.BOLD}[ANÁLISE DE TIMING - {samples} amostras]{Colors.RESET}")
        print(f"  Objetivo: Detectar se o jittering realmente impede timing attacks")
        
        latencies = []
        for i in range(samples):
            headers = self.generate_headers(mask)
            try:
                start = time.perf_counter()
                response = requests.get(TARGET_URL, headers=headers, timeout=5)
                latency = (time.perf_counter() - start) * 1000
                latencies.append(latency)
                print(f"  [{i+1:2d}/{samples}] {latency:.2f}ms", end='\r')
            except:
                continue
        
        if not latencies:
            print("\n  Falha na coleta de amostras")
            return
        
        stats = ElpAnalyzer.analyze_timing(latencies)
        print(f"\n  Média: {stats['mean']:.2f}ms")
        print(f"  Mediana: {stats['median']:.2f}ms")
        print(f"  Desvio Padrão: {stats['stddev']:.2f}ms")
        print(f"  Range (Max-Min): {stats['range']:.2f}ms")
        
        # Avaliação da eficácia do jittering
        cv = (stats['stddev'] / stats['mean']) * 100  # Coeficiente de variação
        print(f"\n  Coeficiente de Variação: {cv:.2f}%")
        
        if cv > 10:
            print(f"  {Colors.PRIME}✓ Jittering eficaz (CV > 10%){Colors.RESET}")
        else:
            print(f"  {Colors.SHADOW}✗ Jittering insuficiente (CV < 10%){Colors.RESET}")
            print(f"  {Colors.INFO}[RECOMENDAÇÃO] Aumentar o range de delay aleatório{Colors.RESET}")

# ==================== SUITE DE TESTES ====================
def run_attack_suite():
    """Executa bateria completa de testes de segurança"""
    
    print(f"""
{Colors.BOLD}{'='*70}
ELP-Ω SECURITY TESTING SUITE
{'='*70}{Colors.RESET}
Target: {TARGET_URL}
Secret: {SECRET_KEY.decode('utf-8')}
""")
    
    attacker = ElpAttacker(SECRET_KEY)
    
    # ==================== TESTE 1: Acesso Legítimo ====================
    print(f"\n{Colors.BOLD}[CATEGORIA 1: ACESSOS LEGÍTIMOS]{Colors.RESET}")
    attacker.execute_attack("Usuário Autorizado", mask=5)   # 101
    attacker.execute_attack("Usuário Autorizado", mask=9)   # 1001
    attacker.execute_attack("Admin Privilegiado", mask=21)  # 10101
    
    # ==================== TESTE 2: Violações Matemáticas ====================
    print(f"\n{Colors.BOLD}[CATEGORIA 2: VIOLAÇÕES DE ZECKENDORF]{Colors.RESET}")
    attacker.execute_attack("Bits Adjacentes (110)", mask=6)   # 110
    attacker.execute_attack("Bits Adjacentes (111)", mask=7)   # 111
    attacker.execute_attack("Bits Adjacentes (1110)", mask=14) # 1110
    
    # ==================== TESTE 3: Ataques Criptográficos ====================
    print(f"\n{Colors.BOLD}[CATEGORIA 3: ATAQUES CRIPTOGRÁFICOS]{Colors.RESET}")
    attacker.execute_attack(
        "Assinatura Forjada (Bit Flip)",
        mask=5,
        corrupt_signature=True
    )
    
    attacker.execute_attack(
        "Timestamp Expirado (Clock Skew)",
        mask=5,
        corrupt_timestamp=True
    )
    
    # ==================== TESTE 4: Replay Attack ====================
    print(f"\n{Colors.BOLD}[CATEGORIA 4: REPLAY ATTACK]{Colors.RESET}")
    valid_headers = attacker.generate_headers(mask=5)
    
    # Primeira requisição (deve funcionar)
    print("  [1/2] Enviando requisição original...")
    try:
        r1 = requests.get(TARGET_URL, headers=valid_headers)
        print(f"  Resultado: {r1.json().get('reality')} (esperado: PRIME)")
    except:
        print("  Falha ao enviar requisição original")
    
    # Segunda requisição com mesmo nonce (deve falhar)
    print("  [2/2] Tentando replay com mesmo nonce...")
    try:
        time.sleep(0.5)
        r2 = requests.get(TARGET_URL, headers=valid_headers)
        reality2 = r2.json().get('reality')
        if reality2 == "SHADOW":
            print(f"  {Colors.PRIME}✓ Replay bloqueado com sucesso (SHADOW Reality){Colors.RESET}")
        else:
            print(f"  {Colors.SHADOW}✗ FALHA: Replay permitido! Reality: {reality2}{Colors.RESET}")
    except:
        print("  Falha ao testar replay")
    
    # ==================== TESTE 5: Análise de Timing ====================
    print(f"\n{Colors.BOLD}[CATEGORIA 5: TIMING ATTACK ANALYSIS]{Colors.RESET}")
    attacker.timing_attack_analysis(mask=5, samples=TIMING_SAMPLES)
    
    # ==================== RELATÓRIO FINAL ====================
    print(f"\n{Colors.BOLD}{'='*70}")
    print("RELATÓRIO FINAL")
    print(f"{'='*70}{Colors.RESET}")
    
    total = len(attacker.results)
    prime_count = sum(1 for r in attacker.results if r.reality == "PRIME")
    shadow_count = sum(1 for r in attacker.results if r.reality == "SHADOW")
    mirror_count = sum(1 for r in attacker.results if r.reality == "MIRROR")
    
    print(f"\nTotal de Ataques: {total}")
    print(f"  {Colors.PRIME}PRIME Reality: {prime_count}{Colors.RESET}")
    print(f"  {Colors.SHADOW}SHADOW Reality: {shadow_count}{Colors.RESET}")
    print(f"  {Colors.MIRROR}MIRROR Reality: {mirror_count}{Colors.RESET}")
    
    # Análise de eficácia
    invalid_masks = [r for r in attacker.results if not r.is_valid_mask]
    blocked = sum(1 for r in invalid_masks if r.reality == "SHADOW")
    
    if invalid_masks:
        effectiveness = (blocked / len(invalid_masks)) * 100
        print(f"\nEficácia de Bloqueio: {effectiveness:.1f}%")
        if effectiveness == 100:
            print(f"{Colors.PRIME}✓ Todas as violações foram corretamente encaminhadas para SHADOW{Colors.RESET}")
        else:
            print(f"{Colors.SHADOW}✗ Algumas violações vazaram para PRIME/MIRROR{Colors.RESET}")
    
    # Latências médias por realidade
    latencies_by_reality = {}
    for r in attacker.results:
        if r.reality not in latencies_by_reality:
            latencies_by_reality[r.reality] = []
        latencies_by_reality[r.reality].append(r.latency_ms)
    
    print("\nLatências Médias por Realidade:")
    for reality, lats in latencies_by_reality.items():
        avg = statistics.mean(lats)
        color = {
            "PRIME": Colors.PRIME,
            "SHADOW": Colors.SHADOW,
            "MIRROR": Colors.MIRROR
        }.get(reality, Colors.INFO)
        print(f"  {color}{reality}: {avg:.2f}ms{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

# ==================== EXECUÇÃO ====================
if __name__ == "__main__":
    try:
        run_attack_suite()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.INFO}[INFO] Testes interrompidos pelo usuário{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.SHADOW}[ERRO FATAL] {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()