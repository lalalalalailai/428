import os
import json
import pickle
import hashlib
from datetime import datetime
from typing import Any, Optional

CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_EXPIRY = 172800

_cache_stats = {'hits': 0, 'misses': 0, 'saves': 0}

def get_cache_key(prefix: str, symbol: str, **kwargs) -> str:
    key_parts = [prefix, symbol]
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")
    return "_".join(key_parts)

def get_cache_path(key: str) -> str:
    if len(key) > 200:
        key_hash = hashlib.md5(key.encode()).hexdigest()
        key = key[:100] + '_' + key_hash
    return os.path.join(CACHE_DIR, f"{key}.pkl")

def save_cache(key: str, data: Any) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_path(key)
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump({
                'data': data,
                'timestamp': datetime.now().timestamp()
            }, f, protocol=pickle.HIGHEST_PROTOCOL)
        _cache_stats['saves'] += 1
    except Exception:
        pass

def load_cache(key: str) -> Optional[Any]:
    global _cache_stats
    cache_path = get_cache_path(key)
    if not os.path.exists(cache_path):
        _cache_stats['misses'] += 1
        return None
    
    try:
        with open(cache_path, 'rb') as f:
            cache_data = pickle.load(f)
        
        timestamp = cache_data.get('timestamp', 0)
        if datetime.now().timestamp() - timestamp > CACHE_EXPIRY:
            os.remove(cache_path)
            _cache_stats['misses'] += 1
            return None
        
        _cache_stats['hits'] += 1
        return cache_data.get('data')
    except Exception:
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
            except OSError:
                pass
        _cache_stats['misses'] += 1
        return None

def clear_cache() -> None:
    for file in os.listdir(CACHE_DIR):
        if file.endswith('.pkl'):
            try:
                os.remove(os.path.join(CACHE_DIR, file))
            except OSError:
                pass

def clear_expired_cache() -> None:
    for file in os.listdir(CACHE_DIR):
        if file.endswith('.pkl'):
            cache_path = os.path.join(CACHE_DIR, file)
            try:
                with open(cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                timestamp = cache_data.get('timestamp', 0)
                if datetime.now().timestamp() - timestamp > CACHE_EXPIRY:
                    os.remove(cache_path)
            except Exception:
                try:
                    os.remove(cache_path)
                except OSError:
                    pass

def get_cache_stats() -> dict:
    total = _cache_stats['hits'] + _cache_stats['misses']
    hit_rate = _cache_stats['hits'] / total * 100 if total > 0 else 0
    return {
        'hits': _cache_stats['hits'],
        'misses': _cache_stats['misses'],
        'saves': _cache_stats['saves'],
        'hit_rate': f"{hit_rate:.1f}%",
        'cache_files': len([f for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')]),
        'cache_size_mb': sum(os.path.getsize(os.path.join(CACHE_DIR, f)) for f in os.listdir(CACHE_DIR) if f.endswith('.pkl')) / 1024 / 1024
    }


def smart_cache_key(*args, **kwargs) -> str:
    key_parts = []
    for arg in args:
        try:
            hash(arg)
            key_parts.append(str(arg))
        except TypeError:
            if hasattr(arg, 'shape'):
                key_parts.append(f"{type(arg).__name__}_shape{'_'.join(str(s) for s in arg.shape)}")
            elif hasattr(arg, '__len__'):
                key_parts.append(f"{type(arg).__name__}_len{len(arg)}")
            else:
                key_parts.append(f"{type(arg).__name__}_{hashlib.md5(str(arg).encode()).hexdigest()[:8]}")

    for k, v in sorted(kwargs.items()):
        try:
            hash(v)
            key_parts.append(f"{k}={v}")
        except TypeError:
            if hasattr(v, 'shape'):
                key_parts.append(f"{k}={type(v).__name__}_shape{'_'.join(str(s) for s in v.shape)}")
            elif hasattr(v, '__len__'):
                key_parts.append(f"{k}={type(v).__name__}_len{len(v)}")
            else:
                key_parts.append(f"{k}={type(v).__name__}_{hashlib.md5(str(v).encode()).hexdigest()[:8]}")

    raw_key = "_".join(key_parts)
    if len(raw_key) > 200:
        return raw_key[:100] + '_' + hashlib.md5(raw_key.encode()).hexdigest()
    return raw_key


def cache_warmup(cache_keys: list) -> dict:
    results = {'loaded': 0, 'missed': 0, 'errors': 0}
    for key in cache_keys:
        try:
            data = load_cache(key)
            if data is not None:
                results['loaded'] += 1
            else:
                results['missed'] += 1
        except Exception:
            results['errors'] += 1
    return results


def get_cache_recommendations() -> list:
    recommendations = []
    stats = get_cache_stats()
    total = stats['hits'] + stats['misses']

    if total == 0:
        recommendations.append("缓存尚未使用，建议对高频数据加载启用缓存")
        return recommendations

    hit_rate = stats['hits'] / total * 100 if total > 0 else 0

    if hit_rate < 30:
        recommendations.append(f"命中率偏低({hit_rate:.1f}%)，建议检查缓存键生成逻辑或延长过期时间")
    elif hit_rate < 60:
        recommendations.append(f"命中率一般({hit_rate:.1f}%)，建议对重复查询场景增加缓存预热")
    else:
        recommendations.append(f"命中率良好({hit_rate:.1f}%)，缓存策略有效")

    if stats['cache_size_mb'] > 500:
        recommendations.append(f"缓存占用{stats['cache_size_mb']:.1f}MB较大，建议清理过期数据或压缩存储")

    if stats['misses'] > stats['hits'] * 2:
        recommendations.append("未命中次数远超命中次数，建议扩大缓存容量或优化缓存键设计")

    if stats['cache_files'] > 1000:
        recommendations.append(f"缓存文件数({stats['cache_files']})过多，建议合并小文件或定期清理")

    return recommendations