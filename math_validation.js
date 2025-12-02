/**
 * ============================================================================
 * EUROPEAN WARRANT CALCULATOR v3.0 - SUITE DE TESTS MATEMÁTICOS
 * ============================================================================
 * Validación exhaustiva de todas las fórmulas Black-Scholes-Merton y Greeks.
 * Referencias: Hull (10th ed.), Wilmott (2nd ed.), Bloomberg terminal values.
 */

const DAYS_PER_YEAR = 365.25;
const NEWTON_RAPHSON_TOLERANCE = 1e-8;
const NEWTON_RAPHSON_MAX_ITERATIONS = 100;
const IV_BOUNDS = { min: 0.1, max: 500 };

// ═══════════════════════════════════════════════════════════════════════════
// FUNCIONES MATEMÁTICAS (copiadas del código principal para tests)
// ═══════════════════════════════════════════════════════════════════════════

function normalCDF(x) {
    if (x < -10) return 0;
    if (x > 10) return 1;
    const a1 = 0.319381530;
    const a2 = -0.356563782;
    const a3 = 1.781477937;
    const a4 = -1.821255978;
    const a5 = 1.330274429;
    const p = 0.2316419;
    const absX = Math.abs(x);
    const t = 1 / (1 + p * absX);
    const t2 = t * t;
    const t3 = t2 * t;
    const t4 = t3 * t;
    const t5 = t4 * t;
    const pdf = Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
    const cdf = pdf * (a1 * t + a2 * t2 + a3 * t3 + a4 * t4 + a5 * t5);
    return x >= 0 ? 1 - cdf : cdf;
}

function normalPDF(x) {
    return Math.exp(-0.5 * x * x) / Math.sqrt(2 * Math.PI);
}

function calculateD1(S, K, T, r, q, sigma) {
    const numerator = Math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T;
    const denominator = sigma * Math.sqrt(T);
    return numerator / denominator;
}

function calculateD2(d1, sigma, T) {
    return d1 - sigma * Math.sqrt(T);
}

function blackScholesPrice(params) {
    const { type, spot, strike, daysToExpiration, riskFreeRate, dividendYield, volatility } = params;
    if (!volatility || volatility <= 0) return 0;
    const T = daysToExpiration / DAYS_PER_YEAR;
    const r = riskFreeRate / 100;
    const q = dividendYield / 100;
    const sigma = volatility / 100;
    if (T <= 0) {
        return type === 'call' ? Math.max(0, spot - strike) : Math.max(0, strike - spot);
    }
    const d1 = calculateD1(spot, strike, T, r, q, sigma);
    const d2 = calculateD2(d1, sigma, T);
    const discountDiv = Math.exp(-q * T);
    const discountRf = Math.exp(-r * T);
    if (type === 'call') {
        return spot * discountDiv * normalCDF(d1) - strike * discountRf * normalCDF(d2);
    } else {
        return strike * discountRf * normalCDF(-d2) - spot * discountDiv * normalCDF(-d1);
    }
}

