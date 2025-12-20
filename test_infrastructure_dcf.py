"""
Unit Tests for Infrastructure DCF Valuation Engine

Tests cover:
1. Sector classification and override logic
2. Expansion phase detection
3. FCF normalization (historical vs forward)
4. Maintenance capex estimation
5. WACC calculation
6. Complete DCF valuation
7. Edge cases and error handling

Author: Claude Code
Version: 1.0
"""

import unittest
import numpy as np
from infrastructure_dcf import (
    InfrastructureDCF,
    CompanyFinancials,
    InfrastructureSector,
    ValuationMethod,
    ValuationResult,
    quick_valuation
)


class TestCompanyFinancials(unittest.TestCase):
    """Test CompanyFinancials data validation"""

    def test_valid_financials_creation(self):
        """Test creating valid CompanyFinancials object"""
        financials = CompanyFinancials(
            company_name="Test Tower Co",
            sector="towers",
            revenues=[1000, 1100, 1200],
            ebitda=[500, 550, 600],
            depreciation=[100, 110, 120],
            interest_expense=[50, 55, 60],
            capex=[300, 350, 400],
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100
        )

        self.assertEqual(financials.company_name, "Test Tower Co")
        self.assertEqual(financials.net_debt, 1900)
        self.assertEqual(len(financials.revenues), 3)

    def test_net_debt_calculation(self):
        """Test net debt is calculated correctly"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3,
            total_debt=2000,
            cash=500
        )

        self.assertEqual(financials.net_debt, 1500)

    def test_time_series_mismatch_raises_error(self):
        """Test that mismatched time series lengths raise error"""
        with self.assertRaises(ValueError):
            CompanyFinancials(
                company_name="Test",
                sector="towers",
                revenues=[1000, 1100],  # 2 years
                ebitda=[500, 550, 600],  # 3 years - mismatch!
                depreciation=[100, 110, 120],
                interest_expense=[50, 55, 60],
                capex=[300, 350, 400]
            )

    def test_insufficient_data_raises_error(self):
        """Test that < 3 years of data raises error"""
        with self.assertRaises(ValueError):
            CompanyFinancials(
                company_name="Test",
                sector="towers",
                revenues=[1000, 1100],  # Only 2 years
                ebitda=[500, 550],
                depreciation=[100, 110],
                interest_expense=[50, 55],
                capex=[300, 350]
            )


class TestSectorClassification(unittest.TestCase):
    """Test sector classification and override logic"""

    def test_tower_company_fingerprint_detection(self):
        """Test automatic detection of tower company characteristics"""
        # Create company with tower-like characteristics
        financials = CompanyFinancials(
            company_name="Pseudo Tower Co",
            sector="telecommunications",  # Mislabeled
            revenues=[1000, 1100, 1200],
            ebitda=[600, 660, 720],  # 60% EBITDA margin (tower-like)
            depreciation=[150, 165, 180],
            interest_expense=[200, 220, 240],
            capex=[500, 1500, 200],  # Volatile (expansion then maintenance)
            total_debt=5000,  # 5000/720 = ~7x leverage (tower-like)
            cash=100,
            total_assets=4000,  # 4000/1200 = 3.3x asset intensity
            market_cap=3000,
            shares_outstanding=100
        )

        dcf = InfrastructureDCF(financials)
        dcf.validate_and_classify()

        # Should be reclassified as TOWERS
        self.assertEqual(dcf._sector_enum, InfrastructureSector.TOWERS)
        self.assertTrue(dcf.validation_results['sector_override'])
        self.assertEqual(dcf.validation_results['original_sector'], 'telecommunications')

    def test_explicit_tower_sector(self):
        """Test explicit tower sector classification"""
        financials = CompanyFinancials(
            company_name="Tower Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3
        )

        dcf = InfrastructureDCF(financials)
        dcf.validate_and_classify()

        self.assertEqual(dcf._sector_enum, InfrastructureSector.TOWERS)

    def test_reit_fingerprint_detection(self):
        """Test REIT detection based on characteristics"""
        financials = CompanyFinancials(
            company_name="REIT Co",
            sector="other",
            revenues=[1000, 1050, 1100],
            ebitda=[650, 680, 710],  # 65% margin
            depreciation=[200, 210, 220],
            interest_expense=[150, 155, 160],
            capex=[100, 110, 120],  # Low capex
            total_debt=3000,
            cash=50,
            total_assets=6000,  # High asset intensity
            market_cap=4000,
            shares_outstanding=200
        )

        dcf = InfrastructureDCF(financials)
        dcf.validate_and_classify()

        # Should be classified as REIT
        self.assertEqual(dcf._sector_enum, InfrastructureSector.REITS)


class TestExpansionPhaseDetection(unittest.TestCase):
    """Test detection of expansion phase companies"""

    def test_sustained_negative_fcf_flag(self):
        """Test sustained negative FCF triggers flag"""
        financials = CompanyFinancials(
            company_name="Expansion Co",
            sector="towers",
            revenues=[1000, 1200, 1400, 1600, 1800],
            ebitda=[500, 600, 700, 800, 900],
            depreciation=[100, 120, 140, 160, 180],
            interest_expense=[50, 60, 70, 80, 90],
            capex=[1000, 1200, 1400, 1600, 800],  # High capex causing negative FCF
            operating_cash_flow=[450, 540, 630, 720, 810],  # Positive OCF
            total_debt=5000,
            market_cap=6000,
            shares_outstanding=100
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()

        # FCF should be negative for most years
        negative_count = sum(1 for fcf in historical_fcf if fcf < 0)
        self.assertGreater(negative_count, 0)

        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        self.assertTrue(use_forward)
        self.assertIn('sustained_negative_fcf', flags)

    def test_high_growth_capex_flag(self):
        """Test high capex/EBITDA ratio triggers flag"""
        financials = CompanyFinancials(
            company_name="High Capex Co",
            sector="towers",
            revenues=[1000, 1100, 1200, 1300, 1400],
            ebitda=[500, 550, 600, 650, 700],
            depreciation=[100] * 5,
            interest_expense=[50] * 5,
            capex=[600, 700, 800, 900, 500],  # Capex > EBITDA for 4 years
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()
        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        self.assertTrue(use_forward)
        self.assertIn('high_growth_capex', flags)

    def test_infrastructure_sector_flag(self):
        """Test infrastructure sector automatically triggers flag"""
        financials = CompanyFinancials(
            company_name="Infra Co",
            sector="towers",
            revenues=[1000] * 5,
            ebitda=[500] * 5,
            depreciation=[100] * 5,
            interest_expense=[50] * 5,
            capex=[200] * 5,  # Low, stable capex
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()
        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        self.assertIn('infrastructure_sector', flags)

    def test_ebitda_fcf_divergence_flag(self):
        """Test positive EBITDA with negative FCF triggers flag"""
        financials = CompanyFinancials(
            company_name="Divergence Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,  # Positive
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[800, 800, 800],  # High capex causing negative FCF
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()

        self.assertGreater(financials.ebitda[-1], 0)
        self.assertLess(historical_fcf[-1], 0)

        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        self.assertIn('ebitda_fcf_divergence', flags)

    def test_contracted_revenues_flag(self):
        """Test long contract duration triggers flag"""
        financials = CompanyFinancials(
            company_name="Contracted Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3,
            avg_contract_duration=15  # 15-year contracts
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()
        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        self.assertIn('contracted_revenues', flags)

    def test_no_flags_for_stable_company(self):
        """Test stable company doesn't trigger forward FCF"""
        financials = CompanyFinancials(
            company_name="Stable Co",
            sector="other",  # Not infrastructure
            revenues=[1000, 1020, 1040],
            ebitda=[300, 306, 312],
            depreciation=[100, 102, 104],
            interest_expense=[30, 31, 32],
            capex=[80, 82, 84],  # Low, stable capex
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()
        use_forward, flags = dcf._should_use_forward_fcf(historical_fcf)

        # Should have few or no flags (less than 2)
        self.assertLess(len(flags), 2)
        self.assertFalse(use_forward)


class TestFCFNormalization(unittest.TestCase):
    """Test FCF normalization methods"""

    def test_historical_fcf_calculation_from_ocf(self):
        """Test FCF calculation when operating cash flow is provided"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200, 300, 250],
            operating_cash_flow=[450, 480, 500]
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()

        # FCF = OCF - Capex
        expected_fcf = [
            450 - 200,  # 250
            480 - 300,  # 180
            500 - 250   # 250
        ]

        np.testing.assert_array_almost_equal(historical_fcf, expected_fcf)

    def test_historical_fcf_approximation(self):
        """Test FCF approximation when OCF not provided"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            effective_tax_rate=0.25
        )

        dcf = InfrastructureDCF(financials)
        historical_fcf = dcf._calculate_historical_fcf()

        # EBIT = EBITDA - Depreciation = 500 - 100 = 400
        # Tax = 400 * 0.25 = 100
        # OCF ≈ EBITDA - Tax = 500 - 100 = 400
        # FCF = OCF - Capex = 400 - 200 = 200

        for fcf in historical_fcf:
            self.assertAlmostEqual(fcf, 200.0)

    def test_forward_fcf_with_guidance(self):
        """Test forward FCF uses maintenance capex guidance"""
        financials = CompanyFinancials(
            company_name="Guided Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500, 550, 600],
            depreciation=[100, 110, 120],
            interest_expense=[50] * 3,
            capex=[800, 900, 1000],  # High growth capex
            maintenance_capex_guidance=150,  # Explicit guidance
            effective_tax_rate=0.25
        )

        dcf = InfrastructureDCF(financials)
        forward_fcf = dcf._calculate_forward_fcf()

        # EBITDA = 600
        # Maintenance Capex = 150 (guidance)
        # EBIT = 600 - 120 = 480
        # Tax = 480 * 0.25 = 120
        # FCF = 600 - 150 - 120 = 330

        self.assertAlmostEqual(forward_fcf, 330.0, places=1)

    def test_forward_fcf_with_benchmark(self):
        """Test forward FCF uses industry benchmark when no guidance"""
        financials = CompanyFinancials(
            company_name="Tower Co",
            sector="towers",
            revenues=[1000, 1100, 1200],
            ebitda=[500, 550, 600],
            depreciation=[100, 110, 120],
            interest_expense=[50] * 3,
            capex=[800, 900, 1000],
            effective_tax_rate=0.25
        )

        dcf = InfrastructureDCF(financials)
        dcf._sector_enum = InfrastructureSector.TOWERS
        forward_fcf = dcf._calculate_forward_fcf()

        # Maintenance capex = 1200 * 0.06 = 72 (towers benchmark)
        # EBITDA = 600
        # EBIT = 600 - 120 = 480
        # Tax = 480 * 0.25 = 120
        # FCF = 600 - 72 - 120 = 408

        self.assertAlmostEqual(forward_fcf, 408.0, places=1)

    def test_ebitda_baseline_uses_latest(self):
        """Test EBITDA baseline uses latest year when stable"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500, 505, 510],  # Low volatility
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3
        )

        dcf = InfrastructureDCF(financials)
        baseline = dcf._get_ebitda_baseline()

        # Should use latest (510) since volatility is low
        self.assertEqual(baseline, 510)

    def test_ebitda_baseline_uses_average_when_volatile(self):
        """Test EBITDA baseline uses average when volatile"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[400, 600, 500],  # High volatility
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3
        )

        dcf = InfrastructureDCF(financials)
        baseline = dcf._get_ebitda_baseline()

        # Should use average due to volatility
        expected_avg = np.mean([400, 600, 500])
        self.assertAlmostEqual(baseline, expected_avg)


