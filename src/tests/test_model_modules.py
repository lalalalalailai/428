import pytest


def test_pricing_model_import():
    from models.pricing_model import PricingModel
    assert PricingModel is not None
    assert hasattr(PricingModel, '__init__')


def test_causal_discovery_import():
    from models.causal_discovery import CausalDiscovery
    assert CausalDiscovery is not None
    assert hasattr(CausalDiscovery, '__init__')


def test_risk_assessor_import():
    from models.risk_assessor import RiskAssessor
    assert RiskAssessor is not None
    assert hasattr(RiskAssessor, '__init__')


def test_agri_pc_import():
    from models.agri_pc import AgriPC
    assert AgriPC is not None
    assert hasattr(AgriPC, '__init__')


def test_acml_import():
    from models.acml import ACML
    assert ACML is not None
    assert hasattr(ACML, '__init__')


def test_ccp_import():
    from models.ccp import CausalConformalPricing
    assert CausalConformalPricing is not None
    assert hasattr(CausalConformalPricing, '__init__')


def test_premium_calculator_import():
    from models.premium_calculator import PremiumCalculator
    assert PremiumCalculator is not None
    assert hasattr(PremiumCalculator, '__init__')


def test_social_value_import():
    from models.social_value import SocialValueCalculator
    assert SocialValueCalculator is not None
    assert hasattr(SocialValueCalculator, '__init__')


def test_extreme_risk_warning_import():
    from models.extreme_risk_warning import ExtremeRiskWarning
    assert ExtremeRiskWarning is not None
    assert hasattr(ExtremeRiskWarning, '__init__')
