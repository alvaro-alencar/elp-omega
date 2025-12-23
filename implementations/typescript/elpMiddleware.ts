import { Request, Response, NextFunction } from 'express';
import { EntangledLogicOmega } from './elp_omega';
import * as crypto from 'crypto';

export const elpOmegaMiddleware = (secretKey: string) => {
    const securityEngine = new EntangledLogicOmega(secretKey);

    return (req: Request, res: Response, next: NextFunction) => {
        const mask = parseInt(req.header('X-ELP-Mask') || '-1');
        const seal = req.header('X-ELP-Seal') || '';
        const timestamp = parseInt(req.header('X-ELP-Timestamp') || '0');
        const nonce = req.header('X-ELP-Nonce') || '';
        
        const path = req.path;
        const context = req.method;
        const now = Date.now();

        let isShadowCandidate = false;

        // 1. Validação Topológica
        if (!securityEngine.isValidZeckendorf(mask)) {
            isShadowCandidate = true;
        }

        // 2. Validação Timestamp
        // Acessa a propriedade pública maxAgeMs
        if (!isShadowCandidate && Math.abs(now - timestamp) > securityEngine.maxAgeMs) {
            isShadowCandidate = true;
        }

        // 3. Validação HMAC
        if (!isShadowCandidate) {
            const expected = securityEngine.computeSeal(mask, context, timestamp, path, nonce);
            
            // Timing-safe compare
            const a = Buffer.from(seal, 'utf-8'); // Especifica encoding para evitar erro de tipo
            const b = Buffer.from(expected, 'utf-8');
            
            if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) {
                isShadowCandidate = true;
            }
        }

        // 4. Validação Nonce
        if (!isShadowCandidate) {
            // Usa o método público validateNonce
            if (!securityEngine.validateNonce(nonce, now)) {
                isShadowCandidate = true;
            }
        }

        if (isShadowCandidate) {
            // Shadow Reality com Jitter (20ms a 60ms)
            const jitter = Math.floor(Math.random() * 40) + 20;
            // Usa o método público generateShadow
            const shadowPayload = securityEngine.generateShadow(context, path, nonce);
            
            setTimeout(() => {
                res.status(200).json(shadowPayload);
            }, jitter);
            return;
        }

        next();
    };
};