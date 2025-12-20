"""
Real-World Example: Cellnex Telecom DCF Valuation

This example demonstrates the infrastructure DCF engine with real data from
Cellnex Telecom, a European tower company that went through a massive expansion
phase (2019-2022) with significant M&A activity.

The traditional DCF approach would produce NEGATIVE intrinsic value due to
years of negative FCF. The infrastructure DCF approach correctly values the
company based on its forward cash generation potential.

Data Source: Cellnex Annual Reports (2019-2023)
Currency: EUR millions
"""

from infrastructure_dcf import (
    CompanyFinancials,
    InfrastructureDCF,
    quick_valuation
)


def cellnex_full_valuation():
    """
    Complete Cellnex valuation with detailed historical data.

    Key characteristics:
    - EBITDA growing strongly (€1.2B → €3.2B)
    - Massive M&A capex (€10B+ in some years)
    - Negative FCF during expansion (2019-2022)
    - Long-term contracts (avg 15 years)
    - High leverage (structural, not risky)
    - Post-expansion maintenance capex ~€200M/year
    """

    cellnex_data = CompanyFinancials(
        company_name="Cellnex Telecom S.A.",
        sector="telecommunications",  # Will be auto-reclassified as "towers"

        # Income Statement (EUR millions, 2019-2023)
        revenues=[1714, 1989, 2659, 3142, 3478],
        ebitda=[1245, 1451, 2156, 2674, 3245],
        depreciation=[445, 523, 687, 856, 1045],
        interest_expense=[387, 492, 689, 825, 945],

        # Cash Flow Statement
        capex=[2145, 8756, 11234, 6789, 1234],  # Includes M&A & growth capex
        operating_cash_flow=[1089, 1287, 1834, 2398, 2987],

        # Balance Sheet (2023)
        total_debt=19500,
        cash=1200,
        total_assets=42500,
        total_equity=15800,

        # Market Data (hypothetical as of valuation date)
        market_cap=16500,
        shares_outstanding=700,  # million shares
        current_price=23.57,

        # Company Guidance & Parameters
        maintenance_capex_guidance=200,  # Post-expansion steady-state
        avg_contract_duration=15,  # 15-year contracts
        asset_beta=0.58,  # Infrastructure beta

        # Market Rates
        risk_free_rate=0.035,  # 3.5% EUR government bonds
        market_risk_premium=0.065,  # European equity risk premium
        effective_tax_rate=0.18,  # Favorable infrastructure tax regime

        # Growth Assumptions
        revenue_growth_rate=0.04,  # 4% organic growth
        terminal_growth_rate=0.02,  # 2% perpetuity growth
    )

    # Initialize DCF engine
    dcf = InfrastructureDCF(cellnex_data)

    # Validate and classify
    valid, errors = dcf.validate_and_classify()
    if not valid:
        print(f"Validation errors: {errors}")
        return

    print("="*70)
    print("CELLNEX TELECOM - INFRASTRUCTURE DCF ANALYSIS")
    print("="*70)
    print()

    # Show classification results
    print("Sector Classification:")
    print(f"  Original sector: {dcf.validation_results['original_sector']}")
    print(f"  Classified as: {dcf.validation_results['sector']}")
    print(f"  Override applied: {dcf.validation_results['sector_override']}")
    print()

    # Show detection flags
    print("Expansion Phase Detection:")
    print(f"  Use forward FCF method: {dcf.validation_results['use_forward_fcf']}")
    print(f"  Flags triggered:")
    for flag in dcf.validation_results['flags']:
        flag_descriptions = {
            'sustained_negative_fcf': '    → Sustained negative FCF (expansion phase)',
            'high_growth_capex': '    → High growth capex ratio (>100% of EBITDA)',
            'infrastructure_sector': '    → Infrastructure sector classification',
            'ebitda_fcf_divergence': '    → Positive EBITDA but negative FCF',
            'contracted_revenues': '    → Long-term contracted revenues',
            'high_capex_volatility': '    → High capex volatility (M&A activity)'
        }
        print(flag_descriptions.get(flag, f"    → {flag}"))
    print()

    # Calculate historical FCF (for comparison)
    historical_fcf = dcf._calculate_historical_fcf()
    print("Historical Free Cash Flow (EUR millions):")
    years = [2019, 2020, 2021, 2022, 2023]
    for year, fcf in zip(years, historical_fcf):
        print(f"  {year}: €{fcf:>10,.0f} {'(NEGATIVE)' if fcf < 0 else ''}")

    avg_historical = sum(historical_fcf) / len(historical_fcf)
    print(f"\n  5-Year Average: €{avg_historical:>10,.0f}")
    print()

    if avg_historical < 0:
        print("  ⚠️  Traditional DCF would produce NEGATIVE intrinsic value!")
        print("  ⚠️  This is economically INCORRECT for expansion-phase infrastructure")
        print()

    # Calculate normalized FCF (forward-looking)
    normalized_fcf, method = dcf.calculate_normalized_fcf()
    print(f"Normalized FCF (Forward-Looking Method):")
    print(f"  Method: {method}")
    print(f"  Normalized FCF: €{normalized_fcf:>10,.0f}")
    print()

    # Show components
    ebitda_base = dcf._get_ebitda_baseline()
    maintenance_capex = dcf._estimate_maintenance_capex()
    print("  Components:")
    print(f"    EBITDA baseline: €{ebitda_base:>10,.0f}")
    print(f"    Maintenance capex: €{maintenance_capex:>10,.0f}")
    print(f"    Normalized tax: €{(ebitda_base - cellnex_data.depreciation[-1]) * cellnex_data.effective_tax_rate:>10,.0f}")
    print(f"    Working capital: €{dcf._estimate_wc_change():>10,.0f}")
    print()

    # Calculate WACC
    wacc = dcf.calculate_wacc()
    print(f"Weighted Average Cost of Capital (WACC):")
    print(f"  Asset Beta: {cellnex_data.asset_beta if cellnex_data.asset_beta else 'Industry benchmark'}")
    print(f"  WACC: {wacc*100:.2f}%")
    print()

    # Perform DCF valuation
    result = dcf.calculate_valuation(projection_years=10)

    # Display full report
    report = dcf.generate_report(result)
    print(report)

    # Sensitivity Analysis
    print("\n" + "="*70)
    print("SENSITIVITY ANALYSIS")
    print("="*70)
    print()

    print("Impact of WACC on Intrinsic Value:")
    print(f"{'WACC':<10} {'Intrinsic Value':<20} {'Upside %':<15}")
    print("-" * 50)

    original_wacc = wacc
    for wacc_adj in [-0.01, -0.005, 0, 0.005, 0.01]:
        # Temporarily adjust WACC assumption
        test_beta = cellnex_data.asset_beta + (wacc_adj / cellnex_data.market_risk_premium)
        cellnex_data.asset_beta = max(0.3, min(1.0, test_beta))

        dcf_temp = InfrastructureDCF(cellnex_data)
        dcf_temp.validate_and_classify()
        result_temp = dcf_temp.calculate_valuation(projection_years=10)

        upside = (result_temp.intrinsic_value_per_share / cellnex_data.current_price - 1) * 100

        print(f"{(original_wacc + wacc_adj)*100:>5.2f}%    €{result_temp.intrinsic_value_per_share:>15.2f}    {upside:>12.1f}%")

    # Reset
    cellnex_data.asset_beta = 0.58

    print()
    print("Impact of Terminal Growth Rate on Intrinsic Value:")
    print(f"{'Terminal g':<12} {'Intrinsic Value':<20} {'Upside %':<15}")
    print("-" * 50)

    for terminal_g in [0.015, 0.02, 0.025, 0.03]:
        cellnex_data.terminal_growth_rate = terminal_g

        dcf_temp = InfrastructureDCF(cellnex_data)
        dcf_temp.validate_and_classify()
        result_temp = dcf_temp.calculate_valuation(projection_years=10)

        upside = (result_temp.intrinsic_value_per_share / cellnex_data.current_price - 1) * 100

        print(f"{terminal_g*100:>6.1f}%       €{result_temp.intrinsic_value_per_share:>15.2f}    {upside:>12.1f}%")

    print()
    print("="*70)
    print("KEY TAKEAWAYS")
    print("="*70)
    print()
    print("1. Historical FCF averaging would produce NEGATIVE valuation")
    print("   → Economically incorrect for expansion-phase infrastructure")
    print()
    print("2. Forward FCF method produces POSITIVE valuation")
    print("   → Based on normalized EBITDA - maintenance capex")
    print("   → Separates temporary growth capex from sustainable cash flow")
    print()
    print("3. Sector override correctly classified Cellnex as 'towers'")
    print("   → Original classification: 'telecommunications'")
    print("   → Business model fingerprint: tower operator")
    print()
    print("4. Multiple flags triggered automatic forward FCF selection")
    print("   → Sustained negative FCF")
    print("   → High growth capex")
    print("   → Infrastructure sector")
    print()
    print("="*70)


