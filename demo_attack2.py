#!/usr/bin/env python3
"""
ELP-Ω Advanced Security Testing Suite v2.1 (BUGFIX)
Testa: Timing Attacks, Shadow Detection, Payload Analysis, Statistical Fingerprinting
Autor: Claude (Adversarial Mode - Debugged Edition)
"""

import requests
import hmac
import hashlib
import base64
import time
import uuid
import json
import statistics
import math
import re
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter

# ==================== CONFIGURAÇÃO ====================
TARGET_URL = "http://127.0.0.1:8000/api/v1/resource"
SECRET_KEY = b"SUA_CHAVE_MESTRA_AQUI"
TIMING_SAMPLES = 50
CONFIDENCE_LEVEL = 0.95

# ==================== CORES ANSI ====================
class Colors:
    PRIME = "\033[92m"
    SHADOW = "\033[91m"
    MIRROR = "\033[93m"
    INFO = "\033[94m"
    WARNING = "\033[95m"
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
    payload_raw: dict
    payload_preview: str
    latency_ms: float
    headers_used: Dict[str, str]
    success: bool
    notes: str = ""
    entropy: float = 0.0
    pattern_score: float = 0.0

# ==================== ANALISADOR FORENSE ====================
class ForensicAnalyzer:
    """Análise forense avançada de payloads para detectar Shadow Reality"""
    
    @staticmethod
    def calculate_entropy(data: str) -> float:
        """Calcula entropia de Shannon (bits por caractere) - VERSÃO CORRIGIDA"""
        if not data:
            return 0.0
        
        freq = Counter(data)
        total = len(data)
        
        # Calcula entropia usando logaritmo base 2
        entropy = 0.0
        for count in freq.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    @staticmethod
    def detect_synthetic_patterns(payload: dict) -> Dict[str, any]:
        """Detecta padrões que indicam dados sintéticos"""
        indicators = {
            "has_shadow_markers": False,
            "suspicious_fields": [],
            "entropy_scores": {},
            "pattern_anomalies": [],
            "deterministic_score": 0.0,
            "field_analysis": {}
        }
        
        try:
            # Converte para string para análise
            payload_str = json.dumps(payload, sort_keys=True)
            
            # 1. Detecta marcadores explícitos de Shadow
            shadow_keywords = ['shadow', 'fake', 'synthetic', 'vault_id', 'vault', 'encrypted', 'dummy', 'test']
            for keyword in shadow_keywords:
                if keyword.lower() in payload_str.lower():
                    indicators["has_shadow_markers"] = True
                    indicators["suspicious_fields"].append(keyword)
            
            # 2. Analisa entropia de cada campo string
            for key, value in payload.items():
                if isinstance(value, str) and len(value) > 5:
                    entropy = ForensicAnalyzer.calculate_entropy(value)
                    indicators["entropy_scores"][key] = entropy
                    indicators["field_analysis"][key] = {
                        "entropy": entropy,
                        "length": len(value),
                        "unique_chars": len(set(value))
                    }
                    
                    # Dados reais tendem a ter entropia > 3.5
                    # Dados muito uniformes (baixa entropia) são suspeitos
                    if entropy < 2.5 and len(value) > 10:
                        indicators["pattern_anomalies"].append(
                            f"{key}: entropia baixa ({entropy:.2f})"
                        )
                    
                    # Dados com entropia muito alta (> 4.5) também podem ser suspeitos
                    # (ex: base64 random, hash, etc)
                    if entropy > 4.5 and len(value) > 20:
                        indicators["pattern_anomalies"].append(
                            f"{key}: entropia muito alta ({entropy:.2f}) - possível dado gerado"
                        )
            
            # 3. Detecta sequências numéricas "redondas"
            numbers = re.findall(r'\b\d+\b', payload_str)
            if len(numbers) > 2:
                rounded = sum(1 for n in numbers if len(n) > 2 and (int(n) % 1000 == 0 or int(n) % 100 == 0))
                if (rounded / len(numbers)) > 0.3:
                    indicators["pattern_anomalies"].append(
                        f"Números redondos suspeitos: {rounded}/{len(numbers)}"
                    )
            
            # 4. Detecta estruturas muito similares entre campos
            if len(payload) > 1:
                string_values = [str(v) for v in payload.values() if isinstance(v, (str, int, float))]
                if len(string_values) > 2:
                    lengths = [len(str(v)) for v in string_values]
                    if len(set(lengths)) == 1:  # Todos os campos têm o mesmo tamanho
                        indicators["pattern_anomalies"].append(
                            "Campos com tamanhos idênticos (geração template-based)"
                        )
            
            # 5. Calcula score de determinismo (0-1)
            score = 0.0
            if indicators["has_shadow_markers"]:
                score += 0.6  # Marcadores explícitos são muito suspeitos
            if len(indicators["suspicious_fields"]) > 2:
                score += 0.2
            if len(indicators["pattern_anomalies"]) > 0:
                score += 0.1 * min(len(indicators["pattern_anomalies"]), 2)
            
            indicators["deterministic_score"] = min(score, 1.0)
            
        except Exception as e:
            indicators["error"] = str(e)
        
        return indicators
    
    @staticmethod
    def statistical_timing_attack(latencies_prime: List[float], latencies_shadow: List[float]) -> Dict:
        """Teste t de Student para detectar diferença estatisticamente significativa"""
        if len(latencies_prime) < 2 or len(latencies_shadow) < 2:
            return {
                "distinguishable": False, 
                "reason": f"Amostras insuficientes (Prime: {len(latencies_prime)}, Shadow: {len(latencies_shadow)})",
                "t_statistic": 0,
                "mean_prime": 0,
                "mean_shadow": 0,
                "difference_ms": 0,
                "confidence": "N/A"
            }
        
        mean_prime = statistics.mean(latencies_prime)
        mean_shadow = statistics.mean(latencies_shadow)
        std_prime = statistics.stdev(latencies_prime) if len(latencies_prime) > 1 else 0
        std_shadow = statistics.stdev(latencies_shadow) if len(latencies_shadow) > 1 else 0
        
        # Teste t simples
        n1, n2 = len(latencies_prime), len(latencies_shadow)
        pooled_variance = (std_prime**2 / n1) + (std_shadow**2 / n2)
        pooled_std = math.sqrt(pooled_variance) if pooled_variance > 0 else 0.001
        
        t_stat = abs(mean_prime - mean_shadow) / pooled_std if pooled_std > 0 else 0
        
        # t crítico para 95% confiança ≈ 1.96
        distinguishable = t_stat > 1.96
        
        return {
            "distinguishable": distinguishable,
            "t_statistic": t_stat,
            "mean_prime": mean_prime,
            "mean_shadow": mean_shadow,
            "difference_ms": abs(mean_prime - mean_shadow),
            "difference_percent": abs(mean_prime - mean_shadow) / mean_prime * 100 if mean_prime > 0 else 0,
            "confidence": "95%" if distinguishable else "< 95%"
        }

