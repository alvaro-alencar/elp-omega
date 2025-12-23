import { EntangledLogicOmega, Reality } from './elp_omega';

describe('ELP-Omega TypeScript Implementation', () => {
    const secret = 'vortex-secret';
    const elp = new EntangledLogicOmega(secret);

    test('should validate Zeckendorf non-adjacency', () => {
        expect(elp.isValidZeckendorf(0b1001)).toBe(true);
        expect(elp.isValidZeckendorf(0b0011)).toBe(false);
    });

    test('should return PRIME for valid request', () => {
        const ts = Date.now();
        const req = {
            mask: 1,
            context: 'test',
            timestamp: ts,
            path: '/api',
            nonce: 'n1'
        };
        const seal = elp.computeSeal(req);
        const result = elp.processRequest({ ...req, seal }, 'SECRET', 'fp1');
        expect(result.reality).toBe(Reality.PRIME);
    });

    test('should trigger SHADOW on nonce replay', () => {
        const ts = Date.now();
        const req = { mask: 1, context: 'c', timestamp: ts, path: '/p', nonce: 'r1' };
        const seal = elp.computeSeal(req);
        
        elp.processRequest({ ...req, seal }, 'D', 'fp');
        const result = elp.processRequest({ ...req, seal }, 'D', 'fp');
        
        expect(result.reality).toBe(Reality.SHADOW);
    });
});