class TestMaintenanceCapex(unittest.TestCase):
    """Test maintenance capex estimation"""

    def test_maintenance_capex_from_guidance(self):
        """Test maintenance capex uses guidance when provided"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3,
            maintenance_capex_guidance=75
        )

        dcf = InfrastructureDCF(financials)
        maintenance = dcf._estimate_maintenance_capex()

        self.assertEqual(maintenance, 75)

    def test_maintenance_capex_from_benchmark(self):
        """Test maintenance capex uses industry benchmark"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000, 1100, 1200],
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[300] * 3
        )

        dcf = InfrastructureDCF(financials)
        dcf._sector_enum = InfrastructureSector.TOWERS
        maintenance = dcf._estimate_maintenance_capex()

        # Towers: 6% of revenues
        expected = 1200 * 0.06
        self.assertAlmostEqual(maintenance, expected)

    def test_maintenance_capex_from_percentile(self):
        """Test maintenance capex uses 25th percentile as proxy"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="other",
            revenues=[1000] * 5,
            ebitda=[500] * 5,
            depreciation=[100] * 5,
            interest_expense=[50] * 5,
            capex=[100, 150, 500, 600, 700]  # Low capex years likely = maintenance
        )

        dcf = InfrastructureDCF(financials)
        dcf._sector_enum = InfrastructureSector.OTHER
        maintenance = dcf._estimate_maintenance_capex()

        # 25th percentile of [100, 150, 500, 600, 700]
        expected = np.percentile([100, 150, 500, 600, 700], 25)
        self.assertAlmostEqual(maintenance, expected)


class TestWACCCalculation(unittest.TestCase):
    """Test WACC calculation"""

    def test_wacc_with_custom_beta(self):
        """Test WACC uses custom asset beta when provided"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[200] * 3,
            capex=[300] * 3,
            total_debt=5000,
            market_cap=5000,
            risk_free_rate=0.03,
            market_risk_premium=0.06,
            asset_beta=0.5,
            effective_tax_rate=0.25
        )

        dcf = InfrastructureDCF(financials)
        wacc = dcf.calculate_wacc()

        # Cost of equity = 0.03 + 0.5 * 0.06 = 0.06
        # Cost of debt = 200/5000 * (1-0.25) = 0.04 * 0.75 = 0.03
        # WACC = 0.5 * 0.06 + 0.5 * 0.03 = 0.045

        self.assertAlmostEqual(wacc, 0.045, places=4)

    def test_wacc_with_benchmark_beta(self):
        """Test WACC uses benchmark beta for sector"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[200] * 3,
            capex=[300] * 3,
            total_debt=5000,
            market_cap=5000,
            risk_free_rate=0.03,
            market_risk_premium=0.06,
            effective_tax_rate=0.25
        )

        dcf = InfrastructureDCF(financials)
        dcf._sector_enum = InfrastructureSector.TOWERS
        wacc = dcf.calculate_wacc()

        # Towers benchmark beta = 0.6
        # Cost of equity = 0.03 + 0.6 * 0.06 = 0.066
        expected_coe = 0.03 + 0.6 * 0.06

        self.assertGreater(wacc, 0.03)  # Should be > risk-free
        self.assertLess(wacc, expected_coe)  # Should be < cost of equity (due to debt)

    def test_wacc_zero_debt(self):
        """Test WACC when company has no debt"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[0] * 3,
            capex=[300] * 3,
            total_debt=0,
            market_cap=5000,
            asset_beta=0.6,
            risk_free_rate=0.03,
            market_risk_premium=0.06
        )

        dcf = InfrastructureDCF(financials)
        wacc = dcf.calculate_wacc()

        # WACC = Cost of Equity (no debt)
        expected_coe = 0.03 + 0.6 * 0.06
        self.assertAlmostEqual(wacc, expected_coe, places=4)