# ==================== GERADOR DE ATAQUES ====================
class AdvancedElpAttacker:
    def __init__(self, secret: bytes):
        self.secret = secret
        self.nonce_history: List[str] = []
        self.results: List[AttackResult] = []
        self.latencies_by_reality: Dict[str, List[float]] = {
            "PRIME": [],
            "SHADOW": [],
            "MIRROR": []
        }
    
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
        
        if corrupt_timestamp:
            ts = ts - (1000 * 60 * 15)  # 15 minutos no passado
        
        payload = f"{mask}|{context}|{ts}|{path}|{n}"
        h = hmac.new(self.secret, payload.encode('utf-8'), hashlib.sha256)
        sig = base64.b64encode(h.digest()).decode('utf-8')
        
        if corrupt_signature:
            sig_bytes = base64.b64decode(sig)
            corrupted = bytearray(sig_bytes)
            corrupted[0] ^= 0xFF
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
        silent: bool = False,
        **header_kwargs
    ) -> Optional[AttackResult]:
        """Executa um ataque e analisa o resultado"""
        
        is_valid = (mask & (mask >> 1)) == 0
        headers = self.generate_headers(mask, **header_kwargs)
        
        if not silent:
            mask_bin = bin(mask)
            status = f"{Colors.PRIME}VÁLIDA{Colors.RESET}" if is_valid else f"{Colors.SHADOW}INVÁLIDA{Colors.RESET}"
            print(f"\n{Colors.BOLD}[ATAQUE: {scenario}]{Colors.RESET}")
            print(f"  Máscara: {mask} ({mask_bin}) -> {status}")
        
        try:
            start = time.perf_counter()
            response = requests.get(TARGET_URL, headers=headers, timeout=10)
            latency = (time.perf_counter() - start) * 1000
            
            data = response.json()
            reality = data.get('reality', 'UNKNOWN')
            
            # Análise forense do payload
            forensics = ForensicAnalyzer.detect_synthetic_patterns(data)
            
            # Calcula entropia média dos campos analisados
            entropy = 0.0
            if forensics["entropy_scores"]:
                entropy = statistics.mean(forensics["entropy_scores"].values())
            
            payload_str = json.dumps(data, indent=2)
            
            # Armazena latência por realidade
            if reality in self.latencies_by_reality:
                self.latencies_by_reality[reality].append(latency)
            
            if not silent:
                reality_color = {
                    "PRIME": Colors.PRIME,
                    "SHADOW": Colors.SHADOW,
                    "MIRROR": Colors.MIRROR
                }.get(reality, Colors.INFO)
                
                print(f"  HTTP Status: {response.status_code}")
                print(f"  Realidade: {reality_color}{reality}{Colors.RESET}")
                print(f"  Latência: {latency:.2f}ms")
                
                if entropy > 0:
                    print(f"  Entropia Média: {entropy:.2f} bits/char")
                
                # Alertas de detecção
                if forensics["has_shadow_markers"]:
                    print(f"  {Colors.WARNING}⚠ DETECTADO: Marcadores explícitos ({', '.join(forensics['suspicious_fields'][:3])}){Colors.RESET}")
                
                if forensics["pattern_anomalies"]:
                    print(f"  {Colors.WARNING}⚠ ANOMALIAS: {forensics['pattern_anomalies'][0]}{Colors.RESET}")
                
                if forensics["deterministic_score"] > 0.5:
                    print(f"  {Colors.WARNING}⚠ Shadow Detection Score: {forensics['deterministic_score']*100:.0f}%{Colors.RESET}")
            
            result = AttackResult(
                scenario=scenario,
                mask=mask,
                mask_binary=bin(mask),
                is_valid_mask=is_valid,
                http_status=response.status_code,
                reality=reality,
                payload_raw=data,
                payload_preview=payload_str[:150],
                latency_ms=latency,
                headers_used=headers,
                success=(reality == "PRIME"),
                entropy=entropy,
                pattern_score=forensics["deterministic_score"]
            )
            
            self.results.append(result)
            return result
            
        except requests.exceptions.Timeout:
            if not silent:
                print(f"  {Colors.SHADOW}[TIMEOUT] Servidor não respondeu em 10s{Colors.RESET}")
            return None
        except requests.exceptions.ConnectionError:
            if not silent:
                print(f"  {Colors.SHADOW}[ERRO] Servidor não acessível - verifique se está rodando{Colors.RESET}")
            return None
        except json.JSONDecodeError as e:
            if not silent:
                print(f"  {Colors.SHADOW}[ERRO] Resposta não é JSON válido: {e}{Colors.RESET}")
            return None
        except Exception as e:
            if not silent:
                print(f"  {Colors.SHADOW}[ERRO] {type(e).__name__}: {e}{Colors.RESET}")
            return None
    
    def advanced_timing_analysis(self):
        """Análise estatística avançada de timing attack"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print("[ANÁLISE FORENSE DE TIMING ATTACK]")
        print(f"{'='*70}{Colors.RESET}")
        
        # Coleta amostras de PRIME
        print(f"\n{Colors.INFO}[1/2] Coletando {TIMING_SAMPLES} amostras de PRIME Reality...{Colors.RESET}")
        prime_latencies = []
        for i in range(TIMING_SAMPLES):
            result = self.execute_attack(f"Prime Sample {i+1}", mask=5, silent=True)
            if result and result.reality == "PRIME":
                prime_latencies.append(result.latency_ms)
            print(f"  Progresso: [{i+1}/{TIMING_SAMPLES}] | Coletadas: {len(prime_latencies)}", end='\r')
        
        # Coleta amostras de SHADOW
        print(f"\n{Colors.INFO}[2/2] Coletando {TIMING_SAMPLES} amostras de SHADOW Reality...{Colors.RESET}")
        shadow_latencies = []
        for i in range(TIMING_SAMPLES):
            result = self.execute_attack(f"Shadow Sample {i+1}", mask=6, silent=True)
            if result and result.reality == "SHADOW":
                shadow_latencies.append(result.latency_ms)
            print(f"  Progresso: [{i+1}/{TIMING_SAMPLES}] | Coletadas: {len(shadow_latencies)}", end='\r')
        
        print("\n")
        
        if len(prime_latencies) < 5 or len(shadow_latencies) < 5:
            print(f"{Colors.SHADOW}[FALHA] Amostras insuficientes: PRIME={len(prime_latencies)}, SHADOW={len(shadow_latencies)}{Colors.RESET}")
            print(f"{Colors.INFO}Verifique se o servidor está retornando as realidades corretas{Colors.RESET}")
            return
        
        # Estatísticas descritivas
        print(f"{Colors.BOLD}Estatísticas de PRIME Reality ({len(prime_latencies)} amostras):{Colors.RESET}")
        print(f"  Média: {statistics.mean(prime_latencies):.2f}ms")
        print(f"  Mediana: {statistics.median(prime_latencies):.2f}ms")
        print(f"  Desvio Padrão: {statistics.stdev(prime_latencies):.2f}ms")
        print(f"  Min/Max: {min(prime_latencies):.2f}ms / {max(prime_latencies):.2f}ms")
        
        print(f"\n{Colors.BOLD}Estatísticas de SHADOW Reality ({len(shadow_latencies)} amostras):{Colors.RESET}")
        print(f"  Média: {statistics.mean(shadow_latencies):.2f}ms")
        print(f"  Mediana: {statistics.median(shadow_latencies):.2f}ms")
        print(f"  Desvio Padrão: {statistics.stdev(shadow_latencies):.2f}ms")
        print(f"  Min/Max: {min(shadow_latencies):.2f}ms / {max(shadow_latencies):.2f}ms")
        
        # Teste de distinguibilidade estatística
        timing_test = ForensicAnalyzer.statistical_timing_attack(prime_latencies, shadow_latencies)
        
        print(f"\n{Colors.BOLD}Teste de Distinguibilidade (Teste t de Student):{Colors.RESET}")
        print(f"  Estatística t: {timing_test['t_statistic']:.3f}")
        print(f"  Diferença absoluta: {timing_test['difference_ms']:.2f}ms ({timing_test['difference_percent']:.1f}%)")
        print(f"  Nível de confiança: {timing_test['confidence']}")
        
        if timing_test['distinguishable']:
            print(f"\n  {Colors.SHADOW}✗ VULNERÁVEL A TIMING ATTACK{Colors.RESET}")
            print(f"  {Colors.WARNING}Um atacante pode distinguir PRIME de SHADOW com {timing_test['confidence']} de confiança{Colors.RESET}")
            print(f"  {Colors.INFO}Recomendação: Aumentar variação de jitter para CV > 15%{Colors.RESET}")
        else:
            print(f"\n  {Colors.PRIME}✓ RESISTENTE A TIMING ATTACK{Colors.RESET}")
            print(f"  {Colors.PRIME}Distribuições estatisticamente indistinguíveis{Colors.RESET}")
        
        # Calcula Coeficiente de Variação
        all_latencies = prime_latencies + shadow_latencies
        if all_latencies:
            cv_combined = (statistics.stdev(all_latencies) / statistics.mean(all_latencies)) * 100
            print(f"\n  Coeficiente de Variação (geral): {cv_combined:.2f}%")
            
            if cv_combined > 15:
                print(f"  {Colors.PRIME}✓ Jittering eficaz (CV > 15%){Colors.RESET}")
            elif cv_combined > 10:
                print(f"  {Colors.WARNING}⚠ Jittering moderado (10% < CV < 15%){Colors.RESET}")
            else:
                print(f"  {Colors.SHADOW}✗ Jittering insuficiente (CV < 10%){Colors.RESET}")
    
    def payload_fingerprinting_analysis(self):
        """Analisa se payloads de Shadow são distinguíveis de Prime"""
        print(f"\n{Colors.BOLD}{'='*70}")
        print("[ANÁLISE DE FINGERPRINTING DE PAYLOAD]")
        print(f"{'='*70}{Colors.RESET}")
        
        shadow_results = [r for r in self.results if r.reality == "SHADOW" and not r.scenario.startswith("Shadow Sample")]
        
        if not shadow_results:
            print("Nenhuma resposta Shadow detectada nos testes principais")
            return
        
        print(f"\nAnalisando {len(shadow_results)} payloads de SHADOW Reality...")
        
        shadow_detected = 0
        detection_details = []
        
        for result in shadow_results:
            if result.pattern_score > 0.5:
                shadow_detected += 1
                detection_details.append({
                    "scenario": result.scenario,
                    "score": result.pattern_score,
                    "entropy": result.entropy
                })
        
        if detection_details:
            print(f"\n{Colors.WARNING}Payloads detectáveis como Shadow:{Colors.RESET}")
            for detail in detection_details[:3]:  # Mostra até 3
                print(f"  • {detail['scenario']}: Score {detail['score']*100:.0f}%, Entropia {detail['entropy']:.2f}")
        
        detection_rate = (shadow_detected / len(shadow_results)) * 100
        
        print(f"\n{Colors.BOLD}Taxa de Detecção de Shadow: {detection_rate:.1f}%{Colors.RESET}")
        
        if detection_rate > 50:
            print(f"{Colors.SHADOW}✗ PAYLOADS SHADOW SÃO FACILMENTE DISTINGUÍVEIS{Colors.RESET}")
            print(f"{Colors.INFO}Recomendação: Remover marcadores e melhorar geração de dados sintéticos{Colors.RESET}")
        elif detection_rate > 20:
            print(f"{Colors.WARNING}⚠ ALGUNS PAYLOADS SHADOW SÃO DETECTÁVEIS{Colors.RESET}")
            print(f"{Colors.INFO}Recomendação: Revisar campos com baixa/alta entropia{Colors.RESET}")
        else:
            print(f"{Colors.PRIME}✓ PAYLOADS SHADOW SÃO INDISTINGUÍVEIS{Colors.RESET}")

# ==================== SUITE DE TESTES ====================
def run_advanced_attack_suite():
    """Executa bateria completa de ataques forenses"""
    
    print(f"""
{Colors.BOLD}{'='*70}
ELP-Ω ADVANCED SECURITY TESTING SUITE v2.1
Modo: Adversarial Analysis (Red Team)
{'='*70}{Colors.RESET}
Target: {TARGET_URL}
""")
    
    attacker = AdvancedElpAttacker(SECRET_KEY)
    
    # Testes básicos
    print(f"\n{Colors.BOLD}[CATEGORIA 1: BASELINE - ACESSOS LEGÍTIMOS]{Colors.RESET}")
    attacker.execute_attack("Usuário Autorizado", mask=5)
    attacker.execute_attack("Admin Privilegiado", mask=21)
    
    print(f"\n{Colors.BOLD}[CATEGORIA 2: VIOLAÇÕES MATEMÁTICAS]{Colors.RESET}")
    attacker.execute_attack("Bits Adjacentes (110)", mask=6)
    attacker.execute_attack("Bits Adjacentes (111)", mask=7)
    attacker.execute_attack("Bits Adjacentes (1110)", mask=14)
    
    print(f"\n{Colors.BOLD}[CATEGORIA 3: ATAQUES CRIPTOGRÁFICOS]{Colors.RESET}")
    attacker.execute_attack("Assinatura Corrompida", mask=5, corrupt_signature=True)
    attacker.execute_attack("Timestamp Expirado", mask=5, corrupt_timestamp=True)
    
    print(f"\n{Colors.BOLD}[CATEGORIA 4: REPLAY ATTACK]{Colors.RESET}")
    valid_headers = attacker.generate_headers(mask=5)
    print("  [1/2] Enviando requisição original...")
    try:
        r1 = requests.get(TARGET_URL, headers=valid_headers, timeout=5)
        reality1 = r1.json().get('reality', 'UNKNOWN')
        print(f"  Resultado: {reality1} (esperado: PRIME)")
    except Exception as e:
        print(f"  Erro: {e}")
        reality1 = None
    
    print("  [2/2] Tentando replay com mesmo nonce...")
    try:
        time.sleep(0.5)
        r2 = requests.get(TARGET_URL, headers=valid_headers, timeout=5)
        reality2 = r2.json().get('reality', 'UNKNOWN')
        if reality2 == "SHADOW":
            print(f"  {Colors.PRIME}✓ Replay bloqueado (realidade: {reality2}){Colors.RESET}")
        else:
            print(f"  {Colors.SHADOW}✗ VULNERÁVEL: Replay permitido (realidade: {reality2})!{Colors.RESET}")
    except Exception as e:
        print(f"  Erro no replay: {e}")
    
    # Análises forenses avançadas
    attacker.advanced_timing_analysis()
    attacker.payload_fingerprinting_analysis()
    
    # Relatório final
    print(f"\n{Colors.BOLD}{'='*70}")
    print("RELATÓRIO EXECUTIVO")
    print(f"{'='*70}{Colors.RESET}")
    
    main_results = [r for r in attacker.results if not r.scenario.startswith("Prime Sample") and not r.scenario.startswith("Shadow Sample")]
    total = len(main_results)
    prime_count = sum(1 for r in main_results if r.reality == "PRIME")
    shadow_count = sum(1 for r in main_results if r.reality == "SHADOW")
    mirror_count = sum(1 for r in main_results if r.reality == "MIRROR")
    
    print(f"\nTotal de Ataques Principais: {total}")
    print(f"  {Colors.PRIME}PRIME: {prime_count}{Colors.RESET}")
    print(f"  {Colors.SHADOW}SHADOW: {shadow_count}{Colors.RESET}")
    print(f"  {Colors.MIRROR}MIRROR: {mirror_count}{Colors.RESET}")
    
    invalid_masks = [r for r in main_results if not r.is_valid_mask]
    if invalid_masks:
        blocked = sum(1 for r in invalid_masks if r.reality == "SHADOW")
        effectiveness = (blocked / len(invalid_masks)) * 100
        print(f"\nEficácia de Bloqueio Matemático: {effectiveness:.1f}%")
        
        if effectiveness == 100:
            print(f"{Colors.PRIME}✓ Todas as violações Zeckendorf foram bloqueadas{Colors.RESET}")
        else:
            print(f"{Colors.SHADOW}✗ Algumas violações vazaram para PRIME/MIRROR{Colors.RESET}")
    
    # Latências médias
    if attacker.latencies_by_reality["PRIME"] and attacker.latencies_by_reality["SHADOW"]:
        print(f"\nLatências Médias:")
        for reality in ["PRIME", "SHADOW", "MIRROR"]:
            lats = attacker.latencies_by_reality[reality]
            if lats:
                avg = statistics.mean(lats)
                color = {"PRIME": Colors.PRIME, "SHADOW": Colors.SHADOW, "MIRROR": Colors.MIRROR}.get(reality, "")
                print(f"  {color}{reality}: {avg:.2f}ms{Colors.RESET}")
    
    print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}\n")

if __name__ == "__main__":
    try:
        run_advanced_attack_suite()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.INFO}[INFO] Análise interrompida{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.SHADOW}[ERRO FATAL] {type(e).__name__}: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()