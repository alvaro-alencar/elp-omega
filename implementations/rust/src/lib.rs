use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};
use base64::{engine::general_purpose, Engine as _};

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, PartialEq, Clone)]
pub enum Reality {
    Prime,
    Mirror,
    Shadow,
}

pub struct SecureRequest {
    pub mask: i32,
    pub seal: String,
    pub context: String,
    pub timestamp: u64,
    pub path: String,
    pub nonce: String,
}

pub struct EntangledLogicOmega {
    secret: Vec<u8>,
    max_age_ms: u64,
    max_failures: u32,
    used_nonces: Arc<Mutex<HashMap<String, u64>>>,
    failures: Arc<Mutex<HashMap<String, u32>>>,
}

impl EntangledLogicOmega {
    pub fn new(secret: Vec<u8>, max_age_ms: u64, max_failures: u32) -> Self {
        Self {
            secret,
            max_age_ms,
            max_failures,
            used_nonces: Arc::new(Mutex::new(HashMap::new())),
            failures: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn is_valid_zeckendorf_mask(&self, mask: i32) -> bool {
        if mask < 0 { return false; }
        // Constraint de não-adjacência: (mask & (mask >> 1)) == 0
        (mask & (mask >> 1)) == 0
    }

    pub fn compute_seal(&self, req: &SecureRequest) -> String {
        let mut mac = HmacSha256::new_from_slice(&self.secret)
            .expect("HMAC can take key of any size");
        let payload = format!("{}|{}|{}|{}|{}", req.mask, req.context, req.timestamp, req.path, req.nonce);
        mac.update(payload.as_bytes());
        general_purpose::STANDARD.encode(mac.finalize().into_bytes())
    }

    pub fn process_request(&self, req: SecureRequest, real_data: &str, fingerprint: &str) -> (String, Reality) {
        // 1. Validação de Máscara
        if !self.is_valid_zeckendorf_mask(req.mask) {
            return (self.generate_shadow(real_data, &req.context, &req.path), Reality::Shadow);
        }

        // 2. Check de Freshness
        let now = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_millis() as u64;
        if now.saturating_sub(req.timestamp) > self.max_age_ms {
            return (self.sanitize(real_data), Reality::Mirror);
        }

        // 3. Validação do Selo (HMAC)
        let expected_seal = self.compute_seal(&req);
        if req.seal != expected_seal {
            return self.handle_failure(fingerprint, real_data, &req.context, &req.path);
        }

        // 4. Anti-Replay (Nonce)
        let mut nonces = self.used_nonces.lock().unwrap();
        if nonces.contains_key(&req.nonce) {
            return (self.generate_shadow(real_data, &req.context, &req.path), Reality::Shadow);
        }
        nonces.insert(req.nonce.clone(), now);

        (format!("PRIME_REALITY: {}", real_data), Reality::Prime)
    }

    fn handle_failure(&self, fp: &str, data: &str, ctx: &str, path: &str) -> (String, Reality) {
        let mut fails = self.failures.lock().unwrap();
        let count = fails.entry(fp.to_string()).or_insert(0);
        *count += 1;

        if *count > self.max_failures {
            (self.generate_shadow(data, ctx, path), Reality::Shadow)
        } else {
            (self.sanitize(data), Reality::Mirror)
        }
    }

    fn sanitize(&self, data: &str) -> String {
        // Sanitização básica: oculta números (ex: CPFs, saldos)
        data.chars().map(|c| if c.is_numeric() { '*' } else { c }).collect()
    }

    fn generate_shadow(&self, real_data: &str, ctx: &str, path: &str) -> String {
        let mut mac = HmacSha256::new_from_slice(&self.secret).unwrap();
        let seed = format!("SHADOW|{}|{}|{}", path, ctx, real_data.len());
        mac.update(seed.as_bytes());
        let hash = hex::encode(&mac.finalize().into_bytes()[..8]);
        format!("SHADOW_VAULT_ID:{}:ENCRYPTED", hash)
    }
}