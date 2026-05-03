import pytest
import pandas as pd
import numpy as np


def test_data_loader_import():
    from data.data_loader import DataLoader
    assert DataLoader is not None
    loader = DataLoader()
    assert hasattr(loader, 'load_futures_data')


def test_data_quality_checker_import():
    from data.data_quality_checker import DataQualityChecker
    assert DataQualityChecker is not None
    checker = DataQualityChecker()
    assert hasattr(checker, 'check_date_range_compliance')
    assert hasattr(checker, 'check_completeness')


def test_data_preprocessor_import():
    from data.data_preprocessor import DataPreprocessor
    assert DataPreprocessor is not None
    preprocessor = DataPreprocessor()
    assert hasattr(preprocessor, 'handle_missing_values')


def test_feature_engineer_import():
    from data.feature_engineer import FeatureEngineer
    assert FeatureEngineer is not None
    engineer = FeatureEngineer()
    assert hasattr(engineer, 'create_lag_features')
    assert hasattr(engineer, 'create_moving_averages')


def test_data_quality_checker_date_range(sample_data):
    from data.data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    df = sample_data.reset_index()
    result = checker.check_date_range_compliance(df, date_col='date', name='test_futures')
    assert isinstance(result, dict)
    assert 'compliant' in result
    assert 'score' in result
    assert result['name'] == 'test_futures'
    assert result['dimension'] == 'date_range_compliance'


def test_data_quality_checker_completeness(sample_data):
    from data.data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()
    result = checker.check_completeness(sample_data, name='test_futures')
    assert isinstance(result, dict)
    assert result['dimension'] == 'completeness'
    assert 'missing_pct' in result
    assert 'score' in result
    assert result['missing_pct'] == 0.0
    assert result['score'] == 100.0
