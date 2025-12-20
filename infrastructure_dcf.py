"""
Infrastructure DCF Valuation Engine

Purpose: Provide accurate DCF valuation for infrastructure companies (towers, REITs,
utilities) that have negative historical FCF due to expansion phase, but strong
forward cash generation potential.

Key Innovation: Separates maintenance capex from growth capex to calculate normalized
FCF from EBITDA, avoiding the conceptual error of using historical negative FCF.

Author: Claude Code
Version: 1.0
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValuationMethod(Enum):
    """Valuation methodology options"""
    DCF_FCFF = "dcf_fcff"  # Free Cash Flow to Firm
    DCF_FCFE = "dcf_fcfe"  # Free Cash Flow to Equity
    DDM = "ddm"  # Dividend Discount Model
    HYBRID = "hybrid"  # Combination approach


class InfrastructureSector(Enum):
    """Infrastructure sector classifications"""
    TOWERS = "towers"
    TELECOM_INFRA = "telecom_infrastructure"
    REITS = "reits"
    UTILITIES = "utilities"
    PIPELINES = "pipelines"
    TOLL_ROADS = "toll_roads"
    AIRPORTS = "airports"
    DATA_CENTERS = "data_centers"
    OTHER = "other"


@dataclass
class CompanyFinancials:
    """
    Company financial data container.
    All monetary values in millions (currency agnostic).
    Time series data: index 0 = oldest, index -1 = most recent.
    """
    # Required fields
    company_name: str
    sector: str

    # Income statement (time series)
    revenues: List[float]
    ebitda: List[float]
    depreciation: List[float]
    interest_expense: List[float]

    # Cash flow (time series)
    capex: List[float]
    operating_cash_flow: Optional[List[float]] = None

    # Balance sheet
    total_debt: float = 0.0
    cash: float = 0.0
    total_assets: float = 0.0
    total_equity: float = 0.0

    # Market data
    market_cap: float = 0.0
    shares_outstanding: float = 0.0
    current_price: float = 0.0

    # Rates & parameters
    risk_free_rate: float = 0.025
    market_risk_premium: float = 0.06
    effective_tax_rate: float = 0.25

    # Optional guidance
    maintenance_capex_guidance: Optional[float] = None
    revenue_growth_rate: float = 0.03
    terminal_growth_rate: float = 0.02
    avg_contract_duration: Optional[float] = None
    asset_beta: Optional[float] = None

    # Dividend data (optional)
    dividend_per_share: float = 0.0

    # Computed fields
    net_debt: float = field(init=False)

    def __post_init__(self):
        """Compute derived fields"""
        self.net_debt = self.total_debt - self.cash

        # Validate time series lengths
        self._validate_data()

    def _validate_data(self):
        """Validate data integrity"""
        time_series_fields = [
            ('revenues', self.revenues),
            ('ebitda', self.ebitda),
            ('depreciation', self.depreciation),
            ('capex', self.capex),
            ('interest_expense', self.interest_expense)
        ]

        lengths = {name: len(data) for name, data in time_series_fields}

        if len(set(lengths.values())) > 1:
            raise ValueError(f"Time series length mismatch: {lengths}")

        if lengths['revenues'] < 3:
            raise ValueError(f"Need at least 3 years of data, got {lengths['revenues']}")


@dataclass
class ValuationResult:
    """DCF valuation output"""
    enterprise_value: float
    equity_value: float
    intrinsic_value_per_share: float
    normalized_fcf: float
    wacc: float
    method: str
    forward_fcf_used: bool
    flags: List[str]

    # Additional details
    pv_explicit_period: float = 0.0
    pv_terminal_value: float = 0.0
    projected_fcf: List[float] = field(default_factory=list)
    terminal_value: float = 0.0

    # Diagnostics
    company_name: str = ""
    sector: str = ""
    sector_override: bool = False
    original_sector: str = ""


class InfrastructureDCF:
    """
    Main DCF valuation engine for infrastructure companies.

    Usage:
        financials = CompanyFinancials(...)
        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()
    """

    # Industry benchmark parameters
    MAINTENANCE_CAPEX_BENCHMARKS = {
        InfrastructureSector.TOWERS: 0.06,  # 6% of revenues
        InfrastructureSector.TELECOM_INFRA: 0.07,
        InfrastructureSector.REITS: 0.12,
        InfrastructureSector.UTILITIES: 0.45,
        InfrastructureSector.PIPELINES: 0.25,
        InfrastructureSector.TOLL_ROADS: 0.15,
        InfrastructureSector.AIRPORTS: 0.20,
        InfrastructureSector.DATA_CENTERS: 0.10,
    }

    ASSET_BETA_BENCHMARKS = {
        InfrastructureSector.TOWERS: 0.6,
        InfrastructureSector.TELECOM_INFRA: 0.65,
        InfrastructureSector.REITS: 0.55,
        InfrastructureSector.UTILITIES: 0.40,
        InfrastructureSector.PIPELINES: 0.50,
        InfrastructureSector.TOLL_ROADS: 0.70,
        InfrastructureSector.AIRPORTS: 0.75,
        InfrastructureSector.DATA_CENTERS: 0.65,
    }

    def __init__(self, financials: CompanyFinancials):
        self.data = financials
        self.validation_results: Optional[Dict[str, Any]] = None
        self._sector_enum: Optional[InfrastructureSector] = None

    def validate_and_classify(self) -> Tuple[bool, List[str]]:
        """
        Validate data quality and classify company sector.

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check data completeness (already validated in __post_init__)

        # Override sector classification if needed
        original_sector = self.data.sector
        self._classify_sector()

        # Detect expansion phase
        historical_fcf = self._calculate_historical_fcf()
        use_forward, flags = self._should_use_forward_fcf(historical_fcf)

        self.validation_results = {
            'use_forward_fcf': use_forward,
            'flags': flags,
            'sector': self._sector_enum.value if self._sector_enum else self.data.sector,
            'sector_override': original_sector != self.data.sector,
            'original_sector': original_sector
        }

        return len(errors) == 0, errors

    def _classify_sector(self):
        """
        Classify company into infrastructure sector.
        Override misleading sector classifications based on business model.
        """
        # First, check business model characteristics for override
        # This takes priority over sector label matching
        characteristics = self._analyze_business_model()

        # Tower company fingerprint detection (check first for telecom infrastructure)
        # Towers: EBITDA margin 50-70%, asset intensity 3-6x, low volatility, high leverage
        if (characteristics['ebitda_margin'] > 0.50 and
            characteristics['asset_intensity'] > 3.0 and
            characteristics['asset_intensity'] < 15.0 and  # Distinguish from pure REITs
            characteristics['revenue_volatility'] < 0.15 and
            characteristics['leverage'] > 4.0):

            self._sector_enum = InfrastructureSector.TOWERS
            self.data.sector = InfrastructureSector.TOWERS.value
            return

        # REIT fingerprint (very high asset intensity, real estate focused)
        # REITs: EBITDA margin > 60%, asset intensity > 8x
        if (characteristics['ebitda_margin'] > 0.60 and
            characteristics['asset_intensity'] > 8.0):

            self._sector_enum = InfrastructureSector.REITS
            self.data.sector = InfrastructureSector.REITS.value
            return

        # If no fingerprint match, try to map existing sector label
        sector_lower = self.data.sector.lower()
        sector_mapping = {
            'towers': InfrastructureSector.TOWERS,
            'tower': InfrastructureSector.TOWERS,
            'reit': InfrastructureSector.REITS,
            'reits': InfrastructureSector.REITS,
            'utilities': InfrastructureSector.UTILITIES,
            'utility': InfrastructureSector.UTILITIES,
            'pipeline': InfrastructureSector.PIPELINES,
            'pipelines': InfrastructureSector.PIPELINES,
            'toll': InfrastructureSector.TOLL_ROADS,
            'airport': InfrastructureSector.AIRPORTS,
            'airports': InfrastructureSector.AIRPORTS,
            'data center': InfrastructureSector.DATA_CENTERS,
            'datacenter': InfrastructureSector.DATA_CENTERS,
            'telecom': InfrastructureSector.TELECOM_INFRA,
            'telecommunications': InfrastructureSector.TELECOM_INFRA,
        }

        for key, sector_enum in sector_mapping.items():
            if key in sector_lower:
                self._sector_enum = sector_enum
                self.data.sector = sector_enum.value
                return

        # Default: OTHER
        self._sector_enum = InfrastructureSector.OTHER

    def _analyze_business_model(self) -> Dict[str, float]:
        """
        Analyze business model characteristics for sector classification.
        """
        latest_ebitda = self.data.ebitda[-1]
        latest_revenue = self.data.revenues[-1]

        # EBITDA margin
        ebitda_margin = latest_ebitda / latest_revenue if latest_revenue > 0 else 0

        # Asset intensity
        asset_intensity = self.data.total_assets / latest_revenue if latest_revenue > 0 else 0

        # Revenue volatility (coefficient of variation)
        revenue_volatility = self._calculate_revenue_volatility()

        # Leverage
        leverage = self.data.total_debt / latest_ebitda if latest_ebitda > 0 else 0

        # Capex intensity
        avg_capex = np.mean(self.data.capex[-3:])
        avg_revenue = np.mean(self.data.revenues[-3:])
        capex_intensity = avg_capex / avg_revenue if avg_revenue > 0 else 0

        return {
            'ebitda_margin': ebitda_margin,
            'asset_intensity': asset_intensity,
            'revenue_volatility': revenue_volatility,
            'leverage': leverage,
            'capex_intensity': capex_intensity
        }

    def _calculate_revenue_volatility(self) -> float:
        """
        Calculate revenue predictability metric.
        Lower volatility = more contracted/predictable revenues.
        """
        revenues = np.array(self.data.revenues)
        if len(revenues) < 2:
            return 0.0

        yoy_growth = np.diff(revenues) / revenues[:-1]
        volatility = np.std(yoy_growth)

        return volatility

    def _calculate_historical_fcf(self) -> List[float]:
        """
        Calculate historical Free Cash Flow.
        FCF = Operating Cash Flow - Capex
        """
        if self.data.operating_cash_flow and len(self.data.operating_cash_flow) > 0:
            # Use actual operating cash flow if available
            return [
                ocf - capex
                for ocf, capex in zip(self.data.operating_cash_flow, self.data.capex)
            ]

        # Fallback: Approximate from EBITDA
        # OCF ≈ EBITDA - Tax (simplified, ignores WC changes)
        fcf = []
        for i in range(len(self.data.ebitda)):
            ebitda = self.data.ebitda[i]
            depreciation = self.data.depreciation[i]
            capex = self.data.capex[i]

            # EBIT = EBITDA - Depreciation
            ebit = ebitda - depreciation

            # Tax on EBIT
            tax = ebit * self.data.effective_tax_rate if ebit > 0 else 0

            # Approximate OCF = EBITDA - Tax
            ocf_approx = ebitda - tax

            # FCF = OCF - Capex
            fcf_year = ocf_approx - capex
            fcf.append(fcf_year)

        return fcf

    def _should_use_forward_fcf(self, historical_fcf: List[float]) -> Tuple[bool, List[str]]:
        """
        Determine if forward-looking FCF normalization should be used.

        Returns:
            (use_forward, list_of_flags)
        """
        # Ensure sector is classified (needed for infrastructure sector check)
        if self._sector_enum is None:
            self._classify_sector()

        flags = []

        # Rule 1: Sustained Negative FCF
        if len(historical_fcf) >= 5:
            negative_years = sum(1 for fcf in historical_fcf[-5:] if fcf < 0)
            if negative_years >= 3:
                flags.append('sustained_negative_fcf')
        elif len(historical_fcf) >= 3:
            negative_years = sum(1 for fcf in historical_fcf[-3:] if fcf < 0)
            if negative_years >= 2:
                flags.append('sustained_negative_fcf')

        # Rule 2: High Growth Capex Ratio
        capex_to_ebitda = np.array(self.data.capex) / np.array(self.data.ebitda)
        if len(capex_to_ebitda) >= 5:
            high_capex_years = sum(1 for ratio in capex_to_ebitda[-5:] if ratio > 1.0)
            if high_capex_years >= 3:
                flags.append('high_growth_capex')
        elif len(capex_to_ebitda) >= 3:
            high_capex_years = sum(1 for ratio in capex_to_ebitda[-3:] if ratio > 1.0)
            if high_capex_years >= 2:
                flags.append('high_growth_capex')

        # Rule 3: Infrastructure Sector Classification
        infrastructure_sectors = [
            InfrastructureSector.TOWERS,
            InfrastructureSector.TELECOM_INFRA,
            InfrastructureSector.UTILITIES,
            InfrastructureSector.PIPELINES,
            InfrastructureSector.REITS,
            InfrastructureSector.TOLL_ROADS,
            InfrastructureSector.AIRPORTS,
            InfrastructureSector.DATA_CENTERS
        ]

        if self._sector_enum in infrastructure_sectors:
            flags.append('infrastructure_sector')

        # Rule 4: EBITDA-FCF Divergence
        latest_ebitda = self.data.ebitda[-1]
        latest_fcf = historical_fcf[-1]
        if latest_ebitda > 0 and latest_fcf < 0:
            flags.append('ebitda_fcf_divergence')

        # Rule 5: Contracted Revenue Model
        if self.data.avg_contract_duration and self.data.avg_contract_duration > 5:
            flags.append('contracted_revenues')

        # Rule 6: High Capex Volatility (indicates expansion projects)
        if len(self.data.capex) >= 5:
            capex_std = np.std(self.data.capex[-5:])
            capex_mean = np.mean(self.data.capex[-5:])
            capex_cv = capex_std / capex_mean if capex_mean > 0 else 0
            if capex_cv > 0.5:  # High coefficient of variation
                flags.append('high_capex_volatility')

        # Decision: Use forward FCF if 2+ flags triggered
        use_forward = len(flags) >= 2

        return use_forward, flags

    def calculate_normalized_fcf(self) -> Tuple[float, str]:
        """
        Calculate normalized Free Cash Flow.

        Returns:
            (normalized_fcf, method_used)
        """
        if self.validation_results is None:
            self.validate_and_classify()

        if self.validation_results['use_forward_fcf']:
            fcf = self._calculate_forward_fcf()
            method = "forward_ebitda_based"
        else:
            fcf = self._calculate_historical_average_fcf()
            method = "historical_average"

        return fcf, method

    def _calculate_forward_fcf(self) -> float:
        """
        Calculate normalized FCF using forward-looking method.
        FCF = EBITDA - Maintenance Capex - Normalized Tax - ΔWC
        """
        # Ensure sector is classified (needed for maintenance capex and WC)
        if self._sector_enum is None:
            self._classify_sector()

        # Step 1: EBITDA baseline
        ebitda_base = self._get_ebitda_baseline()

        # Step 2: Maintenance Capex
        maintenance_capex = self._estimate_maintenance_capex()

        # Step 3: Normalized Tax
        # Tax is on EBIT, not EBITDA
        latest_depreciation = self.data.depreciation[-1]
        ebit = ebitda_base - latest_depreciation
        normalized_tax = ebit * self.data.effective_tax_rate if ebit > 0 else 0

        # Step 4: Working Capital (minimal for infrastructure)
        delta_wc = self._estimate_wc_change()

        # Step 5: Normalized FCF
        normalized_fcf = ebitda_base - maintenance_capex - normalized_tax - delta_wc

        return normalized_fcf

    def _get_ebitda_baseline(self) -> float:
        """
        Get baseline EBITDA for normalization.
        Prefer latest year unless volatile, then use average.
        """
        latest_ebitda = self.data.ebitda[-1]

        if len(self.data.ebitda) >= 3:
            # Check volatility
            ebitda_recent = self.data.ebitda[-3:]
            ebitda_std = np.std(ebitda_recent)
            ebitda_mean = np.mean(ebitda_recent)
            cv = ebitda_std / ebitda_mean if ebitda_mean > 0 else 0

            if cv > 0.15:  # High volatility, use average
                return ebitda_mean

        return latest_ebitda

    def _estimate_maintenance_capex(self) -> float:
        """
        Estimate maintenance capex (excluding growth capex).

        Priority:
        1. Company guidance (if provided)
        2. Industry benchmark
        3. Historical minimum (proxy)
        """
        # Method 1: Company guidance
        if self.data.maintenance_capex_guidance is not None:
            return self.data.maintenance_capex_guidance

        # Method 2: Industry benchmark
        if self._sector_enum in self.MAINTENANCE_CAPEX_BENCHMARKS:
            benchmark_rate = self.MAINTENANCE_CAPEX_BENCHMARKS[self._sector_enum]
            latest_revenue = self.data.revenues[-1]
            return latest_revenue * benchmark_rate

        # Method 3: Historical minimum (25th percentile)
        # Assumption: minimum capex years ≈ maintenance only
        maintenance_proxy = np.percentile(self.data.capex, 25)

        return maintenance_proxy

    def _estimate_wc_change(self) -> float:
        """
        Estimate normalized working capital change.
        Infrastructure companies: minimal WC changes due to contracted revenues.
        """
        if self._sector_enum in [
            InfrastructureSector.TOWERS,
            InfrastructureSector.TELECOM_INFRA,
            InfrastructureSector.UTILITIES,
            InfrastructureSector.PIPELINES
        ]:
            return 0.0  # Assume steady-state ΔWC ≈ 0

        # For other sectors: small % of revenue growth
        latest_revenue = self.data.revenues[-1]
        revenue_growth = self.data.revenue_growth_rate

        # ΔWC ≈ 2% of incremental revenue
        delta_wc = latest_revenue * revenue_growth * 0.02

        return delta_wc

    def _calculate_historical_average_fcf(self) -> float:
        """
        Calculate historical average FCF (3-year average).
        """
        historical_fcf = self._calculate_historical_fcf()

        if len(historical_fcf) >= 3:
            return np.mean(historical_fcf[-3:])
        else:
            return np.mean(historical_fcf)

    def calculate_wacc(self) -> float:
        """
        Calculate Weighted Average Cost of Capital for infrastructure company.

        Key consideration: Use asset beta (not equity beta) as high leverage
        is structural for infrastructure, not risky.
        """
        # Cost of Equity (CAPM)
        risk_free = self.data.risk_free_rate
        market_premium = self.data.market_risk_premium

        # Asset beta
        if self.data.asset_beta is not None:
            asset_beta = self.data.asset_beta
        elif self._sector_enum in self.ASSET_BETA_BENCHMARKS:
            asset_beta = self.ASSET_BETA_BENCHMARKS[self._sector_enum]
        else:
            asset_beta = 0.60  # Default for infrastructure

        cost_of_equity = risk_free + asset_beta * market_premium

        # Cost of Debt
        latest_interest = self.data.interest_expense[-1]
        total_debt = self.data.total_debt

        if total_debt > 0:
            cost_of_debt_pretax = latest_interest / total_debt
            cost_of_debt = cost_of_debt_pretax * (1 - self.data.effective_tax_rate)
        else:
            cost_of_debt = risk_free + 0.02  # Risk-free + 200bps spread

        # Weights (market values)
        market_value_equity = self.data.market_cap
        market_value_debt = total_debt  # Assume book ≈ market for debt

        total_value = market_value_equity + market_value_debt

        if total_value > 0:
            weight_equity = market_value_equity / total_value
            weight_debt = market_value_debt / total_value
        else:
            weight_equity = 0.5
            weight_debt = 0.5

        # WACC
        wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt

        return wacc

    def calculate_valuation(self, projection_years: int = 10, custom_growth_rates: Optional[List[float]] = None) -> ValuationResult:
        """
        Perform complete DCF valuation.

        Args:
            projection_years: Number of years for explicit forecast (default 10)
            custom_growth_rates: Optional list of growth rates for each year.
                                If provided, overrides tapering growth calculation.
                                Example: [0.08, 0.10, 0.12, 0.15, 0.18]

        Returns:
            ValuationResult object
        """
        # Step 1: Validate and classify
        if self.validation_results is None:
            valid, errors = self.validate_and_classify()
            if not valid:
                raise ValueError(f"Validation failed: {errors}")

        # Step 2: Calculate normalized FCF
        normalized_fcf, fcf_method = self.calculate_normalized_fcf()

        # Step 3: Calculate WACC
        wacc = self.calculate_wacc()

        # Step 4: Project FCF
        growth_rate_high = self.data.revenue_growth_rate
        growth_rate_terminal = self.data.terminal_growth_rate

        projected_fcf = []
        fcf_prev = normalized_fcf

        # Use custom growth rates if provided, otherwise use tapering
        if custom_growth_rates is not None:
            # Validate custom growth rates
            if len(custom_growth_rates) < projection_years:
                # Extend with terminal growth rate if needed
                extended_rates = list(custom_growth_rates) + [growth_rate_terminal] * (projection_years - len(custom_growth_rates))
            else:
                extended_rates = custom_growth_rates[:projection_years]

            for year in range(1, projection_years + 1):
                growth_rate = extended_rates[year - 1]
                fcf_year = fcf_prev * (1 + growth_rate)
                projected_fcf.append(fcf_year)
                fcf_prev = fcf_year
        else:
            # Original tapering logic
            for year in range(1, projection_years + 1):
                # Taper growth: linear convergence to terminal rate
                growth_rate = (
                    growth_rate_high * (1 - year / projection_years) +
                    growth_rate_terminal * (year / projection_years)
                )

                # Apply growth to previous year's FCF
                fcf_year = fcf_prev * (1 + growth_rate)
                projected_fcf.append(fcf_year)
                fcf_prev = fcf_year

        # Step 5: Terminal Value
        terminal_fcf = projected_fcf[-1] * (1 + growth_rate_terminal)
        terminal_value = terminal_fcf / (wacc - growth_rate_terminal)

        # Step 6: Present Value
        pv_fcf = sum(
            fcf / ((1 + wacc) ** (i + 1))
            for i, fcf in enumerate(projected_fcf)
        )

        pv_terminal = terminal_value / ((1 + wacc) ** projection_years)

        # Step 7: Enterprise Value
        enterprise_value = pv_fcf + pv_terminal

        # Step 8: Equity Value
        equity_value = enterprise_value - self.data.net_debt

        # Step 9: Per Share Value
        if self.data.shares_outstanding > 0:
            intrinsic_value_per_share = equity_value / self.data.shares_outstanding
        else:
            intrinsic_value_per_share = 0.0

        # Create result object
        result = ValuationResult(
            enterprise_value=enterprise_value,
            equity_value=equity_value,
            intrinsic_value_per_share=intrinsic_value_per_share,
            normalized_fcf=normalized_fcf,
            wacc=wacc,
            method=ValuationMethod.DCF_FCFF.value,
            forward_fcf_used=self.validation_results['use_forward_fcf'],
            flags=self.validation_results['flags'],
            pv_explicit_period=pv_fcf,
            pv_terminal_value=pv_terminal,
            projected_fcf=projected_fcf,
            terminal_value=terminal_value,
            company_name=self.data.company_name,
            sector=self.validation_results['sector'],
            sector_override=self.validation_results['sector_override'],
            original_sector=self.validation_results['original_sector']
        )

        return result

    def generate_report(self, result: Optional[ValuationResult] = None) -> str:
        """
        Generate human-readable valuation report.
        """
        if result is None:
            result = self.calculate_valuation()

        upside = 0.0
        if self.data.current_price > 0:
            upside = (result.intrinsic_value_per_share / self.data.current_price - 1) * 100

        report = f"""
{'='*70}
INFRASTRUCTURE DCF VALUATION REPORT
{'='*70}

Company: {result.company_name}
Sector: {result.sector}"""

        if result.sector_override:
            report += f" (Overridden from: {result.original_sector})"

        report += f"""

{'='*70}
METHODOLOGY SELECTION
{'='*70}

Forward FCF Method Used: {'YES' if result.forward_fcf_used else 'NO'}
Detection Flags: {', '.join(result.flags) if result.flags else 'None'}

Rationale:
"""

        if result.forward_fcf_used:
            report += "  → Historical FCF is unreliable due to expansion phase\n"
            report += "  → Using normalized FCF from EBITDA - Maintenance Capex\n"
            report += "  → This avoids negative valuation from temporary growth capex\n"
        else:
            report += "  → Historical FCF is representative of steady state\n"
            report += "  → Using 3-year average historical FCF\n"

        report += f"""
{'='*70}
VALUATION RESULTS
{'='*70}

Normalized FCF:              {result.normalized_fcf:>15,.2f}
WACC:                        {result.wacc*100:>15.2f}%

Enterprise Value:            {result.enterprise_value:>15,.2f}
  PV of Explicit Period:     {result.pv_explicit_period:>15,.2f}
  PV of Terminal Value:      {result.pv_terminal_value:>15,.2f}

Net Debt:                    {self.data.net_debt:>15,.2f}
Equity Value:                {result.equity_value:>15,.2f}

Shares Outstanding:          {self.data.shares_outstanding:>15,.2f}
Intrinsic Value/Share:       {result.intrinsic_value_per_share:>15.2f}

Current Market Price:        {self.data.current_price:>15.2f}
Upside/(Downside):           {upside:>15.1f}%

{'='*70}
VALUATION COMPONENTS
{'='*70}

Terminal Value:              {result.terminal_value:>15,.2f}
Terminal Value as % of EV:   {(result.pv_terminal_value/result.enterprise_value*100):>15.1f}%

Projected FCF (first 5 years):
"""

        for i, fcf in enumerate(result.projected_fcf[:5], 1):
            report += f"  Year {i}:                     {fcf:>15,.2f}\n"

        report += f"\n{'='*70}\n"

        return report


