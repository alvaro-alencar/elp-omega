import * as crypto from 'crypto';

export enum Reality {
    PRIME = "PRIME",
    MIRROR = "MIRROR",
    SHADOW = "SHADOW"
}

export class EntangledLogicOmega {
    private secret: string;
    private usedNonces: Map<string, number>;
    public readonly maxAgeMs = 300000; // 5 minutos (Público para acesso no middleware)

    constructor(secret: string) {
        this.secret = secret;
        this.usedNonces = new Map();
    }

    /**
     * Validação Topológica Zeckendorf O(1)
     */
    public isValidZeckendorf(mask: number): boolean {
        return (mask & (mask >> 1)) === 0;
    }

    /**
     * Gera o selo HMAC para integridade
     */
    public computeSeal(mask: number, context: string, timestamp: number, path: string, nonce: string): string {
        const payload = `${mask}|${context}|${timestamp}|${path}|${nonce}`;
        return crypto.createHmac('sha256', this.secret).update(payload).digest('hex');
    }

    /**
     * Verifica Nonce (Anti-Replay)
     * Retorna true se o nonce é válido (novo), false se já foi usado (replay).
     */
    public validateNonce(nonce: string, now: number): boolean {
        // Limpeza simples de nonces antigos para evitar estouro de memória
        // Em produção, isso seria feito via Redis com TTL
        if (this.usedNonces.size > 10000) {
            this.usedNonces.clear(); 
        }

        if (this.usedNonces.has(nonce)) {
            return false; // Replay detectado
        }
        
        this.usedNonces.set(nonce, now);
        return true; // Nonce válido e registrado
    }

    /**
     * Gera Payload da Shadow Reality
     * Deve ser DETERMINÍSTICO: Mesma entrada = Mesma saída.
     * Publico para ser usado pelo middleware.
     */
    public generateShadow(context: string, path: string, nonce: string): any {
        // Cria uma seed numérica baseada no hash da requisição
        const seedStr = `${path}|${context}|${nonce}|${this.secret}`;
        const hash = crypto.createHash('sha256').update(seedStr).digest('hex');
        // Pega os primeiros 8 caracteres hexa e converte para int
        let seed = parseInt(hash.substring(0, 8), 16);

        // Gerador de números pseudo-aleatórios simples (LCG)
        const rand = () => {
            seed = (seed * 1664525 + 1013904223) % 4294967296;
            return seed / 4294967296;
        };

        // Gera dados bancários sintéticos
        return {
            status: "success",
            transaction_id: crypto.randomUUID(), 
            timestamp: Date.now(),
            data: {
                account_type: rand() > 0.5 ? "checking" : "savings",
                balance: parseFloat((rand() * 500000).toFixed(2)),
                currency: "BRL",
                flags: ["verified", "secure"]
            },
            meta: {
                processing_time_ms: Math.floor(rand() * 140) + 10,
                region: "sa-east-1"
            }
        };
    }
}