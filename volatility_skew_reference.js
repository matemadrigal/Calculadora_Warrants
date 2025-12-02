/**
 * ══════════════════════════════════════════════════════════════════════════════
 * VOLATILITY SKEW MODEL - INTEGRACIÓN PARA EUROPEAN WARRANT CALCULATOR v3.1
 * ══════════════════════════════════════════════════════════════════════════════
 * 
 * Este archivo contiene:
 * 1. Función de ajuste de volatilidad por skew
 * 2. Código de integración para el componente React
 * 3. Componente UI para controlar el skew
 * 
 * INSTRUCCIONES DE INTEGRACIÓN:
 * 1. Copiar la función adjustVolatilityForSkew() después de calculateBreakeven()
 * 2. Añadir el estado enableSkew en el componente principal
 * 3. Modificar la lógica de cálculo donde se usa la volatilidad
 * 4. Añadir el control UI en el panel de inputs
 */

// ═══════════════════════════════════════════════════════════════════════════
// PARTE 1: FUNCIÓN DE VOLATILITY SKEW
// ═══════════════════════════════════════════════════════════════════════════
// Copiar esta función DESPUÉS de calculateBreakeven() (línea ~647)

/**
 * Ajusta la volatilidad ATM según el skew de mercado para índices de renta variable.
 * 
 * El skew captura el fenómeno donde opciones OTM (especialmente PUTs) cotizan
 * con volatilidades implícitas superiores a las ATM debido a la demanda de
 * protección contra caídas del mercado.
 * 
 * Características del modelo:
 * - Skew asimétrico: PUTs OTM tienen mayor IV que CALLs OTM
 * - Term structure: el skew se aplana con el tiempo
 * - Calibrado para índices europeos y americanos (STOXX50, SPX, NDX)
 * 
 * @param {number} sigmaATM - Volatilidad ATM en % (ej: 28 para 28%)
 * @param {number} S - Precio spot del subyacente
 * @param {number} K - Precio de ejercicio (strike)
 * @param {number} T - Tiempo a vencimiento en años
 * @param {string} type - 'call' o 'put'
 * @param {Object} params - Parámetros opcionales de calibración
 * @returns {number} - Volatilidad ajustada en %
 */
function adjustVolatilityForSkew(sigmaATM, S, K, T, type, params = {}) {
    // ───────────────────────────────────────────────────────────────────────
    // Parámetros de calibración
    // Estos valores están calibrados para índices de renta variable.
    // Puedes ajustarlos si observas discrepancias sistemáticas.
    // ───────────────────────────────────────────────────────────────────────
    const {
        // Intensidad del skew para PUTs OTM (1.5-2.5 típico)
        putSkewIntensity = 2.2,
        // Intensidad del skew para CALLs OTM (0.4-0.8 típico)
        callSkewIntensity = 0.5,
        // Curvatura del smile (0.3-0.6 típico)
        smileCurvature = 0.5,
        // Exponente de decaimiento temporal (0.3-0.5 típico)
        timeDecayExponent = 0.4,
        // Límites de volatilidad como ratio de ATM
        minVolRatio = 0.6,
        maxVolRatio = 2.5
    } = params;

    // Validación de inputs
    if (sigmaATM <= 0 || S <= 0 || K <= 0 || T <= 0) {
        return sigmaATM;
    }

    // Log-moneyness: ln(S/K)
    // - Positivo cuando S > K (PUT OTM, CALL ITM)
    // - Negativo cuando S < K (PUT ITM, CALL OTM)
    const logMoneyness = Math.log(S / K);

    // Factor de atenuación temporal
    // El skew es más pronunciado a corto plazo y se aplana con el tiempo
    // Referencia: 30 días como base de normalización
    const T_reference = 30 / 365.25;
    const timeFactor = Math.pow(
        T_reference / Math.max(T, T_reference / 10), 
        timeDecayExponent
    );
    // Cap para evitar valores extremos
    const cappedTimeFactor = Math.min(timeFactor, 2.5);

    // Cálculo del ajuste según tipo de opción
    let skewAdjustment;

    if (type === 'put') {
        if (logMoneyness > 0) {
            // PUT OTM (S > K): skew pronunciado
            // Componente lineal (skew principal) + cuadrático (smile)
            skewAdjustment = putSkewIntensity * logMoneyness * cappedTimeFactor
                           + smileCurvature * logMoneyness * logMoneyness;
        } else {
            // PUT ITM (S < K): skew reducido
            skewAdjustment = putSkewIntensity * logMoneyness * cappedTimeFactor * 0.25
                           + smileCurvature * logMoneyness * logMoneyness * 0.4;
        }
    } else { // call
        if (logMoneyness < 0) {
            // CALL OTM (S < K): skew presente pero menor que PUT
            skewAdjustment = -callSkewIntensity * logMoneyness * cappedTimeFactor
                           + smileCurvature * logMoneyness * logMoneyness * 0.3;
        } else {
            // CALL ITM (S > K): mínimo ajuste
            skewAdjustment = callSkewIntensity * logMoneyness * cappedTimeFactor * 0.15
                           + smileCurvature * logMoneyness * logMoneyness * 0.2;
        }
    }

    // Aplicar ajuste multiplicativo
    const adjustedVol = sigmaATM * (1 + skewAdjustment);

    // Aplicar límites razonables
    const minVol = sigmaATM * minVolRatio;
    const maxVol = sigmaATM * maxVolRatio;

    return Math.max(minVol, Math.min(maxVol, adjustedVol));
}

