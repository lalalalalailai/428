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