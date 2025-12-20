"""
Cellnex Telecom (CLNX.MC) - REALISTIC DCF VALUATION

Tasas de crecimiento realistas para operador de torres maduro europeo:
- Año 1: 4.0% (escaladores contractuales CPI + nuevas tenencias)
- Año 2: 4.5% (5G densificación moderada)
- Año 3: 5.0% (edge computing inicial)
- Año 4: 5.5% (build-to-suit selectivo)
- Año 5: 6.0% (servicios valor añadido)
- Años 6-12: Convergencia lineal a 2.5% terminal

Objetivo: Generar valoración defendible con múltiplos alineados a industria

Author: Infrastructure DCF Engine
Date: December 2024
"""

from infrastructure_dcf import CompanyFinancials, InfrastructureDCF
import numpy as np


def cellnex_realistic_valuation():
    """
    DCF con tasas de crecimiento realistas para Cellnex.

    Base de comparación:
    - American Tower: EV/EBITDA 20-22x, crecimiento orgánico 4-6%
    - Crown Castle: EV/EBITDA 18-20x, crecimiento orgánico 3-5%
    - SBA Communications: EV/EBITDA 20-23x, crecimiento orgánico 4-7%
    """

    print("="*80)
    print("CELLNEX TELECOM (CLNX.MC) - REALISTIC DCF VALUATION")
    print("Tasas de Crecimiento Realistas para Operador de Torres Maduro")
    print("="*80)
    print()

    # ============================================================================
    # JUSTIFICACIÓN DE TASAS DE CRECIMIENTO
    # ============================================================================

    print("JUSTIFICACIÓN DE TASAS DE CRECIMIENTO:")
    print("-" * 80)
    print()
    print("Cellnex Profile:")
    print("  - 138,000+ sites en 12 países europeos")
    print("  - 93% EBITDA margin (altamente eficiente)")
    print("  - Fase M&A completada en 2023")
    print("  - Contratos 10-15 años con escaladores CPI + 0-2%")
    print()
    print("Crecimiento Orgánico Breakdown:")
    print()
    print("  Año 1 (4.0%): Escaladores contractuales + nuevas co-locations")
    print("    • CPI Europa 2024: ~2.5%")
    print("    • Escaladores adicionales: +0.5-1.0%")
    print("    • Nuevas tenencias: +1.0%")
    print()
    print("  Año 2 (4.5%): 5G densificación fase 2")
    print("    • Operadores añaden equipos 5G a sites existentes")
    print("    • Small cells en zonas urbanas")
    print()
    print("  Año 3 (5.0%): Edge computing inicial")
    print("    • Despliegue de edge data centers en torres")
    print("    • IoT y servicios empresariales")
    print()
    print("  Año 4 (5.5%): Build-to-suit selectivo")
    print("    • Nuevas torres en áreas de alta demanda")
    print("    • Neutral host en estadios/aeropuertos")
    print()
    print("  Año 5 (6.0%): Servicios de valor añadido")
    print("    • DAS (Distributed Antenna Systems)")
    print("    • Fiber backhaul")
    print("    • Monetización de datos de localización")
    print()
    print("  Años 6-12: Convergencia a 2.5% (crecimiento europeo de largo plazo)")
    print("    • Mercado maduro + inflación")
    print()
    print("="*80)
    print()

    # ============================================================================
    # DATOS FINANCIEROS (IGUALES AL ANÁLISIS ANTERIOR)
    # ============================================================================

    revenues_historical = [1714, 1989, 2659, 3142, 3478]
    ebitda_historical = [1245, 1451, 2156, 2674, 3245]
    depreciation_historical = [445, 523, 687, 856, 1045]
    interest_expense_historical = [387, 492, 689, 825, 945]
    capex_historical = [2145, 8756, 11234, 6789, 1234]
    operating_cash_flow_historical = [1089, 1287, 1834, 2398, 2987]

    total_debt = 19500
    cash = 1200
    net_debt = 18300
    total_assets = 42500
    total_equity = 15800

    market_cap = 16500
    shares_outstanding = 700
    current_price = 23.57

    # ============================================================================
    # PARÁMETROS CONSERVADORES
    # ============================================================================

    maintenance_capex = 200
    avg_contract_duration = 12
    risk_free_rate = 0.028
    market_risk_premium = 0.060
    asset_beta = 0.70  # Conservador para EU
    effective_tax_rate = 0.22
    terminal_growth_rate = 0.025  # Ligeramente superior por calidad de activos

    # ============================================================================
    # TASAS DE CRECIMIENTO REALISTAS
    # ============================================================================

    # Años 1-5: Crecimiento orgánico realista
    realistic_growth = [0.040, 0.045, 0.050, 0.055, 0.060]

    # Años 6-12: Convergencia lineal a terminal
    projection_years = 12

    for i in range(projection_years - 5):
        progress = (i + 1) / (projection_years - 5)
        growth = 0.060 * (1 - progress) + terminal_growth_rate * progress
        realistic_growth.append(growth)

    print("TASAS DE CRECIMIENTO APLICADAS:")
    print("-" * 80)
    for i, g in enumerate(realistic_growth, 1):
        print(f"  Año {i:>2}: {g*100:>5.2f}%")
    print(f"  Terminal: {terminal_growth_rate*100:>5.2f}%")
    print()

    # ============================================================================
    # CREAR FINANCIALS
    # ============================================================================

    financials = CompanyFinancials(
        company_name="Cellnex Telecom S.A. (CLNX.MC)",
        sector="towers",
        revenues=revenues_historical,
        ebitda=ebitda_historical,
        depreciation=depreciation_historical,
        interest_expense=interest_expense_historical,
        capex=capex_historical,
        operating_cash_flow=operating_cash_flow_historical,
        total_debt=total_debt,
        cash=cash,
        total_assets=total_assets,
        total_equity=total_equity,
        market_cap=market_cap,
        shares_outstanding=shares_outstanding,
        current_price=current_price,
        maintenance_capex_guidance=maintenance_capex,
        avg_contract_duration=avg_contract_duration,
        asset_beta=asset_beta,
        risk_free_rate=risk_free_rate,
        market_risk_premium=market_risk_premium,
        effective_tax_rate=effective_tax_rate,
        revenue_growth_rate=0.04,
        terminal_growth_rate=terminal_growth_rate
    )

    # ============================================================================
    # VALORACIÓN
    # ============================================================================

    dcf = InfrastructureDCF(financials)
    dcf.validate_and_classify()

    normalized_fcf, method = dcf.calculate_normalized_fcf()
    wacc = dcf.calculate_wacc()

    print("="*80)
    print("PARÁMETROS CLAVE DEL DCF")
    print("="*80)
    print()
    print(f"FCF Normalizado:              €{normalized_fcf:>10,.0f}M")
    print(f"WACC:                         {wacc*100:>15.2f}%")
    print(f"Terminal Growth:              {terminal_growth_rate*100:>15.2f}%")
    print(f"Spread (WACC - g):            {(wacc-terminal_growth_rate)*100:>15.2f}%")
    print()

    # Valoración
    result = dcf.calculate_valuation(projection_years=projection_years, custom_growth_rates=realistic_growth)

    # ============================================================================
    # PROYECCIÓN FCF DETALLADA
    # ============================================================================

    print("="*80)
    print("PROYECCIÓN DE FREE CASH FLOW (12 AÑOS)")
    print("="*80)
    print()
    print(f"{'Año':<6} {'Growth':<10} {'FCF (€M)':<15} {'FCF Acum':<15} {'PV (€M)':<15}")
    print("-" * 70)

    fcf_cumulative = 0
    pv_cumulative = 0

    for i, fcf in enumerate(result.projected_fcf, 1):
        growth = realistic_growth[i-1]
        fcf_cumulative += fcf
        pv = fcf / ((1 + wacc) ** i)
        pv_cumulative += pv

        print(f"  {i:<4} {growth*100:>6.2f}%    €{fcf:>12,.0f}    €{fcf_cumulative:>12,.0f}    €{pv:>12,.0f}")

    print()
    print(f"Total PV Periodo Explícito:   €{result.pv_explicit_period:>12,.0f}M")
    print()

    # Terminal Value
    terminal_fcf = result.projected_fcf[-1] * (1 + terminal_growth_rate)
    tv_pct = result.pv_terminal_value / result.enterprise_value * 100

    print("VALOR TERMINAL:")
    print("-" * 80)
    print(f"  FCF Año 12:                   €{result.projected_fcf[-1]:>12,.0f}M")
    print(f"  × (1 + g {terminal_growth_rate*100:.2f}%):            {(1+terminal_growth_rate):>12.3f}")
    print(f"  = Terminal FCF:               €{terminal_fcf:>12,.0f}M")
    print(f"  / (WACC {wacc*100:.2f}% - g {terminal_growth_rate*100:.2f}%):   {(wacc-terminal_growth_rate)*100:>6.2f}%")
    print(f"  = Terminal Value:             €{result.terminal_value:>12,.0f}M")
    print(f"  × Factor descuento:           {1/((1+wacc)**projection_years):>12.4f}")
    print(f"  = PV Terminal:                €{result.pv_terminal_value:>12,.0f}M")
    print()
    print(f"Terminal Value % del EV:      {tv_pct:>17.1f}%")

    if 50 <= tv_pct <= 70:
        print("  ✓ Proporción óptima del valor terminal")
    elif 40 <= tv_pct < 50 or 70 < tv_pct <= 75:
        print("  ✓ Proporción aceptable del valor terminal")
    else:
        print("  ⚠️  Revisar proporción del valor terminal")
    print()

    # ============================================================================
    # RESUMEN DE VALORACIÓN
    # ============================================================================

    print("="*80)
    print("RESUMEN DE VALORACIÓN")
    print("="*80)
    print()
    print(f"Enterprise Value:             €{result.enterprise_value:>15,.0f}M")
    print(f"  - PV Periodo Explícito:     €{result.pv_explicit_period:>15,.0f}M  ({result.pv_explicit_period/result.enterprise_value*100:>5.1f}%)")
    print(f"  - PV Valor Terminal:        €{result.pv_terminal_value:>15,.0f}M  ({tv_pct:>5.1f}%)")
    print()
    print(f"Menos: Deuda Neta             €{net_debt:>15,.0f}M")
    print(f"  {'='*60}")
    print(f"Equity Value:                 €{result.equity_value:>15,.0f}M")
    print()
    print(f"Acciones en Circulación:      {shares_outstanding:>15,.0f}M")
    print(f"  {'='*60}")
    print(f"VALOR INTRÍNSECO POR ACCIÓN:  €{result.intrinsic_value_per_share:>15.2f}")
    print()
    print(f"Precio de Mercado Actual:     €{current_price:>15.2f}")
    upside = (result.intrinsic_value_per_share / current_price - 1) * 100
    print(f"  {'='*60}")
    print(f"UPSIDE / (DOWNSIDE):          {upside:>15.1f}%")
    print()

    # ============================================================================
    # MÚLTIPLOS IMPLÍCITOS
    # ============================================================================

    ev_to_ebitda = result.enterprise_value / ebitda_historical[-1]
    ev_to_revenue = result.enterprise_value / revenues_historical[-1]
    price_to_fcf = (result.intrinsic_value_per_share * shares_outstanding) / normalized_fcf

    print("="*80)
    print("MÚLTIPLOS IMPLÍCITOS DE LA VALORACIÓN")
    print("="*80)
    print()
    print(f"EV / EBITDA (2023):           {ev_to_ebitda:>15.1f}x")
    print(f"EV / Ingresos (2023):         {ev_to_revenue:>15.1f}x")
    print(f"Precio / FCF:                 {price_to_fcf:>15.1f}x")
    print()

    print("COMPARACIÓN CON PEERS INTERNACIONALES:")
    print("-" * 80)
    print("  American Tower (AMT):       EV/EBITDA 20-22x  |  P/FCF 40-45x")
    print("  Crown Castle (CCI):         EV/EBITDA 18-20x  |  P/FCF 35-40x")
    print("  SBA Communications (SBAC):  EV/EBITDA 20-23x  |  P/FCF 40-50x")
    print()
    print(f"  Cellnex (valoración DCF):   EV/EBITDA {ev_to_ebitda:.1f}x  |  P/FCF {price_to_fcf:.1f}x")
    print()

    # Análisis de múltiplos
    if 18 <= ev_to_ebitda <= 23:
        print("  ✅ EV/EBITDA en línea con peers (18-23x)")
        multiple_assessment = "RAZONABLE"
    elif 15 <= ev_to_ebitda < 18:
        print("  ✓ EV/EBITDA ligeramente conservador vs peers")
        multiple_assessment = "CONSERVADOR"
    elif 23 < ev_to_ebitda <= 28:
        print("  ⚠️  EV/EBITDA ligeramente superior a peers")
        multiple_assessment = "OPTIMISTA"
    else:
        print("  ❌ EV/EBITDA fuera de rango razonable")
        multiple_assessment = "REVISAR"

    print()

    # ============================================================================
    # VALIDACIÓN DE RIGOR
    # ============================================================================

    print("="*80)
    print("VALIDACIÓN DE RIGOR FINANCIERO")
    print("="*80)
    print()

    checks = []

    # Check 1: WACC > Terminal Growth
    check1 = wacc > terminal_growth_rate
    checks.append(check1)
    print(f"{'✅' if check1 else '❌'} WACC ({wacc*100:.2f}%) > Terminal Growth ({terminal_growth_rate*100:.2f}%)")

    # Check 2: Terminal value proportion
    check2 = 40 <= tv_pct <= 75
    checks.append(check2)
    print(f"{'✅' if check2 else '⚠️ '} Valor Terminal ({tv_pct:.1f}%) en rango [40%, 75%]")

    # Check 3: EV/EBITDA multiple
    check3 = 15 <= ev_to_ebitda <= 28
    checks.append(check3)
    print(f"{'✅' if check3 else '❌'} EV/EBITDA ({ev_to_ebitda:.1f}x) razonable para torres [15x-28x]")

    # Check 4: Leverage
    leverage = net_debt / ebitda_historical[-1]
    check4 = 3 <= leverage <= 8
    checks.append(check4)
    print(f"{'✅' if check4 else '⚠️ '} Deuda Neta/EBITDA ({leverage:.1f}x) sostenible [3x-8x]")

    # Check 5: FCF positivo
    check5 = normalized_fcf > 0
    checks.append(check5)
    print(f"{'✅' if check5 else '❌'} FCF Normalizado (€{normalized_fcf:,.0f}M) positivo")

    # Check 6: Spread WACC-g
    check6 = (wacc - terminal_growth_rate) >= 0.02
    checks.append(check6)
    print(f"{'✅' if check6 else '❌'} Spread WACC-g ({(wacc-terminal_growth_rate)*100:.2f}%) > 2%")

    # Check 7: Crecimiento realista
    avg_growth_5yr = np.mean(realistic_growth[:5])
    check7 = 0.03 <= avg_growth_5yr <= 0.08
    checks.append(check7)
    print(f"{'✅' if check7 else '⚠️ '} Crecimiento promedio 5 años ({avg_growth_5yr*100:.1f}%) realista [3%-8%]")

    # Check 8: Upside razonable
    check8 = -20 <= upside <= 150
    checks.append(check8)
    print(f"{'✅' if check8 else '⚠️ '} Upside implícito ({upside:.1f}%) en rango razonable [-20%, 150%]")

    passed = sum(checks)
    total = len(checks)

    print()
    print(f"PUNTUACIÓN DE RIGOR: {passed}/{total} checks pasados ({passed/total*100:.0f}%)")
    print()

    if passed == total:
        rigor_grade = "EXCELENTE"
        rigor_symbol = "✅"
    elif passed >= total * 0.875:
        rigor_grade = "MUY BUENO"
        rigor_symbol = "✅"
    elif passed >= total * 0.75:
        rigor_grade = "BUENO"
        rigor_symbol = "✓"
    else:
        rigor_grade = "REVISAR"
        rigor_symbol = "⚠️ "

    print(f"{rigor_symbol} CALIFICACIÓN: {rigor_grade}")
    print()

    # ============================================================================
    # RECOMENDACIÓN DE INVERSIÓN
    # ============================================================================

    print("="*80)
    print("RECOMENDACIÓN DE INVERSIÓN")
    print("="*80)
    print()

    if upside > 50:
        recommendation = "COMPRA FUERTE"
        rating_symbol = "🟢"
    elif upside > 20:
        recommendation = "COMPRA"
        rating_symbol = "🟢"
    elif upside > 0:
        recommendation = "ACUMULAR"
        rating_symbol = "🟡"
    elif upside > -15:
        recommendation = "MANTENER"
        rating_symbol = "🟡"
    else:
        recommendation = "VENDER"
        rating_symbol = "🔴"

    print(f"Recomendación: {rating_symbol} {recommendation}")
    print()
    print(f"Precio Objetivo:              €{result.intrinsic_value_per_share:.2f}")
    print(f"Precio Actual:                €{current_price:.2f}")
    print(f"Potencial de Revalorización:  {upside:+.1f}%")
    print()

    # Análisis de valoración
    if multiple_assessment == "RAZONABLE":
        print("Valoración basada en:")
        print("  ✓ Múltiplos en línea con peers americanos (AMT, CCI, SBAC)")
        print("  ✓ Tasas de crecimiento realistas para operador maduro")
        print("  ✓ Spread WACC-g conservador")
        print("  ✓ Proporción terminal value dentro de rango")
    elif multiple_assessment == "CONSERVADOR":
        print("Valoración conservadora:")
        print("  • Múltiplos por debajo de peers (posible descuento EU)")
        print("  • Puede representar margen de seguridad adicional")
    elif multiple_assessment == "OPTIMISTA":
        print("Valoración ligeramente optimista:")
        print("  • Múltiplos por encima de peers")
        print("  • Considerar reducir estimaciones de crecimiento")

    print()

    # ============================================================================
    # COMPARACIÓN CON ANÁLISIS ANTERIOR
    # ============================================================================

    print("="*80)
    print("COMPARACIÓN: CRECIMIENTOS AGRESIVOS vs REALISTAS")
    print("="*80)
    print()
    print(f"{'Parámetro':<30} {'Agresivo (8-18%)':<20} {'Realista (4-6%)':<20}")
    print("-" * 70)
    print(f"{'Crecimiento Año 1':<30} {'8.0%':<20} {f'{realistic_growth[0]*100:.1f}%':<20}")
    print(f"{'Crecimiento Año 5':<30} {'18.0%':<20} {f'{realistic_growth[4]*100:.1f}%':<20}")
    print(f"{'EV/EBITDA':<30} {'48.0x':<20} {f'{ev_to_ebitda:.1f}x':<20}")
    print(f"{'Valor Intrínseco':<30} {'€196.24':<20} {f'€{result.intrinsic_value_per_share:.2f}':<20}")
    print(f"{'Upside':<30} {'+733%':<20} {f'{upside:+.1f}%':<20}")
    print(f"{'vs Peers':<30} {'2-3x superior':<20} {multiple_assessment:<20}")
    print()

    # ============================================================================
    # SENSIBILIDAD
    # ============================================================================

    print("="*80)
    print("ANÁLISIS DE SENSIBILIDAD")
    print("="*80)
    print()

    print("1. Sensibilidad al WACC:")
    print("-" * 80)
    print(f"{'WACC':<10} {'Valor Intrínseco':<20} {'Upside':<15} {'EV/EBITDA':<15}")
    print("-" * 70)

    for wacc_delta in [-0.01, -0.005, 0, 0.005, 0.01]:
        target_wacc = wacc + wacc_delta
        implied_beta = (target_wacc - (total_debt/(market_cap+total_debt)) * (interest_expense_historical[-1]/total_debt)*(1-effective_tax_rate) - (market_cap/(market_cap+total_debt)) * risk_free_rate) / ((market_cap/(market_cap+total_debt)) * market_risk_premium)

        temp_fin = CompanyFinancials(
            company_name=financials.company_name, sector=financials.sector,
            revenues=financials.revenues, ebitda=financials.ebitda,
            depreciation=financials.depreciation, interest_expense=financials.interest_expense,
            capex=financials.capex, operating_cash_flow=financials.operating_cash_flow,
            total_debt=financials.total_debt, cash=financials.cash,
            total_assets=financials.total_assets, total_equity=financials.total_equity,
            market_cap=financials.market_cap, shares_outstanding=financials.shares_outstanding,
            current_price=financials.current_price,
            maintenance_capex_guidance=financials.maintenance_capex_guidance,
            avg_contract_duration=financials.avg_contract_duration,
            asset_beta=implied_beta, risk_free_rate=financials.risk_free_rate,
            market_risk_premium=financials.market_risk_premium,
            effective_tax_rate=financials.effective_tax_rate,
            revenue_growth_rate=financials.revenue_growth_rate,
            terminal_growth_rate=financials.terminal_growth_rate
        )

        temp_dcf = InfrastructureDCF(temp_fin)
        temp_dcf.validate_and_classify()
        temp_result = temp_dcf.calculate_valuation(projection_years=projection_years, custom_growth_rates=realistic_growth)
        temp_upside = (temp_result.intrinsic_value_per_share / current_price - 1) * 100
        temp_ev_ebitda = temp_result.enterprise_value / ebitda_historical[-1]

        print(f"{target_wacc*100:>5.2f}%    €{temp_result.intrinsic_value_per_share:>15.2f}    {temp_upside:>12.1f}%    {temp_ev_ebitda:>12.1f}x")

    print()
    print("2. Sensibilidad al Terminal Growth:")
    print("-" * 80)
    print(f"{'Terminal g':<12} {'Valor Intrínseco':<20} {'Upside':<15} {'EV/EBITDA':<15}")
    print("-" * 70)

    for term_g in [0.015, 0.020, 0.025, 0.030]:
        temp_growth = realistic_growth[:5].copy()
        for i in range(projection_years - 5):
            progress = (i + 1) / (projection_years - 5)
            growth = 0.060 * (1 - progress) + term_g * progress
            temp_growth.append(growth)

        temp_fin = CompanyFinancials(
            company_name=financials.company_name, sector=financials.sector,
            revenues=financials.revenues, ebitda=financials.ebitda,
            depreciation=financials.depreciation, interest_expense=financials.interest_expense,
            capex=financials.capex, operating_cash_flow=financials.operating_cash_flow,
            total_debt=financials.total_debt, cash=financials.cash,
            total_assets=financials.total_assets, total_equity=financials.total_equity,
            market_cap=financials.market_cap, shares_outstanding=financials.shares_outstanding,
            current_price=financials.current_price,
            maintenance_capex_guidance=financials.maintenance_capex_guidance,
            avg_contract_duration=financials.avg_contract_duration,
            asset_beta=financials.asset_beta, risk_free_rate=financials.risk_free_rate,
            market_risk_premium=financials.market_risk_premium,
            effective_tax_rate=financials.effective_tax_rate,
            revenue_growth_rate=financials.revenue_growth_rate,
            terminal_growth_rate=term_g
        )

        temp_dcf = InfrastructureDCF(temp_fin)
        temp_dcf.validate_and_classify()
        temp_result = temp_dcf.calculate_valuation(projection_years=projection_years, custom_growth_rates=temp_growth)
        temp_upside = (temp_result.intrinsic_value_per_share / current_price - 1) * 100
        temp_ev_ebitda = temp_result.enterprise_value / ebitda_historical[-1]

        print(f"{term_g*100:>6.1f}%       €{temp_result.intrinsic_value_per_share:>15.2f}    {temp_upside:>12.1f}%    {temp_ev_ebitda:>12.1f}x")

    print()
    print("="*80)
    print("FIN DEL ANÁLISIS")
    print("="*80)

    return result, financials, realistic_growth, wacc, ev_to_ebitda


if __name__ == "__main__":
    result, financials, growth_rates, wacc, ev_to_ebitda = cellnex_realistic_valuation()