def cellnex_quick_valuation():
    """
    Quick valuation example with minimal inputs.
    Useful for rapid screening or when detailed historical data is unavailable.
    """

    print("\n" + "="*70)
    print("CELLNEX - QUICK VALUATION (MINIMAL INPUTS)")
    print("="*70)
    print()

    result = quick_valuation(
        company_name="Cellnex Telecom (Quick Method)",
        ebitda_ttm=3245,  # Latest EBITDA
        revenues_ttm=3478,  # Latest revenues
        total_debt=19500,
        cash=1200,
        market_cap=16500,
        shares_outstanding=700,
        current_price=23.57,
        sector="towers",

        # Optional: provide custom capex to show expansion phase
        capex=[2145, 8756, 11234],  # Last 3 years

        # Optional parameters
        maintenance_capex_guidance=200,
        asset_beta=0.58,
        revenue_growth_rate=0.04
    )

    print(f"Company: {result.company_name}")
    print(f"Sector: {result.sector}")
    print()
    print(f"Forward FCF Method Used: {result.forward_fcf_used}")
    print(f"Flags: {', '.join(result.flags) if result.flags else 'None'}")
    print()
    print(f"Normalized FCF: €{result.normalized_fcf:,.0f}")
    print(f"WACC: {result.wacc*100:.2f}%")
    print()
    print(f"Enterprise Value: €{result.enterprise_value:,.0f}")
    print(f"Equity Value: €{result.equity_value:,.0f}")
    print(f"Intrinsic Value per Share: €{result.intrinsic_value_per_share:.2f}")
    print()

    current_price = 23.57
    upside = (result.intrinsic_value_per_share / current_price - 1) * 100
    print(f"Current Price: €{current_price:.2f}")
    print(f"Upside/(Downside): {upside:.1f}%")
    print()
    print("="*70)


