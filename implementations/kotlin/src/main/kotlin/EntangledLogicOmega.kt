Import java.nio.charset.StandardCharsets
import java.util.Base64
import java.util.UUID
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.Executors
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec
import org.slf4j.LoggerFactory

/**
 * PROTOCOLO ELP-Ω v5 — ZECKENDORF-LIKE TRIPLE-REALITY
 *
 * Sistema de controle de acesso baseado em máscara de bits com restrição "não-adjacente"
 * (inspirada na ideia de não-consecutividade de Fibonacci).
 *
 * ARQUITETURA DE TRIPLE-REALITY:
 * - PRIME: Acesso legítimo completo aos dados reais
 * - MIRROR: Dados sanitizados (degradação graciosa)
 * - SHADOW: Dados falsos determinísticos (engana atacantes)
 *
 * @param secretProvider Provedor do segredo criptográfico (HMAC)
 * @param maxAgeMs Janela temporal máxima (default: 5 minutos)
 * @param maxFailures Falhas antes de transição para SHADOW
 * @param nonceTimeoutMs Timeout para limpeza de nonces (default: 1 hora)
 * @author Álvaro Alencar
 */
class EntangledLogicOmegaV5(
    private val secretProvider: () -> ByteArray,
    private val maxAgeMs: Long = 300_000L,
    private val maxFailures: Int = 10,
    private val nonceTimeoutMs: Long = 3_600_000L
) : AutoCloseable {

    private val fibs = listOf(1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
    private val fibToIndex = fibs.withIndex().associate { it.value to it.index }
    private val maxValidMask = (1 shl fibs.size) - 1

    private val logger = LoggerFactory.getLogger(EntangledLogicOmegaV5::class.java)

    enum class Reality { PRIME, MIRROR, SHADOW }

    data class SecureRequest(
        val zeckendorfMask: Int,
        val seal: String,
        val context: String,
        val timestamp: Long,
        val path: String,
        val nonce: String = UUID.randomUUID().toString()
    )

    private data class FailureRecord(
        val count: AtomicInteger = AtomicInteger(0),
        val firstFailureTime: Long = System.currentTimeMillis()
    )

    private val failuresByFingerprint = ConcurrentHashMap<String, FailureRecord>()
    private val usedNonces = ConcurrentHashMap<String, Long>()
    private val metrics = ConcurrentHashMap<String, AtomicLong>()

    // Executor para limpeza periódica de nonces
    private val cleanupExecutor: ScheduledExecutorService =
        Executors.newSingleThreadScheduledExecutor {
            Thread(it, "ELP-Omega-Nonce-Cleanup").apply { isDaemon = true }
        }

    init {
        cleanupExecutor.scheduleAtFixedRate(
            ::cleanupOldNonces,
            10, 60, TimeUnit.SECONDS
        )
    }

    companion object {
        const val PERM_READ = 1
        const val PERM_WRITE = 2
        const val PERM_EXEC = 3
        const val PERM_ADMIN = 5
        const val PERM_AUDIT = 8
        const val PERM_GRANT = 13
        const val PERM_SECURE = 21
        const val PERM_TRACE = 34
        const val PERM_DEBUG = 55
        const val PERM_ROOT = 89
        const val PERM_OMNIS = 144

        val ALL_PERMISSIONS = listOf(
            PERM_READ, PERM_WRITE, PERM_EXEC, PERM_ADMIN, PERM_AUDIT,
            PERM_GRANT, PERM_SECURE, PERM_TRACE, PERM_DEBUG, PERM_ROOT, PERM_OMNIS
        )

        /**
         * Constrói uma máscara de bits onde cada permissão corresponde ao índice do Fibonacci na lista.
         * Regra: não permite escolher permissões com índices adjacentes (constraint não-adjacente).
         */
        fun buildZeckendorfMask(vararg permissions: Int): Int {
            if (permissions.isEmpty()) return 0

            val fibsList = listOf(1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
            val fibToIndexMap = fibsList.withIndex().associate { it.value to it.index }

            val indices = permissions.map { perm ->
                fibToIndexMap[perm] ?: throw IllegalArgumentException(
                    "Permissão inválida: $perm. Válidas: $fibsList"
                )
            }.sorted()

            for (i in 1 until indices.size) {
                if (indices[i] - indices[i - 1] == 1) {
                    val fib1 = fibsList[indices[i - 1]]
                    val fib2 = fibsList[indices[i]]
                    throw IllegalArgumentException(
                        "Violação de adjacência: $fib1 e $fib2 são adjacentes."
                    )
                }
            }

            return indices.fold(0) { mask, idx -> mask or (1 shl idx) }
        }

        fun hasPermission(mask: Int, permission: Int): Boolean {
            val fibsList = listOf(1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
            val idx = fibsList.indexOf(permission)
            return idx != -1 && (mask and (1 shl idx)) != 0
        }
    }

    fun processRequest(req: SecureRequest, realData: String, fingerprint: String): String {
        val startTime = System.nanoTime()
        val requestId = UUID.randomUUID().toString()

        logger.debug("Processando requisição [requestId={}]", requestId)

        try {
            // 1) Máscara válida?
            if (!isValidZeckendorfMask(req.zeckendorfMask)) {
                recordMetric("invalid_zeckendorf_masks")
                logger.warn("Máscara inválida [requestId={}, mask={}]", requestId, req.zeckendorfMask)
                return generateShadow(realData, req.context, req.path)
            }

            // 2) Permissão mínima
            if (!hasPermission(req.zeckendorfMask, PERM_READ)) {
                recordMetric("missing_read_permission")
                logger.warn("Permissão READ ausente [requestId={}, mask={}]", requestId, req.zeckendorfMask)
                return generateShadow(realData, req.context, req.path)
            }

            // 3) Freshness (barato)
            val now = System.currentTimeMillis()
            val isFresh = (now - req.timestamp) in 0L..maxAgeMs
            if (!isFresh) {
                recordMetric("stale_requests")
                logger.info("Requisição expirada [requestId={}, timestamp={}]", requestId, req.timestamp)
                // espelha (degradação graciosa)
                return sanitize(realData).also { recordMetric("reality.mirror") }
            }

            // 4) HMAC (barato)
            val expectedSeal = computeSealInternal(req)
            val sealOk = constantTimeEquals(req.seal, expectedSeal)

            if (!sealOk) {
                recordMetric("seal_validation_failures")
                logger.warn("Falha no selo [requestId={}, fingerprint={}]", requestId, fingerprint)
                val reality = handleFailures(fingerprint)

                recordMetric("reality.${reality.name.lowercase()}")
                return when (reality) {
                    Reality.MIRROR -> sanitize(realData)
                    Reality.SHADOW -> generateShadow(realData, req.context, req.path)
                    Reality.PRIME -> "PRIME_REALITY: $realData" // improvável aqui, mas mantido por completude
                }
            }

            // 5) Agora sim: nonce anti-replay (só depois de passar checks)
            if (!validateAndMarkNonce(req.nonce)) {
                recordMetric("replay_attempts")
                logger.warn("Replay detectado [requestId={}, nonce={}]", requestId, req.nonce)
                recordMetric("reality.shadow")
                return generateShadow(realData, req.context, req.path)
            }

            // Sucesso: PRIME
            failuresByFingerprint.remove(fingerprint)
            recordMetric("successful_requests")
            recordMetric("reality.prime")
            logger.info("Requisição bem-sucedida [requestId={}, reality=PRIME]", requestId)
            return "PRIME_REALITY: $realData"
        } finally {
            val processingTime = System.nanoTime() - startTime
            recordMetric("processing_time_ns", processingTime)
            logger.debug("Requisição processada [requestId={}, timeNs={}]", requestId, processingTime)
        }
    }

    private fun isValidZeckendorfMask(mask: Int): Boolean {
        if (mask < 0 || mask > maxValidMask) return false
        // proíbe bits adjacentes: 0110 inválido, 0101 válido
        return (mask and (mask ushr 1)) == 0
    }

    /**
     * Marca nonce como usado apenas se ele ainda não existia.
     * Retorna true se foi aceito (primeira vez), false se era replay.
     */
    private fun validateAndMarkNonce(nonce: String): Boolean {
        return usedNonces.putIfAbsent(nonce, System.currentTimeMillis()) == null
    }

    private fun cleanupOldNonces() {
        val cutoff = System.currentTimeMillis() - nonceTimeoutMs
        val iterator = usedNonces.entries.iterator()
        var removed = 0
        while (iterator.hasNext()) {
            if (iterator.next().value < cutoff) {
                iterator.remove()
                removed++
            }
        }
        if (removed > 0) {
            logger.debug("Nonces removidos: {}", removed)
        }
    }

    private fun computeSealInternal(req: SecureRequest): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secretProvider(), "HmacSHA256"))
        val payload = "${req.zeckendorfMask}|${req.context}|${req.timestamp}|${req.path}|${req.nonce}"
        val hash = mac.doFinal(payload.toByteArray(StandardCharsets.UTF_8))
        return Base64.getEncoder().encodeToString(hash)
    }

    private fun handleFailures(fp: String): Reality {
        val now = System.currentTimeMillis()
        val record = failuresByFingerprint.computeIfAbsent(fp) { FailureRecord() }

        // janela de reset das falhas
        if (now - record.firstFailureTime > nonceTimeoutMs) {
            failuresByFingerprint.remove(fp)
            return Reality.MIRROR
        }

        val failureCount = record.count.incrementAndGet()
        logger.debug("Falha acumulada [fingerprint={}, count={}]", fp, failureCount)

        return if (failureCount <= maxFailures) Reality.MIRROR else Reality.SHADOW
    }

    private fun sanitize(data: String): String {
        // Sanitização básica (ajuste conforme seu domínio real)
        return data
            .replace(Regex("\\d"), "*")
            .replace(Regex("(?i)senha[:=]\\s*[^\\s,;]+"), "senha=********")
            .replace(Regex("(?i)token[:=]\\s*[^\\s,;]+"), "token=********")
            .replace(Regex("(?i)cpf[:=]\\s*\\d{11}"), "cpf=***.***.***-**")
            .replace(Regex("(?i)email[:=]\\s*[^@\\s]+@[^@\\s]+\\.[^@\\s]+"), "email=***@***.***")
            .replace(Regex("(?i)cartao[:=]\\s*\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}"), "cartao=****-****-****-****")
    }

    private fun generateShadow(realData: String, ctx: String, path: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secretProvider(), "HmacSHA256"))
        val seed = "SHADOW|$path|$ctx|STABILITY_SEED_ELPΩ|${realData.length}"
        val hash = mac.doFinal(seed.toByteArray(StandardCharsets.UTF_8))
        val vaultId = Base64.getUrlEncoder()
            .withoutPadding()
            .encodeToString(hash.copyOfRange(0, 8))
        return "SHADOW_VAULT_ID:$vaultId:DATA_ENCRYPTED"
    }

    private fun constantTimeEquals(a: String, b: String): Boolean {
        if (a.length != b.length) return false
        var diff = 0
        for (i in a.indices) diff = diff or (a[i].code xor b[i].code)
        return diff == 0
    }

    private fun recordMetric(name: String, value: Long = 1L): Long {
        return metrics.computeIfAbsent(name) { AtomicLong(0) }.addAndGet(value)
    }

    fun getMetrics(): Map<String, Long> = metrics.mapValues { it.value.get() }.toSortedMap()
    fun resetMetrics() { metrics.clear() }

    fun getCacheStats(): Map<String, Any> = mapOf(
        "nonce_map_size" to usedNonces.size,
        "failure_records" to failuresByFingerprint.size
    )

    // ===== BUILDER =====
    class ZeckendorfMaskBuilder {
        private val permissions = mutableSetOf<Int>()
        fun read() = apply { permissions.add(PERM_READ) }
        fun write() = apply { permissions.add(PERM_WRITE) }
        fun exec() = apply { permissions.add(PERM_EXEC) }
        fun admin() = apply { permissions.add(PERM_ADMIN) }
        fun audit() = apply { permissions.add(PERM_AUDIT) }
        fun grant() = apply { permissions.add(PERM_GRANT) }
        fun secure() = apply { permissions.add(PERM_SECURE) }
        fun trace() = apply { permissions.add(PERM_TRACE) }
        fun debug() = apply { permissions.add(PERM_DEBUG) }
        fun root() = apply { permissions.add(PERM_ROOT) }
        fun omnis() = apply { permissions.add(PERM_OMNIS) }

        fun add(permission: Int) = apply {
            require(ALL_PERMISSIONS.contains(permission)) { "Permissão inválida: $permission" }
            permissions.add(permission)
        }

        fun build(): Int = buildZeckendorfMask(*permissions.toIntArray())
        fun buildSafe() = runCatching { build() }
    }

    fun maskBuilder() = ZeckendorfMaskBuilder()

    // ===== LIFECYCLE =====
    override fun close() {
        cleanupExecutor.shutdown()
        try {
            if (!cleanupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                cleanupExecutor.shutdownNow()
            }
        } catch (e: InterruptedException) {
            cleanupExecutor.shutdownNow()
            Thread.currentThread().interrupt()
        }
    }
}

