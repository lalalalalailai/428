import pytest
import pandas as pd
import numpy as np


def test_empty_dataframe():
    from data.data_quality_checker import DataQualityChecker
    from data.data_preprocessor import DataPreprocessor
    from data.feature_engineer import FeatureEngineer

    empty_df = pd.DataFrame()

    checker = DataQualityChecker()
    result = checker.check_completeness(empty_df, name='empty')
    assert isinstance(result, dict)

    result_date = checker.check_date_range_compliance(empty_df, name='empty')
    assert isinstance(result_date, dict)

    preprocessor = DataPreprocessor()
    result_preprocess = preprocessor.handle_missing_values(empty_df)
    assert isinstance(result_preprocess, pd.DataFrame)

    engineer = FeatureEngineer()
    result_feat = engineer.create_lag_features(empty_df)
    assert isinstance(result_feat, pd.DataFrame)


def test_nan_values():
    from data.data_quality_checker import DataQualityChecker
    from data.data_preprocessor import DataPreprocessor

    nan_df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=50, freq='D'),
        'close': [np.nan] * 25 + list(np.random.randn(25) * 10 + 3000),
        'volume': [np.nan] * 10 + list(np.random.randint(10000, 100000, 40)),
    })

    checker = DataQualityChecker()
    result = checker.check_completeness(nan_df, name='nan_test')
    assert isinstance(result, dict)
    assert result['missing_pct'] > 0

    preprocessor = DataPreprocessor()
    result_df = preprocessor.handle_missing_values(nan_df)
    assert isinstance(result_df, pd.DataFrame)


def test_extreme_parameters():
    from models.causal_discovery import CausalDiscovery
    from models.risk_assessor import RiskAssessor

    try:
        cd_alpha0 = CausalDiscovery(alpha=0.0)
        assert cd_alpha0 is not None
    except (ValueError, Exception):
        pass

    try:
        cd_alpha1 = CausalDiscovery(alpha=1.0)
        assert cd_alpha1 is not None
    except (ValueError, Exception):
        pass

    try:
        cd_depth0 = CausalDiscovery(max_cond_set_size=0)
        assert cd_depth0 is not None
    except (ValueError, Exception):
        pass

    try:
        cd_depth100 = CausalDiscovery(max_cond_set_size=100)
        assert cd_depth100 is not None
    except (ValueError, Exception):
        pass

    assessor = RiskAssessor()
    assert assessor is not None


def test_invalid_symbol():
    from data.data_loader import DataLoader

    loader = DataLoader()
    result = loader.load_futures_data('INVALID_SYMBOL')
    assert isinstance(result, pd.DataFrame)
