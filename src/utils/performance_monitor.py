import time
import functools
from typing import Dict, List, Optional, Callable
from collections import defaultdict


class PerformanceMonitor:
    def __init__(self):
        self._timers: Dict[str, float] = {}
        self._records: Dict[str, List[float]] = defaultdict(list)

    def start_timer(self, operation: str) -> None:
        self._timers[operation] = time.perf_counter()

    def end_timer(self, operation: str) -> Optional[float]:
        start = self._timers.pop(operation, None)
        if start is None:
            return None
        elapsed_ms = (time.perf_counter() - start) * 1000
        self._records[operation].append(elapsed_ms)
        return elapsed_ms

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        stats = {}
        for op, times in self._records.items():
            if not times:
                continue
            stats[op] = {
                'count': len(times),
                'avg_ms': sum(times) / len(times),
                'min_ms': min(times),
                'max_ms': max(times),
                'total_ms': sum(times),
            }
        return stats

    def get_slow_operations(self, threshold_ms: float = 500) -> List[Dict[str, float]]:
        slow = []
        for op, times in self._records.items():
            if not times:
                continue
            avg_ms = sum(times) / len(times)
            if avg_ms >= threshold_ms:
                slow.append({
                    'operation': op,
                    'avg_ms': avg_ms,
                    'max_ms': max(times),
                    'count': len(times),
                })
        slow.sort(key=lambda x: x['avg_ms'], reverse=True)
        return slow

    def generate_report(self) -> str:
        stats = self.get_stats()
        if not stats:
            return "暂无性能监控数据"

        lines = ["## ⚡ 性能监控报告", ""]
        lines.append("| 操作 | 调用次数 | 平均(ms) | 最小(ms) | 最大(ms) | 总计(ms) |")
        lines.append("|------|---------|----------|----------|----------|----------|")

        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['total_ms'], reverse=True)
        for op, s in sorted_stats:
            lines.append(
                f"| {op} | {s['count']} | {s['avg_ms']:.1f} | "
                f"{s['min_ms']:.1f} | {s['max_ms']:.1f} | {s['total_ms']:.1f} |"
            )

        slow_ops = self.get_slow_operations()
        if slow_ops:
            lines.append("")
            lines.append("### 🐌 慢操作 (>500ms)")
            for s in slow_ops:
                lines.append(f"- **{s['operation']}**: 平均{s['avg_ms']:.0f}ms, "
                             f"峰值{s['max_ms']:.0f}ms, 调用{s['count']}次")

        total_time = sum(s['total_ms'] for s in stats.values())
        total_calls = sum(s['count'] for s in stats.values())
        lines.append("")
        lines.append(f"**总耗时**: {total_time:.0f}ms | **总调用**: {total_calls}次 | "
                     f"**监控操作数**: {len(stats)}")

        return "\n".join(lines)

    def reset(self) -> None:
        self._timers.clear()
        self._records.clear()


def monitor_performance(operation_name: str = None):
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            performance_monitor.start_timer(op_name)
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                performance_monitor.end_timer(op_name)
        return wrapper
    return decorator


performance_monitor = PerformanceMonitor()