def quick_valuation(
    company_name: str,
    ebitda_ttm: float,
    revenues_ttm: float,
    total_debt: float,
    cash: float,
    market_cap: float,
    shares_outstanding: float,
    current_price: float,
    sector: str = "infrastructure",
    **kwargs
) -> ValuationResult:
    """
    Quick valuation with minimal inputs (uses defaults for missing data).

    Args:
        company_name: Company name
        ebitda_ttm: Trailing twelve months EBITDA
        revenues_ttm: TTM revenues
        total_debt: Total debt
        cash: Cash balance
        market_cap: Market capitalization
        shares_outstanding: Shares outstanding
        current_price: Current stock price
        sector: Sector classification
        **kwargs: Additional optional parameters

    Returns:
        ValuationResult
    """
    # Build minimal historical data (3 years of flat data as baseline)
    financials = CompanyFinancials(
        company_name=company_name,
        sector=sector,
        revenues=[revenues_ttm * 0.9, revenues_ttm * 0.95, revenues_ttm],
        ebitda=[ebitda_ttm * 0.9, ebitda_ttm * 0.95, ebitda_ttm],
        depreciation=[ebitda_ttm * 0.15] * 3,  # Assume 15% of EBITDA
        interest_expense=[total_debt * 0.04] * 3,  # Assume 4% interest rate
        capex=kwargs.get('capex', [revenues_ttm * 0.5] * 3),  # Assume high capex
        total_debt=total_debt,
        cash=cash,
        total_assets=kwargs.get('total_assets', total_debt + market_cap),
        total_equity=kwargs.get('total_equity', market_cap),
        market_cap=market_cap,
        shares_outstanding=shares_outstanding,
        current_price=current_price,
        **{k: v for k, v in kwargs.items() if k not in ['capex', 'total_assets', 'total_equity']}
    )

    dcf = InfrastructureDCF(financials)
    result = dcf.calculate_valuation()

    return result
