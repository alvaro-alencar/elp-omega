import { createHmac, timingSafeEqual } from 'crypto';
import { v4 as uuidv4 } from 'uuid';

export enum Reality {
    PRIME = 'PRIME',
    MIRROR = 'MIRROR',
    SHADOW = 'SHADOW'
}

export interface SecureRequest {
    mask: number;
    seal: string;
    context: string;
    timestamp: number;
    path: string;
    nonce: string;
}

export class EntangledLogicOmega {
    private usedNonces: Map<string, number> = new Map();
    private failures: Map<string, { count: number; first: number }> = new Map();

    constructor(
        private secret: string,
        private maxAgeMs: number = 300000,
        private maxFailures: number = 5
    ) {}

    public isValidZeckendorf(mask: number): boolean {
        if (mask < 0) return false;
        return (mask & (mask >> 1)) === 0;
    }

    public computeSeal(req: Omit<SecureRequest, 'seal'>): string {
        const payload = `${req.mask}|${req.context}|${req.timestamp}|${req.path}|${req.nonce}`;
        return createHmac('sha256', this.secret).update(payload).digest('base64');
    }

    public processRequest(req: SecureRequest, realData: string, fingerprint: string): { data: string; reality: Reality } {
        // 1. Validação de Máscara
        if (!this.isValidZeckendorf(req.mask)) {
            return { data: this.generateShadow(realData, req.context, req.path), reality: Reality.SHADOW };
        }

        // 2. Freshness Check
        const now = Date.now();
        if (now - req.timestamp > this.maxAgeMs || now < req.timestamp) {
            return { data: this.sanitize(realData), reality: Reality.MIRROR };
        }

        // 3. HMAC Validation (Timing Safe)
        const expectedSeal = this.computeSeal(req);
        if (!this.safeCompare(req.seal, expectedSeal)) {
            return this.handleFailure(fingerprint, realData, req.context, req.path);
        }

        // 4. Anti-Replay
        if (this.usedNonces.has(req.nonce)) {
            return { data: this.generateShadow(realData, req.context, req.path), reality: Reality.SHADOW };
        }
        this.usedNonces.set(req.nonce, now);

        return { data: `PRIME_REALITY: ${realData}`, reality: Reality.PRIME };
    }

    private safeCompare(a: string, b: string): boolean {
        const bufA = Buffer.from(a);
        const bufB = Buffer.from(b);
        if (bufA.length !== bufB.length) return false;
        return timingSafeEqual(bufA, bufB);
    }

    private handleFailure(fp: string, data: string, ctx: string, path: string): { data: string; reality: Reality } {
        const record = this.failures.get(fp) || { count: 0, first: Date.now() };
        record.count++;
        this.failures.set(fp, record);

        if (record.count > this.maxFailures) {
            return { data: this.generateShadow(data, ctx, path), reality: Reality.SHADOW };
        }
        return { data: this.sanitize(data), reality: Reality.MIRROR };
    }

    private sanitize(data: string): string {
        return data.replace(/\d/g, '*').replace(/(senha|token)=[^ ]+/gi, '$1=********');
    }

    private generateShadow(realData: string, ctx: string, path: string): string {
        const seed = `SHADOW|${path}|${ctx}|${realData.length}`;
        const hash = createHmac('sha256', this.secret).update(seed).digest('hex').substring(0, 16);
        return `SHADOW_VAULT_ID:${hash}:ENCRYPTED`;
    }
}