class TestDCFValuation(unittest.TestCase):
    """Test complete DCF valuation"""

    def test_basic_valuation(self):
        """Test basic DCF valuation produces positive value"""
        financials = CompanyFinancials(
            company_name="Test Tower Co",
            sector="towers",
            revenues=[1000, 1100, 1200],
            ebitda=[500, 550, 600],
            depreciation=[100, 110, 120],
            interest_expense=[50, 55, 60],
            capex=[200, 220, 240],
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100,
            current_price=50.0
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Sanity checks
        self.assertGreater(result.enterprise_value, 0)
        self.assertGreater(result.equity_value, 0)
        self.assertGreater(result.intrinsic_value_per_share, 0)
        self.assertGreater(result.normalized_fcf, 0)
        self.assertGreater(result.wacc, 0)
        self.assertLess(result.wacc, 0.20)  # WACC should be reasonable

    def test_expansion_phase_valuation_positive(self):
        """Test expansion phase company gets positive valuation despite negative historical FCF"""
        financials = CompanyFinancials(
            company_name="Cellnex-like Co",
            sector="telecommunications",
            revenues=[1500, 1700, 2200, 2500, 2600],
            ebitda=[1200, 1400, 1800, 2000, 2100],
            depreciation=[300, 350, 400, 450, 500],
            interest_expense=[300, 320, 350, 380, 400],
            capex=[2000, 2500, 3000, 3500, 1000],  # High expansion capex
            operating_cash_flow=[1000, 1200, 1600, 1800, 1900],
            total_debt=12000,
            cash=500,
            total_assets=20000,
            total_equity=8000,
            market_cap=15000,
            shares_outstanding=600,
            current_price=25.00,
            maintenance_capex_guidance=150,
            avg_contract_duration=15,
            asset_beta=0.6
        )

        dcf = InfrastructureDCF(financials)

        # Check historical FCF is negative
        historical_fcf = dcf._calculate_historical_fcf()
        negative_years = sum(1 for fcf in historical_fcf if fcf < 0)
        self.assertGreater(negative_years, 0, "Historical FCF should be negative")

        # But valuation should be positive
        result = dcf.calculate_valuation()

        self.assertTrue(result.forward_fcf_used, "Should use forward FCF method")
        self.assertGreater(result.normalized_fcf, 0, "Normalized FCF should be positive")
        self.assertGreater(result.enterprise_value, 0, "Enterprise value should be positive")
        self.assertGreater(result.equity_value, 0, "Equity value should be positive")
        self.assertGreater(result.intrinsic_value_per_share, 0, "Intrinsic value should be positive")

    def test_terminal_value_contribution(self):
        """Test terminal value is significant but not excessive"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Terminal value should be 40-80% of enterprise value (typical range)
        tv_percentage = result.pv_terminal_value / result.enterprise_value

        self.assertGreater(tv_percentage, 0.30, "Terminal value too low")
        self.assertLess(tv_percentage, 0.90, "Terminal value too high")

    def test_projected_fcf_growth(self):
        """Test projected FCF shows reasonable growth"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100,
            revenue_growth_rate=0.05,
            terminal_growth_rate=0.02
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Check FCF growth
        self.assertEqual(len(result.projected_fcf), 10)  # 10 year projection

        # First year FCF should be higher than normalized
        self.assertGreater(result.projected_fcf[0], result.normalized_fcf)

        # FCF should grow each year
        for i in range(1, len(result.projected_fcf)):
            self.assertGreater(result.projected_fcf[i], result.projected_fcf[i-1])


class TestQuickValuation(unittest.TestCase):
    """Test quick valuation helper function"""

    def test_quick_valuation_minimal_inputs(self):
        """Test quick valuation with minimal inputs"""
        result = quick_valuation(
            company_name="Quick Test Co",
            ebitda_ttm=500,
            revenues_ttm=1000,
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100,
            current_price=50.0,
            sector="towers"
        )

        self.assertIsInstance(result, ValuationResult)
        self.assertGreater(result.enterprise_value, 0)
        self.assertGreater(result.intrinsic_value_per_share, 0)

    def test_quick_valuation_with_capex(self):
        """Test quick valuation with custom capex"""
        result = quick_valuation(
            company_name="Quick Test Co",
            ebitda_ttm=500,
            revenues_ttm=1000,
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100,
            current_price=50.0,
            sector="towers",
            capex=[800, 900, 1000]  # High growth capex
        )

        self.assertTrue(result.forward_fcf_used)
        self.assertGreater(result.normalized_fcf, 0)


class TestReportGeneration(unittest.TestCase):
    """Test report generation"""

    def test_generate_report(self):
        """Test report generation produces valid output"""
        financials = CompanyFinancials(
            company_name="Report Test Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            total_debt=2000,
            cash=100,
            market_cap=5000,
            shares_outstanding=100,
            current_price=50.0
        )

        dcf = InfrastructureDCF(financials)
        report = dcf.generate_report()

        # Check report contains key elements
        self.assertIn("INFRASTRUCTURE DCF VALUATION REPORT", report)
        self.assertIn("Report Test Co", report)
        self.assertIn("Normalized FCF:", report)
        self.assertIn("WACC:", report)
        self.assertIn("Enterprise Value:", report)
        self.assertIn("Equity Value:", report)
        self.assertIn("Intrinsic Value/Share:", report)
        self.assertIn("Upside/(Downside):", report)

    def test_report_shows_override(self):
        """Test report indicates sector override"""
        financials = CompanyFinancials(
            company_name="Override Test",
            sector="telecommunications",
            revenues=[1000, 1100, 1200],
            ebitda=[600, 660, 720],  # High margin
            depreciation=[150, 165, 180],
            interest_expense=[200, 220, 240],
            capex=[500, 1500, 200],
            total_debt=5000,
            cash=100,
            total_assets=4000,
            market_cap=3000,
            shares_outstanding=100,
            current_price=30.0
        )

        dcf = InfrastructureDCF(financials)
        report = dcf.generate_report()

        # Should show override
        self.assertIn("Overridden", report)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""

    def test_zero_shares_outstanding(self):
        """Test handling of zero shares outstanding"""
        financials = CompanyFinancials(
            company_name="Test",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            shares_outstanding=0  # Edge case
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Should not crash, intrinsic value per share = 0
        self.assertEqual(result.intrinsic_value_per_share, 0.0)

    def test_very_high_leverage(self):
        """Test company with very high leverage"""
        financials = CompanyFinancials(
            company_name="Levered Co",
            sector="towers",
            revenues=[1000] * 3,
            ebitda=[500] * 3,
            depreciation=[100] * 3,
            interest_expense=[400] * 3,
            capex=[200] * 3,
            total_debt=20000,  # Very high debt
            cash=0,
            market_cap=1000,
            shares_outstanding=100
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Should still calculate, equity value may be low or negative
        self.assertIsInstance(result.enterprise_value, float)

    def test_negative_growth_rate(self):
        """Test company with declining revenues"""
        financials = CompanyFinancials(
            company_name="Declining Co",
            sector="towers",
            revenues=[1200, 1100, 1000],  # Declining
            ebitda=[600, 550, 500],
            depreciation=[100] * 3,
            interest_expense=[50] * 3,
            capex=[200] * 3,
            market_cap=5000,
            shares_outstanding=100,
            revenue_growth_rate=-0.05  # Negative growth
        )

        dcf = InfrastructureDCF(financials)
        result = dcf.calculate_valuation()

        # Should handle gracefully
        self.assertIsInstance(result.enterprise_value, float)


def run_all_tests():
    """Run all test suites and return results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestCompanyFinancials,
        TestSectorClassification,
        TestExpansionPhaseDetection,
        TestFCFNormalization,
        TestMaintenanceCapex,
        TestWACCCalculation,
        TestDCFValuation,
        TestQuickValuation,
        TestReportGeneration,
        TestEdgeCases
    ]

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_all_tests()

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
