import { Request, Response, NextFunction } from 'express';
import { EntangledLogicOmega, Reality } from './elp_omega'; // Importa sua classe TS

// Estendendo a tipagem do Express para incluir o status ELP
declare global {
    namespace Express {
        interface Request {
            elpReality?: Reality;
        }
    }
}

/**
 * Cria o Middleware ELP-Ω para Express.
 * @param secretKey A chave mestra para validação HMAC e geração de Shadow Data.
 */
export const elpOmegaMiddleware = (secretKey: string) => {
    // Instancia o motor de segurança uma única vez
    const securityEngine = new EntangledLogicOmega(secretKey);

    return (req: Request, res: Response, next: NextFunction) => {
        // 1. Extração dos Headers Específicos do Protocolo
        const mask = parseInt(req.header('X-ELP-Mask') || '-1');
        const seal = req.header('X-ELP-Seal') || '';
        const timestamp = parseInt(req.header('X-ELP-Timestamp') || '0');
        const nonce = req.header('X-ELP-Nonce') || '';
        
        // Contexto derivado
        const path = req.path;
        const context = req.method;
        const fingerprint = req.ip || 'unknown';

        // 2. Validação Topológica (Zeckendorf) e Criptográfica
        // Nota: Precisamos simular o 'realData' aqui pois o middleware roda ANTES do controller.
        // Se a validação falhar, nem precisaremos dos dados reais.
        
        // Verificação Lógica Rápida (Zeckendorf) - O(1)
        if (!securityEngine.isValidZeckendorf(mask)) {
            // DETECTADO ATAQUE DE BIT-FLIPPING OU PERMISSÃO INVÁLIDA
            // Ação: Shadow Reality imediata.
            // Geramos um payload falso baseado no caminho da URL para parecer real.
            const shadowData = generateShadowPayload(securityEngine, path, context);
            
            // Retorna 200 OK para enganar o atacante
            return res.status(200).json({
                data: shadowData,
                reality: Reality.SHADOW,
                meta: { latency: '4ms' } // Fake latency para realismo
            });
        }

        // Verificação Criptográfica (HMAC)
        const secureReq = { mask, seal, context, timestamp, path, nonce };
        const expectedSeal = securityEngine.computeSeal(secureReq);
        
        // Simulação de check seguro (na prática, usaria o método processRequest completo)
        // Aqui simplificamos para decisão de roteamento
        const isSealValid = (seal === expectedSeal); // Nota: em prod usar timingSafeEqual
        
        if (!isSealValid) {
             const shadowData = generateShadowPayload(securityEngine, path, context);
             return res.status(200).json({
                data: shadowData,
                reality: Reality.SHADOW
            });
        }

        // 3. Aprovação (PRIME ou MIRROR)
        // Se chegou aqui, a requisição é matematicamente válida.
        // Injetamos o status no request para o Controller decidir se precisa sanitizar (Mirror)
        req.elpReality = Reality.PRIME; 
        
        // Passa a bola para o próximo handler (sua API real)
        next();
    };
};

// Função auxiliar para acessar o método privado ou gerar manualmente o shadow
function generateShadowPayload(engine: EntangledLogicOmega, path: string, ctx: string): string {
    // Como o método generateShadow é privado na classe original, 
    // ou o tornamos público ou replicamos a lógica de decepção aqui.
    // Para este exemplo, replicamos a lógica de "Vault ID":
    return `SHADOW_VAULT_ID:${Buffer.from(path + ctx).toString('base64').substring(0,10)}:ENCRYPTED`;
}

// --- Como usar no seu app Express ---
// import express from 'express';
// const app = express();
// app.use(elpOmegaMiddleware('SUA_CHAVE_SUPER_SECRETA'));