use hmac::{Hmac, Mac};
use sha2::Sha256;
use base64::{Engine as _, engine::general_purpose};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

// Definição dos Tipos
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
    max_failures: u32,
    used_nonces: Arc<Mutex<HashMap<String, u128>>>,
    failures: Arc<Mutex<HashMap<String, (u32, u128)>>>,
}

impl EntangledLogicOmega {
    pub fn new(secret: &str) -> Self {
        EntangledLogicOmega {
            secret: secret.as_bytes().to_vec(),
            max_age_ms: 300_000, // 5 minutos
            max_failures: 5,
            used_nonces: Arc::new(Mutex::new(HashMap::new())),
            failures: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Valida a Constraint de Zeckendorf (Bitwise O(1))
    /// Retorna true se não houver bits adjacentes ativos
    pub fn is_valid_zeckendorf_mask(&self, mask: u32) -> bool {
        (mask & (mask >> 1)) == 0
    }

    /// Gera o Selo HMAC para integridade
    pub fn compute_seal(&self, mask: u32, context: &str, timestamp: u128, path: &str, nonce: &str) -> String {
        let payload = format!("{}|{}|{}|{}|{}", mask, context, timestamp, path, nonce);
        let mut mac = HmacSha256::new_from_slice(&self.secret).expect("HMAC can take key of any size");
        mac.update(payload.as_bytes());
        let result = mac.finalize();
        general_purpose::STANDARD.encode(result.into_bytes())
    }

    /// Processa a requisição e define a Realidade de resposta
    pub fn process_request(
        &self, 
        mask: u32, 
        seal: &str, 
        context: &str, 
        timestamp: u128, 
        path: &str, 
        nonce: &str,
        real_data: &str,
        fingerprint: &str
    ) -> (String, Reality) {
        
        // 1. Validação Topológica (Zeckendorf)
        if !self.is_valid_zeckendorf_mask(mask) {
            return (self.generate_shadow(real_data, context, path), Reality::Shadow);
        }

        // 2. Freshness Check (Timestamp)
        let start = SystemTime::now();
        let since_the_epoch = start
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards")
            .as_millis();

        // Verifica se o timestamp está no futuro ou muito no passado
        if timestamp > since_the_epoch || (since_the_epoch - timestamp) > self.max_age_ms {
            return (self.sanitize(real_data), Reality::Mirror);
        }

        // 3. Validação Criptográfica (HMAC)
        let expected_seal = self.compute_seal(mask, context, timestamp, path, nonce);
        if seal != expected_seal {
            return self.handle_failure(fingerprint, real_data, context, path);
        }

        // 4. Anti-Replay (Nonce)
        let mut nonces = self.used_nonces.lock().unwrap();
        if nonces.contains_key(nonce) {
            return (self.generate_shadow(real_data, context, path), Reality::Shadow);
        }
        nonces.insert(nonce.to_string(), since_the_epoch);

        (format!("PRIME_REALITY: {}", real_data), Reality::Prime)
    }

    fn handle_failure(&self, fingerprint: &str, data: &str, ctx: &str, path: &str) -> (String, Reality) {
        let start = SystemTime::now();
        let now = start.duration_since(UNIX_EPOCH).unwrap().as_millis();
        
        let mut fails = self.failures.lock().unwrap();
        let record = fails.entry(fingerprint.to_string()).or_insert((0, now));

        // Reset se passou mais de 1 hora
        if now - record.1 > 3600_000 {
            *record = (1, now);
        } else {
            record.0 += 1;
        }

        if record.0 > self.max_failures {
            (self.generate_shadow(data, ctx, path), Reality::Shadow)
        } else {
            (self.sanitize(data), Reality::Mirror)
        }
    }

    fn sanitize(&self, data: &str) -> String {
        // Simples regex replacement simulation
        let no_digits: String = data.chars().map(|c| if c.is_numeric() { '*' } else { c }).collect();
        no_digits.replace("senha=", "senha=********")
    }

    fn generate_shadow(&self, real_data: &str, context: &str, path: &str) -> String {
        let seed = format!("SHADOW|{}|{}|STABILITY|{}", path, context, real_data.len());
        let mut mac = HmacSha256::new_from_slice(&self.secret).expect("HMAC error");
        mac.update(seed.as_bytes());
        let result = mac.finalize();
        let hash = general_purpose::URL_SAFE_NO_PAD.encode(result.into_bytes());
        
        format!("SHADOW_VAULT_ID:{}:DATA_ENCRYPTED", &hash[..16])
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_zeckendorf_validation() {
        let elp = EntangledLogicOmega::new("test_secret");
        assert!(elp.is_valid_zeckendorf_mask(5)); // 101 -> OK
        assert!(!elp.is_valid_zeckendorf_mask(6)); // 110 -> Fail
    }
}