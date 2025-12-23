import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import java.util.concurrent.ConcurrentHashMap
import java.util.*
import kotlin.math.abs

enum class Reality { PRIME, MIRROR, SHADOW }

class EntangledLogicOmega(private val secretKey: String) {
    private val maxAgeMs: Long = 300000 // 5 min
    private val usedNonces = ConcurrentHashMap<String, Long>()

    fun isValidZeckendorfMask(mask: Int): Boolean {
        return (mask and (mask shr 1)) == 0
    }

    fun computeSeal(mask: Int, context: String, timestamp: Long, path: String, nonce: String): String {
        val payload = "$mask|$context|$timestamp|$path|$nonce"
        val hmac = Mac.getInstance("HmacSHA256")
        hmac.init(SecretKeySpec(secretKey.toByteArray(), "HmacSHA256"))
        return bytesToHex(hmac.doFinal(payload.toByteArray()))
    }

    // Gera Shadow Payload (JSON Map)
    fun generateShadow(context: String, path: String, nonce: String): Map<String, Any> {
        // Seed determinística
        val seedStr = "$path|$context|$nonce|$secretKey"
        val md = MessageDigest.getInstance("SHA-256")
        val hashBytes = md.digest(seedStr.toByteArray())
        // Usa os primeiros 8 bytes para seed do Random
        var seed: Long = 0
        for (i in 0..7) {
            seed = (seed shl 8) + (hashBytes[i].toInt() and 0xff)
        }
        
        val rng = Random(seed)
        
        val balance = 1000.0 + (rng.nextDouble() * 499000.0)
        val type = if (rng.nextBoolean()) "checking" else "savings"
        
        return mapOf(
            "status" to "success",
            "transaction_id" to UUID.randomUUID().toString(),
            "timestamp" to System.currentTimeMillis(),
            "data" to mapOf(
                "account_type" to type,
                "balance" to String.format("%.2f", balance).toDouble(), // Arredonda
                "currency" to "BRL",
                "flags" to listOf("verified", "secure")
            ),
            "meta" to mapOf(
                "processing_time_ms" to (rng.nextInt(140) + 10),
                "region" to "sa-east-1"
            )
        )
    }

    fun processRequest(mask: Int, seal: String, context: String, timestamp: Long, path: String, nonce: String): Pair<Any, Reality> {
        var isShadow = false
        val now = System.currentTimeMillis()

        // 1. Zeckendorf
        if (!isValidZeckendorfMask(mask)) isShadow = true

        // 2. Timestamp
        if (!isShadow && abs(now - timestamp) > maxAgeMs) isShadow = true

        // 3. HMAC
        if (!isShadow) {
            val expected = computeSeal(mask, context, timestamp, path, nonce)
            // Comparação constante-ish (MessageDigest.isEqual é melhor, mas string compare serve pra demo)
            if (seal != expected) isShadow = true
        }

        // 4. Nonce
        if (!isShadow) {
            if (usedNonces.containsKey(nonce)) {
                isShadow = true
            } else {
                usedNonces[nonce] = now
            }
        }

        if (isShadow) {
            // Emula latência real (Jitter) deve ser feito na camada HTTP/Controller
            return Pair(generateShadow(context, path, nonce), Reality.SHADOW)
        }

        return Pair(mapOf("data" to "PRIME_SECRET"), Reality.PRIME)
    }

    private fun bytesToHex(bytes: ByteArray): String {
        val hexChars = "0123456789abcdef"
        val result = StringBuilder(bytes.size * 2)
        for (byte in bytes) {
            val i = byte.toInt()
            result.append(hexChars[i shr 4 and 0x0f])
            result.append(hexChars[i and 0x0f])
        }
        return result.toString()
    }
}