function calculateGreeks(params) {
    const { type, spot, strike, daysToExpiration, riskFreeRate, dividendYield, volatility } = params;
    if (!volatility || volatility <= 0 || daysToExpiration <= 0) {
        return {
            delta: type === 'call' ? (spot > strike ? 1 : 0) : (spot < strike ? -1 : 0),
            gamma: 0, theta: 0, vega: 0, rho: 0
        };
    }
    const T = daysToExpiration / DAYS_PER_YEAR;
    const r = riskFreeRate / 100;
    const q = dividendYield / 100;
    const sigma = volatility / 100;
    const sqrtT = Math.sqrt(T);
    const d1 = calculateD1(spot, strike, T, r, q, sigma);
    const d2 = calculateD2(d1, sigma, T);
    const Nd1 = normalCDF(d1);
    const Nd2 = normalCDF(d2);
    const Nmd1 = normalCDF(-d1);
    const Nmd2 = normalCDF(-d2);
    const nd1 = normalPDF(d1);
    const discountDiv = Math.exp(-q * T);
    const discountRf = Math.exp(-r * T);

    let delta, gamma, theta, vega, rho;

    // Delta
    delta = type === 'call' ? discountDiv * Nd1 : -discountDiv * Nmd1;

    // Gamma
    gamma = (discountDiv * nd1) / (spot * sigma * sqrtT);

    // Theta
    const thetaCommon = -(spot * discountDiv * nd1 * sigma) / (2 * sqrtT);
    if (type === 'call') {
        theta = thetaCommon - r * strike * discountRf * Nd2 + q * spot * discountDiv * Nd1;
    } else {
        theta = thetaCommon + r * strike * discountRf * Nmd2 - q * spot * discountDiv * Nmd1;
    }
    theta = theta / DAYS_PER_YEAR;

    // Vega
    vega = (spot * discountDiv * nd1 * sqrtT) / 100;

    // Rho
    rho = type === 'call' 
        ? (strike * T * discountRf * Nd2) / 100 
        : -(strike * T * discountRf * Nmd2) / 100;

    return { delta, gamma, theta, vega, rho };
}

function calculateImpliedVolatility(params) {
    const { marketPrice, type, spot, strike, daysToExpiration, riskFreeRate, dividendYield } = params;
    if (!marketPrice || marketPrice <= 0) return null;
    let sigma = Math.sqrt(2 * Math.PI / (daysToExpiration / DAYS_PER_YEAR)) * (marketPrice / spot) * 100;
    sigma = Math.max(IV_BOUNDS.min, Math.min(IV_BOUNDS.max, sigma || 30));

    for (let i = 0; i < NEWTON_RAPHSON_MAX_ITERATIONS; i++) {
        const priceParams = { ...params, volatility: sigma };
        const theoreticalPrice = blackScholesPrice(priceParams);
        const diff = theoreticalPrice - marketPrice;
        if (Math.abs(diff) < NEWTON_RAPHSON_TOLERANCE) return sigma;
        const greeks = calculateGreeks(priceParams);
        const vega = greeks.vega;
        if (Math.abs(vega) < 1e-10) {
            sigma = diff > 0 ? sigma * 0.8 : sigma * 1.2;
        } else {
            sigma = sigma - diff / vega;
        }
        sigma = Math.max(IV_BOUNDS.min, Math.min(IV_BOUNDS.max, sigma));
    }
    return null;
}

// ═══════════════════════════════════════════════════════════════════════════
// UTILIDADES DE TESTING
// ═══════════════════════════════════════════════════════════════════════════

let passCount = 0;
let failCount = 0;

function assert(condition, testName, actual, expected, tolerance = 0.01) {
    if (condition) {
        console.log(`  ✓ ${testName}`);
        passCount++;
    } else {
        console.log(`  ✗ ${testName}`);
        console.log(`    Actual:   ${actual}`);
        console.log(`    Expected: ${expected}`);
        console.log(`    Diff:     ${Math.abs(actual - expected)}`);
        failCount++;
    }
}

function assertClose(actual, expected, tolerance, testName) {
    const condition = Math.abs(actual - expected) < tolerance;
    assert(condition, testName, actual, expected, tolerance);
}

// ═══════════════════════════════════════════════════════════════════════════
// SUITE DE TESTS
// ═══════════════════════════════════════════════════════════════════════════

console.log('\n╔══════════════════════════════════════════════════════════════════╗');
console.log('║    EUROPEAN WARRANT CALCULATOR v3.0 - MATHEMATICAL VALIDATION   ║');
console.log('╚══════════════════════════════════════════════════════════════════╝\n');

// ───────────────────────────────────────────────────────────────────────────
// TEST 1: Normal CDF (Abramowitz & Stegun approximation)
// ───────────────────────────────────────────────────────────────────────────
console.log('▶ TEST 1: Normal CDF Accuracy');
console.log('  Reference: Standard normal distribution tables');
console.log('─'.repeat(70));

