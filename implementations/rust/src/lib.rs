use hmac::{Hmac, Mac};
use sha2::{Sha256, Digest};
use base64::{Engine as _, engine::general_purpose};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use serde_json::json;
// Adicionar rand no Cargo.toml se não tiver, ou usar pseudo-random simples
// Para manter sem deps extras pesadas, faremos um LCG simples baseado no hash

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Clone, PartialEq)]
pub enum Reality {
    Prime,
    Mirror,
    Shadow,
}

pub struct EntangledLogicOmega {
    secret: Vec<u8>,
    max_age_ms: u128,
    used_nonces: Arc<Mutex<HashMap<String, u128>>>,
}

impl EntangledLogicOmega {
    pub fn new(secret: &str) -> Self {
        EntangledLogicOmega {
            secret: secret.as_bytes().to_vec(),
            max_age_ms: 300_000, // 5 minutos
            used_nonces: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn is_valid_zeckendorf_mask(&self, mask: u32) -> bool {
        (mask & (mask >> 1)) == 0
    }

    pub fn compute_seal(&self, mask: u32, context: &str, timestamp: u128, path: &str, nonce: &str) -> String {
        let payload = format!("{}|{}|{}|{}|{}", mask, context, timestamp, path, nonce);
        let mut mac = HmacSha256::new_from_slice(&self.secret).expect("HMAC error");
        mac.update(payload.as_bytes());
        let result = mac.finalize();
        hex::encode(result.into_bytes())
    }

    // Retorna JSON Value para ser serializado
    pub fn generate_shadow(&self, context: &str, path: &str, nonce: &str) -> serde_json::Value {
        // Seed determinística baseada no hash da requisição
        let seed_str = format!("{}|{}|{}|{:?}", path, context, nonce, self.secret);
        let mut hasher = Sha256::new();
        hasher.update(seed_str);
        let result = hasher.finalize();
        
        // Usa os primeiros bytes como seed para um LCG simples
        let mut seed = u64::from_be_bytes(result[0..8].try_into().unwrap());
        
        // Função auxiliar rand
        let mut rand_f64 = || {
            seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            (seed as f64) / (u64::MAX as f64)
        };

        let balance = (rand_f64() * 500_000.0).round();
        let acc_type = if rand_f64() > 0.5 { "checking" } else { "savings" };
        let processing_ms = (rand_f64() * 140.0) as u64 + 10;

        json!({
            "status": "success",
            "transaction_id": uuid::Uuid::new_v4().to_string(), // UUID random é aceitável
            "timestamp": SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis() as u64,
            "data": {
                "account_type": acc_type,
                "balance": balance,
                "currency": "BRL",
                "flags": ["verified", "secure"]
            },
            "meta": {
                "processing_time_ms": processing_ms,
                "region": "sa-east-1"
            }
        })
    }

    pub fn process_request(
        &self, 
        mask: u32, 
        seal: &str, 
        context: &str, 
        timestamp: u128, 
        path: &str, 
        nonce: &str
    ) -> (serde_json::Value, Reality) {
        
        let mut is_shadow = false;

        // 1. Validação Topológica
        if !self.is_valid_zeckendorf_mask(mask) { is_shadow = true; }

        // 2. Freshness
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis();
        if !is_shadow && (now < timestamp || (now - timestamp) > self.max_age_ms) {
            is_shadow = true;
        }

        // 3. HMAC
        if !is_shadow {
            let expected = self.compute_seal(mask, context, timestamp, path, nonce);
            if seal != expected { is_shadow = true; }
        }

        // 4. Nonce
        if !is_shadow {
            let mut nonces = self.used_nonces.lock().unwrap();
            if nonces.contains_key(nonce) {
                is_shadow = true;
            } else {
                nonces.insert(nonce.to_string(), now);
            }
        }

        if is_shadow {
            // Retorna Shadow Payload (Stealth)
            return (self.generate_shadow(context, path, nonce), Reality::Shadow);
        }

        // Retorna Prime Reality (Simulação de sucesso)
        (json!({"data": "PRIME_REALITY_DATA"}), Reality::Prime)
    }
}