"""
Cellnex Telecom (CLNX.MC) - FINAL RIGOROUS DCF VALUATION

Adjustments made for maximum financial rigor:
1. Conservative WACC (higher beta to reflect European tower risks)
2. Realistic terminal growth (EU GDP growth)
3. Conservative maintenance capex
4. Rigorous tax rate (no aggressive tax planning)
5. Custom growth rates as specified, but with reality checks

Author: Infrastructure DCF Engine
Date: December 2024
"""

from infrastructure_dcf import CompanyFinancials, InfrastructureDCF
import numpy as np


def cellnex_final_rigorous():
    """
    FINAL rigorous DCF with conservative assumptions.
    """

    print("="*80)
    print("CELLNEX TELECOM (CLNX.MC) - FINAL RIGOROUS DCF")
    print("Conservative Assumptions for Maximum Financial Rigor")
    print("="*80)
    print()

    # ============================================================================
    # CONSERVATIVE ADJUSTMENTS
    # ============================================================================

    print("CONSERVATIVE ADJUSTMENTS FROM INITIAL RUN:")
    print("-" * 80)
    print("1. WACC: Increased beta from 0.61 to 0.70 (EU tower risks)")
    print("2. Terminal Growth: Reduced from 2.5% to 2.0% (EU GDP)")
    print("3. Tax Rate: Increased from 20% to 22% (less aggressive optimization)")
    print("4. Maintenance Capex: Increased from €180M to €200M (conservative)")
    print("5. Extended projection to 12 years (reduce terminal value weight)")
    print()

    # ============================================================================
    # DATA (same as before, but with conservative parameters)
    # ============================================================================

    revenues_historical = [1714, 1989, 2659, 3142, 3478]
    ebitda_historical = [1245, 1451, 2156, 2674, 3245]
    depreciation_historical = [445, 523, 687, 856, 1045]
    interest_expense_historical = [387, 492, 689, 825, 945]
    capex_historical = [2145, 8756, 11234, 6789, 1234]
    operating_cash_flow_historical = [1089, 1287, 1834, 2398, 2987]

    # Balance sheet
    total_debt = 19500
    cash = 1200
    net_debt = 18300
    total_assets = 42500
    total_equity = 15800

    # Market data
    market_cap = 16500
    shares_outstanding = 700
    current_price = 23.57

    # ============================================================================
    # CONSERVATIVE PARAMETERS
    # ============================================================================

    # Higher maintenance capex (more conservative)
    maintenance_capex = 200  # vs €180M in initial run

    # Contract duration (unchanged)
    avg_contract_duration = 12

    # Market rates (unchanged)
    risk_free_rate = 0.028
    market_risk_premium = 0.060

    # CONSERVATIVE BETA
    # Reasons for higher beta (0.70 vs 0.61):
    # - European market maturity (lower growth potential)
    # - Regulatory risk (telecom regulation)
    # - Customer concentration (MNOs consolidation)
    # - Competitive intensity (neutral host models)
    asset_beta = 0.70

    # CONSERVATIVE TAX RATE
    # Reasons for 22% vs 20%:
    # - EU minimum tax directives (15% global minimum)
    # - Limited tax optimization post-BEPS
    # - Local country mix weighted average
    effective_tax_rate = 0.22

    # CONSERVATIVE TERMINAL GROWTH
    # EU GDP growth forecast: 1.5-2.0%
    # Tower organic growth premium: 0.0-0.5%
    # Conservative: 2.0%
    terminal_growth_rate = 0.020

    # ============================================================================
    # CUSTOM GROWTH RATES (as specified)
    # ============================================================================

    # Years 1-5: As requested
    custom_growth = [0.08, 0.10, 0.12, 0.15, 0.18]

    # Years 6-12: Linear taper from 18% to 2.0%
    # Extended projection period to reduce terminal value weight
    projection_years = 12

    for i in range(projection_years - 5):
        progress = (i + 1) / (projection_years - 5)
        growth = 0.18 * (1 - progress) + terminal_growth_rate * progress
        custom_growth.append(growth)

    # ============================================================================
    # CREATE FINANCIALS
    # ============================================================================

    financials = CompanyFinancials(
        company_name="Cellnex Telecom S.A. (CLNX.MC)",
        sector="towers",

        # Historical data
        revenues=revenues_historical,
        ebitda=ebitda_historical,
        depreciation=depreciation_historical,
        interest_expense=interest_expense_historical,
        capex=capex_historical,
        operating_cash_flow=operating_cash_flow_historical,

        # Balance sheet
        total_debt=total_debt,
        cash=cash,
        total_assets=total_assets,
        total_equity=total_equity,

        # Market data
        market_cap=market_cap,
        shares_outstanding=shares_outstanding,
        current_price=current_price,

        # CONSERVATIVE parameters
        maintenance_capex_guidance=maintenance_capex,
        avg_contract_duration=avg_contract_duration,
        asset_beta=asset_beta,

        # Market rates
        risk_free_rate=risk_free_rate,
        market_risk_premium=market_risk_premium,
        effective_tax_rate=effective_tax_rate,

        # Growth
        revenue_growth_rate=0.08,
        terminal_growth_rate=terminal_growth_rate
    )

    # ============================================================================
    # VALUATION
    # ============================================================================

    dcf = InfrastructureDCF(financials)
    dcf.validate_and_classify()

    # Calculate normalized FCF
    normalized_fcf, method = dcf.calculate_normalized_fcf()
    ebitda_base = dcf._get_ebitda_baseline()
    maintenance_capex_used = dcf._estimate_maintenance_capex()
    ebit = ebitda_base - financials.depreciation[-1]
    tax = ebit * effective_tax_rate

    print("NORMALIZED FCF CALCULATION:")
    print("-" * 80)
    print(f"  EBITDA (2023):            €{ebitda_base:>10,.0f}")
    print(f"  - Maintenance Capex:      €{maintenance_capex_used:>10,.0f}")
    print(f"  - Depreciation:           €{financials.depreciation[-1]:>10,.0f}")
    print(f"  = EBIT:                   €{ebit:>10,.0f}")
    print(f"  - Tax (22%):              €{tax:>10,.0f}")
    print(f"  {'='*50}")
    print(f"  Normalized FCF:           €{normalized_fcf:>10,.0f}")
    print()

    # Calculate WACC
    wacc = dcf.calculate_wacc()
    cost_of_equity = risk_free_rate + asset_beta * market_risk_premium
    cost_of_debt_pretax = financials.interest_expense[-1] / total_debt
    cost_of_debt = cost_of_debt_pretax * (1 - effective_tax_rate)

    print("WACC CALCULATION:")
    print("-" * 80)
    print(f"  Cost of Equity:           {cost_of_equity*100:>6.2f}%")
    print(f"    (rf {risk_free_rate*100:.1f}% + β {asset_beta:.2f} × MRP {market_risk_premium*100:.1f}%)")
    print(f"  Cost of Debt (after-tax): {cost_of_debt*100:>6.2f}%")
    print(f"  Equity Weight:            {(market_cap/(market_cap+total_debt))*100:>6.1f}%")
    print(f"  Debt Weight:              {(total_debt/(market_cap+total_debt))*100:>6.1f}%")
    print(f"  {'='*50}")
    print(f"  WACC:                     {wacc*100:>6.2f}%")
    print()

    # Perform valuation
    result = dcf.calculate_valuation(projection_years=projection_years, custom_growth_rates=custom_growth)

    print("PROJECTED FCF (12-YEAR EXPLICIT PERIOD):")
    print("-" * 80)
    print(f"{'Year':<6} {'Growth':<10} {'FCF (€M)':<15} {'PV (€M)':<15}")
    print("-" * 60)

    for i, fcf in enumerate(result.projected_fcf, 1):
        growth = custom_growth[i-1]
        pv = fcf / ((1 + wacc) ** i)
        print(f"  {i:<4} {growth*100:>6.1f}%    €{fcf:>12,.0f}    €{pv:>12,.0f}")

    print()
    print(f"Sum of PV (Years 1-{projection_years}):     €{result.pv_explicit_period:>12,.0f}")
    print()

    # Terminal value
    terminal_fcf = result.projected_fcf[-1] * (1 + terminal_growth_rate)
    print("TERMINAL VALUE:")
    print("-" * 80)
    print(f"  Year {projection_years} FCF:                €{result.projected_fcf[-1]:>12,.0f}")
    print(f"  × (1 + terminal growth {terminal_growth_rate*100:.1f}%):  {(1+terminal_growth_rate):>12.3f}")
    print(f"  = Terminal FCF:           €{terminal_fcf:>12,.0f}")
    print(f"  / (WACC {wacc*100:.2f}% - g {terminal_growth_rate*100:.1f}%):    {(wacc-terminal_growth_rate)*100:>6.2f}%")
    print(f"  = Terminal Value:         €{result.terminal_value:>12,.0f}")
    print(f"  × Discount factor:        {1/((1+wacc)**projection_years):>12.4f}")
    print(f"  = PV of Terminal:         €{result.pv_terminal_value:>12,.0f}")
    print()

    # Terminal value as % of EV
    tv_pct = result.pv_terminal_value / result.enterprise_value * 100

    print("="*80)
    print("VALUATION SUMMARY")
    print("="*80)
    print()
    print(f"Enterprise Value:             €{result.enterprise_value:>15,.0f}")
    print(f"  PV Explicit Period:         €{result.pv_explicit_period:>15,.0f}  ({(result.pv_explicit_period/result.enterprise_value*100):>5.1f}%)")
    print(f"  PV Terminal Value:          €{result.pv_terminal_value:>15,.0f}  ({tv_pct:>5.1f}%)")
    print()
    print(f"Less: Net Debt                €{net_debt:>15,.0f}")
    print(f"  {'='*60}")
    print(f"Equity Value:                 €{result.equity_value:>15,.0f}")
    print()
    print(f"Shares Outstanding:           {shares_outstanding:>15,.0f}M")
    print(f"  {'='*60}")
    print(f"Intrinsic Value per Share:    €{result.intrinsic_value_per_share:>15.2f}")
    print()
    print(f"Current Market Price:         €{current_price:>15.2f}")
    upside = (result.intrinsic_value_per_share / current_price - 1) * 100
    print(f"  {'='*60}")
    print(f"Implied Return:               {upside:>15.1f}%")
    print()

    # Sanity check
    if tv_pct > 70:
        print(f"⚠️  Terminal value = {tv_pct:.1f}% of EV (still high but improved)")
    elif tv_pct < 40:
        print(f"⚠️  Terminal value = {tv_pct:.1f}% of EV (very conservative)")
    else:
        print(f"✓ Terminal value = {tv_pct:.1f}% of EV (reasonable range)")

    print()

    # ============================================================================
    # IMPLIED METRICS
    # ============================================================================

    print("="*80)
    print("IMPLIED VALUATION MULTIPLES")
    print("="*80)
    print()

    ev_to_ebitda = result.enterprise_value / ebitda_historical[-1]
    ev_to_revenue = result.enterprise_value / revenues_historical[-1]
    pe_ratio = (result.intrinsic_value_per_share * shares_outstanding) / (normalized_fcf * (1-effective_tax_rate))

    print(f"EV / EBITDA (2023):           {ev_to_ebitda:>15.1f}x")
    print(f"EV / Revenue (2023):          {ev_to_revenue:>15.1f}x")
    print(f"Implied P/E:                  {pe_ratio:>15.1f}x")
    print()

    # Industry comparables
    print("INDUSTRY COMPARABLES (Reference):")
    print("-" * 80)
    print("  American Tower (AMT):   EV/EBITDA ~20-22x, P/E ~40-45x")
    print("  Crown Castle (CCI):     EV/EBITDA ~18-20x, P/E ~35-40x")
    print("  SBA Communications:     EV/EBITDA ~20-23x, P/E ~40-50x")
    print()

    if ev_to_ebitda < 15:
        print(f"✓ EV/EBITDA {ev_to_ebitda:.1f}x is conservative vs US peers (18-23x)")
    elif ev_to_ebitda > 25:
        print(f"⚠️  EV/EBITDA {ev_to_ebitda:.1f}x seems high vs US peers (18-23x)")
    else:
        print(f"✓ EV/EBITDA {ev_to_ebitda:.1f}x is reasonable vs US peers (18-23x)")

    print()

    # ============================================================================
    # FINAL INPUTS SUMMARY
    # ============================================================================

    print("="*80)
    print("FINAL INPUTS USED")
    print("="*80)
    print()

    print("FINANCIAL DATA (EUR millions):")
    print(f"  2023 Revenue:             €{revenues_historical[-1]:>10,.0f}")
    print(f"  2023 EBITDA:              €{ebitda_historical[-1]:>10,.0f}  (Margin: {ebitda_historical[-1]/revenues_historical[-1]*100:.1f}%)")
    print(f"  2023 Depreciation:        €{depreciation_historical[-1]:>10,.0f}")
    print(f"  Net Debt:                 €{net_debt:>10,.0f}")
    print(f"  Leverage (ND/EBITDA):     {net_debt/ebitda_historical[-1]:>15.1f}x")
    print()

    print("NORMALIZED FCF INPUTS:")
    print(f"  EBITDA baseline:          €{ebitda_base:>10,.0f}")
    print(f"  Maintenance Capex:        €{maintenance_capex_used:>10,.0f}  ({maintenance_capex_used/revenues_historical[-1]*100:.1f}% of revenue)")
    print(f"  Tax Rate:                 {effective_tax_rate*100:>14.1f}%")
    print(f"  Normalized FCF:           €{normalized_fcf:>10,.0f}")
    print()

    print("WACC INPUTS:")
    print(f"  Risk-Free Rate (EUR):     {risk_free_rate*100:>14.2f}%")
    print(f"  Market Risk Premium:      {market_risk_premium*100:>14.2f}%")
    print(f"  Asset Beta:               {asset_beta:>19.2f}")
    print(f"  → Cost of Equity:         {cost_of_equity*100:>14.2f}%")
    print()
    print(f"  Pre-tax Cost of Debt:     {cost_of_debt_pretax*100:>14.2f}%")
    print(f"  After-tax Cost of Debt:   {cost_of_debt*100:>14.2f}%")
    print()
    print(f"  Market Cap:               €{market_cap:>10,.0f}  ({market_cap/(market_cap+total_debt)*100:.1f}%)")
    print(f"  Market Value Debt:        €{total_debt:>10,.0f}  ({total_debt/(market_cap+total_debt)*100:.1f}%)")
    print(f"  → WACC:                   {wacc*100:>14.2f}%")
    print()

    print("GROWTH ASSUMPTIONS:")
    print(f"  Year 1:                   {custom_growth[0]*100:>14.1f}%")
    print(f"  Year 2:                   {custom_growth[1]*100:>14.1f}%")
    print(f"  Year 3:                   {custom_growth[2]*100:>14.1f}%")
    print(f"  Year 4:                   {custom_growth[3]*100:>14.1f}%")
    print(f"  Year 5:                   {custom_growth[4]*100:>14.1f}%")
    print(f"  Years 6-{projection_years}:                Taper to {terminal_growth_rate*100:.1f}%")
    print(f"  Terminal Growth:          {terminal_growth_rate*100:>14.2f}%")
    print()

    print("PROJECTION PARAMETERS:")
    print(f"  Explicit forecast period: {projection_years:>14.0f} years")
    print(f"  Terminal value method:    Perpetuity growth")
    print()

    # ============================================================================
    # RIGOR CHECKS
    # ============================================================================

    print("="*80)
    print("FINANCIAL RIGOR VALIDATION")
    print("="*80)
    print()

    checks = []

    # Check 1: WACC > Terminal Growth
    check1 = wacc > terminal_growth_rate
    checks.append(check1)
    print(f"{'✓' if check1 else '❌'} WACC ({wacc*100:.2f}%) > Terminal Growth ({terminal_growth_rate*100:.2f}%)")

    # Check 2: Terminal value proportion
    check2 = 40 <= tv_pct <= 75
    checks.append(check2)
    print(f"{'✓' if check2 else '⚠️ '} Terminal Value ({tv_pct:.1f}%) in acceptable range [40%, 75%]")

    # Check 3: EV/EBITDA multiple
    check3 = 10 <= ev_to_ebitda <= 25
    checks.append(check3)
    print(f"{'✓' if check3 else '⚠️ '} EV/EBITDA ({ev_to_ebitda:.1f}x) reasonable for towers [10x-25x]")

    # Check 4: Leverage ratio
    leverage = net_debt / ebitda_historical[-1]
    check4 = 3 <= leverage <= 8
    checks.append(check4)
    print(f"{'✓' if check4 else '⚠️ '} Net Debt/EBITDA ({leverage:.1f}x) sustainable [3x-8x]")

    # Check 5: Normalized FCF positive
    check5 = normalized_fcf > 0
    checks.append(check5)
    print(f"{'✓' if check5 else '❌'} Normalized FCF (€{normalized_fcf:,.0f}M) is positive")

    # Check 6: Asset beta range
    check6 = 0.5 <= asset_beta <= 0.9
    checks.append(check6)
    print(f"{'✓' if check6 else '⚠️ '} Asset Beta ({asset_beta:.2f}) in infrastructure range [0.5-0.9]")

    # Check 7: Maintenance capex
    maint_pct = maintenance_capex_used / revenues_historical[-1]
    check7 = 0.03 <= maint_pct <= 0.10
    checks.append(check7)
    print(f"{'✓' if check7 else '⚠️ '} Maintenance Capex ({maint_pct*100:.1f}% of revenue) [3%-10%]")

    # Check 8: Tax rate
    check8 = 0.15 <= effective_tax_rate <= 0.30
    checks.append(check8)
    print(f"{'✓' if check8 else '⚠️ '} Effective Tax Rate ({effective_tax_rate*100:.0f}%) reasonable [15%-30%]")

    # Check 9: EBITDA margin
    ebitda_margin = ebitda_historical[-1] / revenues_historical[-1]
    check9 = 0.60 <= ebitda_margin <= 0.95
    checks.append(check9)
    print(f"{'✓' if check9 else '⚠️ '} EBITDA Margin ({ebitda_margin*100:.1f}%) typical for towers [60%-95%]")

    # Check 10: Discount rate spread
    check10 = (wacc - terminal_growth_rate) >= 0.02
    checks.append(check10)
    print(f"{'✓' if check10 else '❌'} WACC-g spread ({(wacc-terminal_growth_rate)*100:.2f}%) sufficient [>2%]")

    passed = sum(checks)
    total = len(checks)

    print()
    print(f"RIGOR SCORE: {passed}/{total} checks passed ({passed/total*100:.0f}%)")
    print()

    if passed == total:
        print("✅ EXCELLENT - All rigor checks passed")
    elif passed >= total * 0.9:
        print("✓ VERY GOOD - Most checks passed, valuation is robust")
    elif passed >= total * 0.8:
        print("✓ GOOD - Valuation is reasonable with minor issues")
    else:
        print("⚠️  REVIEW NEEDED - Multiple assumptions need verification")

    print()
    print("="*80)
    print("CONCLUSION")
    print("="*80)
    print()

    if upside > 100:
        conclusion = "SIGNIFICANTLY UNDERVALUED"
        recommendation = "STRONG BUY"
    elif upside > 50:
        conclusion = "MODERATELY UNDERVALUED"
        recommendation = "BUY"
    elif upside > 20:
        conclusion = "SLIGHTLY UNDERVALUED"
        recommendation = "ACCUMULATE"
    elif upside > -10:
        conclusion = "FAIRLY VALUED"
        recommendation = "HOLD"
    else:
        conclusion = "OVERVALUED"
        recommendation = "AVOID"

    print(f"Valuation Conclusion: {conclusion}")
    print(f"Implied Recommendation: {recommendation}")
    print()
    print(f"Intrinsic Value: €{result.intrinsic_value_per_share:.2f}")
    print(f"Market Price: €{current_price:.2f}")
    print(f"Upside Potential: {upside:.1f}%")
    print()
    print("Key assumptions:")
    print(f"  - WACC: {wacc*100:.2f}% (conservative)")
    print(f"  - Terminal growth: {terminal_growth_rate*100:.1f}% (EU GDP)")
    print(f"  - Custom growth years 1-5: 8%, 10%, 12%, 15%, 18%")
    print(f"  - {projection_years}-year explicit forecast period")
    print()
    print("="*80)

    return result, financials, custom_growth, wacc


if __name__ == "__main__":
    result, financials, growth_rates, wacc = cellnex_final_rigorous()