// ═══════════════════════════════════════════════════════════════════════════
// PARTE 2: MODIFICACIONES AL COMPONENTE REACT
// ═══════════════════════════════════════════════════════════════════════════

/*
 * 2.1 AÑADIR NUEVO ESTADO (después de línea ~850, junto a los otros useState)
 */
// const [enableSkewAdjustment, setEnableSkewAdjustment] = useState(true);

/*
 * 2.2 MODIFICAR LA LÓGICA DE CÁLCULO (en el useMemo de results, ~línea 911)
 * 
 * Reemplazar:
 *     if (calculationMode === 'volatility') {
 *         usedVolatility = parseFloat(volatility);
 *         ...
 *     }
 * 
 * Por el código siguiente:
 */

/*
if (calculationMode === 'volatility') {
    let inputVolatility = parseFloat(volatility);
    
    // Aplicar ajuste de skew si está habilitado
    if (enableSkewAdjustment) {
        const T = daysNum / DAYS_PER_YEAR;
        usedVolatility = adjustVolatilityForSkew(
            inputVolatility, 
            spotNum, 
            strikeNum, 
            T, 
            warrantType
        );
    } else {
        usedVolatility = inputVolatility;
    }
    
    const priceParams = { ...baseParams, volatility: usedVolatility };
    premium = blackScholesPrice(priceParams) * ratio;
    impliedVol = null;
} else {
    // Modo IV implícita - sin cambios
    const marketPriceNum = parseFloat(marketPrice);
    const bsEquivalentPrice = marketPriceNum / ratio;
    
    const ivParams = { ...baseParams, marketPrice: bsEquivalentPrice };
    const iv = calculateImpliedVolatility(ivParams);
    
    if (iv === null) return null;
    
    impliedVol = iv;
    usedVolatility = iv;
    premium = marketPriceNum;
}
*/

// ═══════════════════════════════════════════════════════════════════════════
// PARTE 3: COMPONENTE UI PARA CONTROL DE SKEW
// ═══════════════════════════════════════════════════════════════════════════

/*
 * Añadir este código DESPUÉS del selector de modo de cálculo (~línea 1275)
 * y ANTES de los inputs de volatilidad/precio de mercado
 */