const cdfTests = [
    { x: 0, expected: 0.5, tolerance: 1e-9 },
    { x: 1, expected: 0.8413447, tolerance: 1e-5 },
    { x: -1, expected: 0.1586553, tolerance: 1e-5 },
    { x: 2, expected: 0.9772499, tolerance: 1e-5 },
    { x: -2, expected: 0.0227501, tolerance: 1e-5 },
    { x: 3, expected: 0.9986501, tolerance: 1e-5 },
    { x: -3, expected: 0.0013499, tolerance: 1e-5 },
];

cdfTests.forEach(({ x, expected, tolerance }) => {
    const actual = normalCDF(x);
    assertClose(actual, expected, tolerance, `N(${x}) = ${expected.toFixed(7)}`);
});

// ───────────────────────────────────────────────────────────────────────────
// TEST 2: Black-Scholes without dividends
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 2: Black-Scholes (No Dividends)');
console.log('  Reference: Hull, 10th ed., Example 15.6');
console.log('  Params: S=42, K=40, T=0.5y, r=10%, σ=20%, q=0%');
console.log('─'.repeat(70));

const hullParams = {
    spot: 42,
    strike: 40,
    daysToExpiration: 182.625, // 0.5 years
    riskFreeRate: 10,
    dividendYield: 0,
    volatility: 20
};

const hullCall = blackScholesPrice({ ...hullParams, type: 'call' });
const hullPut = blackScholesPrice({ ...hullParams, type: 'put' });

// Hull example values: Call ≈ 4.76, Put ≈ 0.81
assertClose(hullCall, 4.76, 0.02, 'Call price ≈ 4.76');
assertClose(hullPut, 0.81, 0.02, 'Put price ≈ 0.81');