// ===== EXTENSÕES SEGURAS =====
fun List<Int>.toZeckendorfMask(): Int =
    EntangledLogicOmegaV5.buildZeckendorfMask(*this.toIntArray())

infix fun Int.hasElpPermission(permission: Int): Boolean =
    EntangledLogicOmegaV5.hasPermission(this, permission)

// ===== EXEMPLO FUNCIONAL =====
fun main() {
    val secret = "SuperSegredo123!".toByteArray()
    val elp = EntangledLogicOmegaV5(
        secretProvider = { secret },
        maxAgeMs = 300_000L,
        maxFailures = 3,          // exemplo: após 3 falhas -> SHADOW
        nonceTimeoutMs = 3_600_000L
    )

    // Máscara válida (não-adjacente): read=1 (idx0), admin=5 (idx3), secure=21 (idx6)
    val mask = elp.maskBuilder().read().admin().secure().build()
    println("Máscara (bits): ${mask.toString(2).padStart(11, '0')}")

    val timestamp = System.currentTimeMillis()
    val path = "/api/user/data"
    val context = "user-dashboard"
    val nonce = UUID.randomUUID().toString()

    // Cliente calcula HMAC do mesmo payload
    val payload = "$mask|$context|$timestamp|$path|$nonce"
    val mac = Mac.getInstance("HmacSHA256")
    mac.init(SecretKeySpec(secret, "HmacSHA256"))
    val seal = Base64.getEncoder().encodeToString(mac.doFinal(payload.toByteArray(StandardCharsets.UTF_8)))

    val req = EntangledLogicOmegaV5.SecureRequest(
        zeckendorfMask = mask,
        seal = seal,
        context = context,
        timestamp = timestamp,
        path = path,
        nonce = nonce
    )

    val result = elp.processRequest(
        req = req,
        realData = "CPF 123.456.789-00, saldo R$ 1.000,00, cartao 1234-5678-9012-3456",
        fingerprint = "192.168.1.100-chrome"
    )

    println("Resultado: $result")
    println("Métricas: ${elp.getMetrics()}")
    println("Cache: ${elp.getCacheStats()}")

    elp.close()
}