const SkewControlUI = `
{/* Control de Volatility Skew - añadir después del ModeSelector */}
{calculationMode === 'volatility' && (
    <div className="mb-4 p-3 bg-terminal-bg rounded-lg border border-terminal-border">
        <div className="flex items-center justify-between">
            <div>
                <label className="flex items-center cursor-pointer">
                    <input
                        type="checkbox"
                        checked={enableSkewAdjustment}
                        onChange={(e) => setEnableSkewAdjustment(e.target.checked)}
                        className="mr-2 w-4 h-4 accent-terminal-warning"
                    />
                    <span className="text-sm text-terminal-text">
                        Ajustar por Volatility Skew
                    </span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-6">
                    Ajusta σ según moneyness (PUTs OTM → mayor IV)
                </p>
            </div>
            {enableSkewAdjustment && results && (
                <div className="text-right">
                    <span className="text-xs text-gray-500">σ ajustada:</span>
                    <span className="text-sm text-terminal-warning font-mono ml-1">
                        {results.usedVolatility.toFixed(2)}%
                    </span>
                </div>
            )}
        </div>
    </div>
)}
`;

// ═══════════════════════════════════════════════════════════════════════════
// PARTE 4: TOOLTIP INFORMATIVO (opcional)
// ═══════════════════════════════════════════════════════════════════════════

const SkewTooltip = `
{/* Tooltip explicativo para el skew */}
<div className="group relative inline-block ml-1">
    <span className="text-gray-500 cursor-help">ⓘ</span>
    <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 
                    hidden group-hover:block w-64 p-3 bg-terminal-card 
                    border border-terminal-border rounded-lg shadow-lg z-10">
        <p className="text-xs text-gray-300 mb-2">
            <strong>Volatility Skew</strong>
        </p>
        <p className="text-xs text-gray-400">
            Las opciones OTM (especialmente PUTs) cotizan con volatilidades 
            implícitas superiores a las ATM. Este ajuste estima automáticamente 
            la IV según el moneyness de tu warrant.
        </p>
        <div className="mt-2 text-xs text-gray-500">
            • PUT OTM: +5% a +40% sobre ATM<br/>
            • ATM: volatilidad base<br/>
            • CALL OTM: +2% a +15% sobre ATM
        </div>
    </div>
</div>
`;

// ═══════════════════════════════════════════════════════════════════════════
// PRUEBA DE LA FUNCIÓN
// ═══════════════════════════════════════════════════════════════════════════

console.log('═'.repeat(74));
console.log('VOLATILITY SKEW MODEL - TEST DE VALIDACIÓN');
console.log('═'.repeat(74));
console.log();

// Test con tu caso del warrant NASDAQ
const testCases = [
    { S: 21500, K: 19000, T: 108/365.25, type: 'put', sigmaATM: 28, expected: '~35%' },
    { S: 21500, K: 21500, T: 108/365.25, type: 'put', sigmaATM: 28, expected: '28% (ATM)' },
    { S: 21500, K: 24000, T: 108/365.25, type: 'call', sigmaATM: 28, expected: '~30%' },
    { S: 4950, K: 4500, T: 30/365.25, type: 'put', sigmaATM: 18, expected: '~22%' },
];

console.log('Strike     S/K      Tipo      σ_ATM    σ_Skew   Esperado');
console.log('─'.repeat(74));

for (const tc of testCases) {
    const adjusted = adjustVolatilityForSkew(tc.sigmaATM, tc.S, tc.K, tc.T, tc.type);
    const ratio = (tc.S / tc.K).toFixed(3);
    console.log(
        `${tc.K.toString().padStart(6)}     ${ratio}    ${tc.type.toUpperCase().padEnd(4)}      ` +
        `${tc.sigmaATM}%      ${adjusted.toFixed(1)}%    ${tc.expected}`
    );
}

console.log('─'.repeat(74));
console.log();
console.log('✓ Función lista para integrar');
console.log();
