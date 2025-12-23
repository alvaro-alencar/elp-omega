import unittest
import time
import base64
import hmac
import hashlib
from elp_omega import EntangledLogicOmegaV5, Reality

class TestELPOmega(unittest.TestCase):
    def setUp(self):
        self.secret = b"vortex-test-secret"
        self.elp = EntangledLogicOmegaV5(self.secret, max_failures=2)

    def test_zeckendorf_validation(self):
        """Testa a regra de não-adjacência de Fibonacci."""
        # Válidos
        self.assertTrue(self.elp.is_valid_zeckendorf_mask(0b1001)) # 1 e 8
        self.assertTrue(self.elp.is_valid_zeckendorf_mask(0b10101))
        # Inválidos (bits adjacentes)
        self.assertFalse(self.elp.is_valid_zeckendorf_mask(0b0011))
        self.assertFalse(self.elp.is_valid_zeckendorf_mask(0b0110))

    def test_prime_reality_success(self):
        """Testa o fluxo de sucesso total (PRIME)."""
        mask = 0b1001
        ts = int(time.time() * 1000)
        nonce = "unique-nonce-1"
        path = "/api/test"
        context = "unit-test"
        
        seal = self.elp.compute_seal(mask, context, ts, path, nonce)
        req = {
            "mask": mask, "seal": seal, "context": context,
            "timestamp": ts, "path": path, "nonce": nonce
        }
        
        data, reality = self.elp.process_request(req, "SECRET_INFO", "fp-1")
        self.assertEqual(reality, Reality.PRIME)
        self.assertIn("SECRET_INFO", data)

    def test_shadow_reality_on_adjacent_bits(self):
        """Testa se bits adjacentes jogam o atacante para SHADOW."""
        req = {"mask": 0b0011} # Inválido
        data, reality = self.elp.process_request(req, "REAL_DATA", "fp-2")
        self.assertEqual(reality, Reality.SHADOW)
        self.assertIn("SHADOW_VAULT_ID", data)

    def test_replay_attack_prevention(self):
        """Testa a proteção contra reutilização de Nonce."""
        mask = 0b1
        ts = int(time.time() * 1000)
        nonce = "replay-me"
        seal = self.elp.compute_seal(mask, "ctx", ts, "/path", nonce)
        req = {"mask": mask, "seal": seal, "context": "ctx", "timestamp": ts, "path": "/path", "nonce": nonce}

        # Primeira vez: PRIME
        _, r1 = self.elp.process_request(req, "DATA", "fp-3")
        self.assertEqual(r1, Reality.PRIME)

        # Segunda vez com mesmo nonce: SHADOW
        _, r2 = self.elp.process_request(req, "DATA", "fp-3")
        self.assertEqual(r2, Reality.SHADOW)

    def test_rate_limiting_to_shadow(self):
        """Testa a transição de MIRROR para SHADOW após falhas repetidas."""
        req = {
            "mask": 1, "seal": "wrong-seal", "context": "ctx",
            "timestamp": int(time.time() * 1000), "path": "/path", "nonce": "n"
        }
        fp = "attacker-ip"

        # Falha 1 e 2: MIRROR
        _, r1 = self.elp.process_request(req, "DATA", fp)
        _, r2 = self.elp.process_request(req, "DATA", fp)
        self.assertEqual(r1, Reality.MIRROR)
        self.assertEqual(r2, Reality.MIRROR)

        # Falha 3 (excede max_failures=2): SHADOW
        req["nonce"] = "new-n"
        _, r3 = self.elp.process_request(req, "DATA", fp)
        self.assertEqual(r3, Reality.SHADOW)

if __name__ == "__main__":
    unittest.main()