// Put-Call Parity: C - P = S - K*e^(-rT)
const parity = hullCall - hullPut;
const expectedParity = 42 - 40 * Math.exp(-0.1 * 0.5);
assertClose(parity, expectedParity, 0.001, `Put-Call Parity: ${parity.toFixed(4)} = ${expectedParity.toFixed(4)}`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 3: Black-Scholes with dividends (Merton model)
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 3: Black-Scholes-Merton (With Dividends)');
console.log('  Params: S=100, K=100, T=1y, r=5%, σ=20%, q=3%');
console.log('─'.repeat(70));

const mertonParams = {
    spot: 100,
    strike: 100,
    daysToExpiration: 365.25,
    riskFreeRate: 5,
    dividendYield: 3,
    volatility: 20
};

const mertonCall = blackScholesPrice({ ...mertonParams, type: 'call' });
const mertonPut = blackScholesPrice({ ...mertonParams, type: 'put' });

// With dividends: calls cheaper, puts more expensive
const callNoDivParams = { ...mertonParams, dividendYield: 0 };
const callNoDiv = blackScholesPrice({ ...callNoDivParams, type: 'call' });
const putNoDiv = blackScholesPrice({ ...callNoDivParams, type: 'put' });

assert(mertonCall < callNoDiv, `Call with div (${mertonCall.toFixed(4)}) < Call no div (${callNoDiv.toFixed(4)})`);
assert(mertonPut > putNoDiv, `Put with div (${mertonPut.toFixed(4)}) > Put no div (${putNoDiv.toFixed(4)})`);

// Put-Call Parity with dividends: C - P = S*e^(-qT) - K*e^(-rT)
const parityMerton = mertonCall - mertonPut;
const expectedParityMerton = 100 * Math.exp(-0.03) - 100 * Math.exp(-0.05);
assertClose(parityMerton, expectedParityMerton, 0.001, `Put-Call Parity (Merton): ${parityMerton.toFixed(4)} = ${expectedParityMerton.toFixed(4)}`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 4: Greeks - Delta
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 4: Delta (Δ)');
console.log('  Property: |Delta_Call| + |Delta_Put| = e^(-qT) ≈ 1');
console.log('─'.repeat(70));

const greeksCall = calculateGreeks({ ...mertonParams, type: 'call' });
const greeksPut = calculateGreeks({ ...mertonParams, type: 'put' });

const deltaSum = Math.abs(greeksCall.delta) + Math.abs(greeksPut.delta);
const expectedDeltaSum = Math.exp(-0.03); // e^(-qT) for T=1, q=3%
assertClose(deltaSum, expectedDeltaSum, 0.001, `|Δ_call| + |Δ_put| = ${deltaSum.toFixed(6)} ≈ ${expectedDeltaSum.toFixed(6)}`);

// ATM call delta should be close to 0.5 (slightly higher due to r > q)
assert(greeksCall.delta > 0.5 && greeksCall.delta < 0.7, `ATM Call Delta in range [0.5, 0.7]: ${greeksCall.delta.toFixed(4)}`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 5: Greeks - Gamma
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 5: Gamma (Γ)');
console.log('  Property: Gamma identical for calls and puts');
console.log('─'.repeat(70));

assertClose(greeksCall.gamma, greeksPut.gamma, 1e-10, `Γ_call = Γ_put: ${greeksCall.gamma.toFixed(8)}`);

// Gamma should be positive
assert(greeksCall.gamma > 0, `Gamma > 0: ${greeksCall.gamma.toFixed(8)}`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 6: Greeks - Theta
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 6: Theta (Θ)');
console.log('  Property: Time decay is typically negative');
console.log('─'.repeat(70));

// For most options, theta is negative (time decay hurts option holders)
// Exception: deep ITM puts with high rates can have positive theta
assert(greeksCall.theta < 0, `Call Theta < 0: ${greeksCall.theta.toFixed(6)} €/day`);
assert(greeksPut.theta < 0, `Put Theta < 0: ${greeksPut.theta.toFixed(6)} €/day`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 7: Greeks - Vega
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 7: Vega (ν)');
console.log('  Property: Vega identical for calls and puts, always positive');
console.log('─'.repeat(70));

assertClose(greeksCall.vega, greeksPut.vega, 1e-10, `ν_call = ν_put: ${greeksCall.vega.toFixed(6)}`);
assert(greeksCall.vega > 0, `Vega > 0: ${greeksCall.vega.toFixed(6)} €/1%σ`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 8: Greeks - Rho
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 8: Rho (ρ)');
console.log('  Property: Call rho positive, put rho negative');
console.log('─'.repeat(70));

assert(greeksCall.rho > 0, `Call Rho > 0: ${greeksCall.rho.toFixed(6)} €/1%r`);
assert(greeksPut.rho < 0, `Put Rho < 0: ${greeksPut.rho.toFixed(6)} €/1%r`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 9: Implied Volatility (Newton-Raphson)
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 9: Implied Volatility');
console.log('  Method: Newton-Raphson with Brenner-Subrahmanyam initial guess');
console.log('─'.repeat(70));

// Generate price with known vol, then recover it
const knownVols = [15, 25, 40, 60];
knownVols.forEach(knownVol => {
    const testPrice = blackScholesPrice({
        type: 'call',
        spot: 100,
        strike: 100,
        daysToExpiration: 90,
        riskFreeRate: 5,
        dividendYield: 2,
        volatility: knownVol
    });
    
    const iv = calculateImpliedVolatility({
        type: 'call',
        spot: 100,
        strike: 100,
        daysToExpiration: 90,
        riskFreeRate: 5,
        dividendYield: 2,
        marketPrice: testPrice
    });
    
    if (iv !== null) {
        assertClose(iv, knownVol, 0.0001, `IV recovery σ=${knownVol}%: ${iv.toFixed(4)}%`);
    } else {
        console.log(`  ✗ IV failed to converge for σ=${knownVol}%`);
        failCount++;
    }
});

// ───────────────────────────────────────────────────────────────────────────
// TEST 10: Edge Cases
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 10: Edge Cases');
console.log('─'.repeat(70));

// Deep ITM call
const deepITM = blackScholesPrice({
    type: 'call', spot: 150, strike: 100,
    daysToExpiration: 30, riskFreeRate: 5, dividendYield: 0, volatility: 20
});
assert(deepITM > 49.5, `Deep ITM call (S=150, K=100) ≈ intrinsic: ${deepITM.toFixed(4)}`);

// Deep OTM call
const deepOTM = blackScholesPrice({
    type: 'call', spot: 50, strike: 100,
    daysToExpiration: 30, riskFreeRate: 5, dividendYield: 0, volatility: 20
});
assert(deepOTM < 0.001, `Deep OTM call (S=50, K=100) ≈ 0: ${deepOTM.toFixed(8)}`);

// At expiration
const atExpiry = blackScholesPrice({
    type: 'call', spot: 105, strike: 100,
    daysToExpiration: 0, riskFreeRate: 5, dividendYield: 0, volatility: 20
});
assertClose(atExpiry, 5, 0.001, `At expiry call (S=105, K=100) = 5: ${atExpiry.toFixed(4)}`);

// Very short time
const shortTime = blackScholesPrice({
    type: 'call', spot: 100, strike: 100,
    daysToExpiration: 1, riskFreeRate: 5, dividendYield: 0, volatility: 20
});
assert(shortTime > 0 && shortTime < 1, `1 day ATM call has small time value: ${shortTime.toFixed(4)}`);

// ───────────────────────────────────────────────────────────────────────────
// TEST 11: Warrant-Specific (Conversion Ratio)
// ───────────────────────────────────────────────────────────────────────────
console.log('\n▶ TEST 11: Warrant Conversion Ratio');
console.log('  Simulating BNP warrant on Euro Stoxx 50');
console.log('─'.repeat(70));

const warrantParams = {
    type: 'put',
    spot: 4950,
    strike: 5000,
    daysToExpiration: 30,
    riskFreeRate: 2.5,
    dividendYield: 2.8,
    volatility: 16
};

const bsPrice = blackScholesPrice(warrantParams);
const ratio = 0.001;
const warrantPrice = bsPrice * ratio;
const breakeven = 5000 - (warrantPrice / ratio);

console.log(`  BS Option Price: ${bsPrice.toFixed(4)} EUR`);
console.log(`  Warrant Price:   ${warrantPrice.toFixed(6)} EUR`);
console.log(`  Breakeven:       ${breakeven.toFixed(2)}`);

assertClose(breakeven, 5000 - bsPrice, 0.01, `Breakeven = K - Premium/Ratio`);

// Warrant delta
const warrantGreeks = calculateGreeks(warrantParams);
const warrantDelta = warrantGreeks.delta * ratio;
console.log(`  Warrant Delta:   ${warrantDelta.toFixed(8)}`);
assert(warrantDelta < 0, `Put warrant delta is negative: ${warrantDelta.toFixed(8)}`);

// ═══════════════════════════════════════════════════════════════════════════
// RESULTS SUMMARY
// ═══════════════════════════════════════════════════════════════════════════
console.log('\n╔══════════════════════════════════════════════════════════════════╗');
console.log('║                         TEST RESULTS                             ║');
console.log('╠══════════════════════════════════════════════════════════════════╣');
console.log(`║  ✓ Passed: ${passCount.toString().padStart(3)}                                                   ║`);
console.log(`║  ✗ Failed: ${failCount.toString().padStart(3)}                                                   ║`);
console.log('╠══════════════════════════════════════════════════════════════════╣');

if (failCount === 0) {
    console.log('║  🎯 ALL TESTS PASSED - MATHEMATICS VALIDATED                    ║');
    console.log('║                                                                  ║');
    console.log('║  Verified against:                                               ║');
    console.log('║  • Hull, Options Futures & Other Derivatives (10th ed.)         ║');
    console.log('║  • Standard normal distribution tables                          ║');
    console.log('║  • Put-Call Parity invariants                                   ║');
    console.log('║  • Greeks mathematical properties                               ║');
} else {
    console.log('║  ⚠️  SOME TESTS FAILED - REVIEW REQUIRED                        ║');
}

console.log('╚══════════════════════════════════════════════════════════════════╝\n');

process.exit(failCount > 0 ? 1 : 0);