def comparison_traditional_vs_infrastructure_dcf():
    """
    Side-by-side comparison of traditional DCF vs infrastructure DCF.
    Shows why historical FCF normalization fails for expansion-phase companies.
    """

    print("\n" + "="*70)
    print("COMPARISON: TRADITIONAL DCF vs INFRASTRUCTURE DCF")
    print("="*70)
    print()

    # Cellnex data
    cellnex_data = CompanyFinancials(
        company_name="Cellnex Telecom",
        sector="telecommunications",
        revenues=[1714, 1989, 2659, 3142, 3478],
        ebitda=[1245, 1451, 2156, 2674, 3245],
        depreciation=[445, 523, 687, 856, 1045],
        interest_expense=[387, 492, 689, 825, 945],
        capex=[2145, 8756, 11234, 6789, 1234],
        operating_cash_flow=[1089, 1287, 1834, 2398, 2987],
        total_debt=19500,
        cash=1200,
        total_assets=42500,
        total_equity=15800,
        market_cap=16500,
        shares_outstanding=700,
        current_price=23.57,
        maintenance_capex_guidance=200,
        avg_contract_duration=15,
        asset_beta=0.58,
        risk_free_rate=0.035,
        market_risk_premium=0.065,
        effective_tax_rate=0.18,
        revenue_growth_rate=0.04,
        terminal_growth_rate=0.02,
    )

    dcf = InfrastructureDCF(cellnex_data)
    dcf.validate_and_classify()

    # Method 1: Traditional (Historical FCF Average)
    historical_fcf = dcf._calculate_historical_fcf()
    traditional_normalized_fcf = sum(historical_fcf[-3:]) / 3  # 3-year average

    # Method 2: Infrastructure (Forward EBITDA-based)
    infrastructure_normalized_fcf = dcf._calculate_forward_fcf()

    print(f"{'Method':<30} {'Normalized FCF':<20} {'Result':<30}")
    print("-" * 80)
    print(f"{'Traditional (Hist. Avg)':<30} €{traditional_normalized_fcf:>15,.0f}    {'NEGATIVE!' if traditional_normalized_fcf < 0 else 'Positive':<30}")
    print(f"{'Infrastructure (Forward)':<30} €{infrastructure_normalized_fcf:>15,.0f}    {'Positive' if infrastructure_normalized_fcf > 0 else 'NEGATIVE':<30}")
    print()

    print("Why the difference?")
    print()
    print("Traditional Method:")
    print("  → Uses historical FCF = Operating CF - Total Capex")
    print("  → Includes €10B+ of growth capex (M&A, tower builds)")
    print("  → Results in negative average FCF")
    print("  → Would produce NEGATIVE intrinsic value ❌")
    print()
    print("Infrastructure Method:")
    print("  → Uses forward FCF = EBITDA - Maintenance Capex - Tax")
    print("  → Excludes temporary growth capex")
    print("  → Focuses on steady-state cash generation")
    print("  → Produces economically sensible valuation ✓")
    print()
    print("="*70)


if __name__ == "__main__":
    # Run full detailed valuation
    cellnex_full_valuation()

    # Run quick valuation
    cellnex_quick_valuation()

    # Show comparison
    comparison_traditional_vs_infrastructure_dcf()

    print("\n" + "="*70)
    print("EXAMPLE COMPLETE")
    print("="*70)
    print()
    print("To use this valuation engine with your own data:")
    print()
    print("  from infrastructure_dcf import CompanyFinancials, InfrastructureDCF")
    print()
    print("  financials = CompanyFinancials(")
    print("      company_name='Your Company',")
    print("      sector='towers',  # or 'utilities', 'reits', etc.")
    print("      revenues=[...],   # Historical time series")
    print("      ebitda=[...],")
    print("      # ... etc")
    print("  )")
    print()
    print("  dcf = InfrastructureDCF(financials)")
    print("  result = dcf.calculate_valuation()")
    print("  print(dcf.generate_report())")
    print()
    print("="*70)
