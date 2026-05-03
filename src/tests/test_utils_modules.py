import pytest
import os
import tempfile


def test_constants_import():
    from utils.constants import CORE_SYMBOLS
    assert CORE_SYMBOLS is not None
    assert isinstance(CORE_SYMBOLS, list)
    assert len(CORE_SYMBOLS) > 0
    assert 'A0' in CORE_SYMBOLS
    assert 'C0' in CORE_SYMBOLS


def test_config_import():
    from utils.config import Config, config
    assert Config is not None
    assert config is not None
    assert hasattr(config, 'data_root')


def test_cache_utils():
    from utils.cache_utils import save_cache, load_cache, clear_cache
    test_key = '__test_auto_key__'
    test_data = {'value': 42, 'name': 'pytest'}
    save_cache(test_key, test_data)
    loaded = load_cache(test_key)
    assert loaded is not None
    assert loaded['value'] == 42
    assert loaded['name'] == 'pytest'
    clear_cache()
    after_clear = load_cache(test_key)
    assert after_clear is None


def test_reproducibility():
    from utils.reproducibility import verify_reproducibility
    result = verify_reproducibility()
    assert isinstance(result, dict)
    assert 'checks' in result
    checks = result['checks']
    assert 'models_importable' in checks
    assert 'data_exists' in checks


def test_literature_db():
    from utils.literature_db import LITERATURE_DB, REQUIRED_FIELDS
    assert isinstance(LITERATURE_DB, dict)
    assert len(LITERATURE_DB) > 0
    for algo_name, papers in LITERATURE_DB.items():
        assert isinstance(papers, list), f"{algo_name} 文献列表应为list"
        assert len(papers) >= 3, f"{algo_name} 应至少有3篇文献，实际{len(papers)}篇"
        for paper in papers:
            for field in REQUIRED_FIELDS:
                assert field in paper, f"{algo_name} 文献缺少必填字段: {field}"


def test_issue_tracker():
    from utils.issue_tracker import ISSUE_REGISTRY, get_issue_summary
    assert isinstance(ISSUE_REGISTRY, list)
    assert len(ISSUE_REGISTRY) > 0
    for issue in ISSUE_REGISTRY:
        assert 'id' in issue
        assert 'severity' in issue
        assert 'status' in issue
    summary = get_issue_summary()
    assert isinstance(summary, dict)
    assert 'total' in summary
    assert summary['total'] > 0
    assert 'by_severity' in summary
