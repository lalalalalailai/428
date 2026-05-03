import sys
import os
import pytest
import pandas as pd
import numpy as np

SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


@pytest.fixture
def src_dir():
    return SRC_DIR


@pytest.fixture
def sample_data():
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='D')
    n = len(dates)
    close = 3000 + np.cumsum(np.random.randn(n) * 10)
    df = pd.DataFrame({
        'date': dates,
        'open': close + np.random.randn(n) * 5,
        'high': close + abs(np.random.randn(n) * 15),
        'low': close - abs(np.random.randn(n) * 15),
        'close': close,
        'volume': np.random.randint(10000, 100000, n),
        'settle': close + np.random.randn(n) * 3,
    })
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    return df
