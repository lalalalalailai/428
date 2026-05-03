import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime

from utils.helpers import logger_setup

logger = logger_setup('data_quality')

VALID_DATE_START = '2020-01-01'
VALID_DATE_END = '2025-12-31'

CN_HOLIDAYS_2020_2025 = [
    '2020-01-01','2020-01-25','2020-01-26','2020-01-27','2020-01-28','2020-01-29','2020-01-30','2020-04-04','2020-04-05','2020-04-06','2020-05-01','2020-05-02','2020-05-03','2020-05-04','2020-05-05','2020-06-25','2020-06-26','2020-06-27','2020-10-01','2020-10-02','2020-10-03','2020-10-04','2020-10-05','2020-10-06','2020-10-07','2020-10-08',
    '2021-01-01','2021-01-02','2021-01-03','2021-02-11','2021-02-12','2021-02-13','2021-02-14','2021-02-15','2021-02-16','2021-02-17','2021-04-03','2021-04-04','2021-04-05','2021-05-01','2021-05-02','2021-05-03','2021-05-04','2021-05-05','2021-06-12','2021-06-13','2021-06-14','2021-09-19','2021-09-20','2021-09-21','2021-10-01','2021-10-02','2021-10-03','2021-10-04','2021-10-05','2021-10-06','2021-10-07',
    '2022-01-01','2022-01-02','2022-01-03','2022-01-31','2022-02-01','2022-02-02','2022-02-03','2022-02-04','2022-02-05','2022-02-06','2022-04-03','2022-04-04','2022-04-05','2022-05-01','2022-05-02','2022-05-03','2022-05-04','2022-06-03','2022-06-04','2022-06-05','2022-09-10','2022-09-11','2022-09-12','2022-10-01','2022-10-02','2022-10-03','2022-10-04','2022-10-05','2022-10-06','2022-10-07',
    '2023-01-01','2023-01-02','2023-01-21','2023-01-22','2023-01-23','2023-01-24','2023-01-25','2023-01-26','2023-01-27','2023-04-05','2023-05-01','2023-05-02','2023-05-03','2023-06-22','2023-06-23','2023-06-24','2023-09-29','2023-09-30','2023-10-01','2023-10-02','2023-10-03','2023-10-04','2023-10-05','2023-10-06',
    '2024-01-01','2024-02-10','2024-02-11','2024-02-12','2024-02-13','2024-02-14','2024-02-15','2024-02-16','2024-02-17','2024-04-04','2024-04-05','2024-04-06','2024-05-01','2024-05-02','2024-05-03','2024-05-04','2024-05-05','2024-06-08','2024-06-09','2024-06-10','2024-09-15','2024-09-16','2024-09-17','2024-10-01','2024-10-02','2024-10-03','2024-10-04','2024-10-05','2024-10-06','2024-10-07',
    '2025-01-01','2025-01-28','2025-01-29','2025-01-30','2025-01-31','2025-02-01','2025-02-02','2025-02-03','2025-02-04','2025-04-04','2025-04-05','2025-04-06','2025-05-01','2025-05-02','2025-05-03','2025-05-04','2025-05-05','2025-05-31','2025-06-01','2025-06-02','2025-10-01','2025-10-02','2025-10-03','2025-10-04','2025-10-05','2025-10-06','2025-10-07','2025-10-08',
]
CN_HOLIDAYS = set(pd.to_datetime(CN_HOLIDAYS_2020_2025).date)


class DataQualityChecker:
    def __init__(self):
        self.reports: Dict[str, Dict] = {}
        self.data_type: str = 'general'

    def set_data_type(self, data_type: str):
        self.data_type = data_type

    def _is_non_trading_day(self, dt):
        if hasattr(dt, 'date'):
            d = dt.date()
        else:
            d = dt
        return d.weekday() >= 5 or d in CN_HOLIDAYS

    def check_date_range_compliance(self, df: pd.DataFrame,
                                      date_col: str = 'date',
                                      name: str = 'dataset') -> Dict[str, Any]:
        valid_start = pd.Timestamp(VALID_DATE_START)
        valid_end = pd.Timestamp(VALID_DATE_END)

        if date_col not in df.columns:
            if isinstance(df.index, pd.DatetimeIndex):
                dates = df.index
            else:
                return {'name': name, 'dimension': 'date_range', 'compliant': True,
                        'note': '无日期列，跳过日期范围检查'}
        else:
            dates = pd.to_datetime(df[date_col], errors='coerce')

        if len(dates) == 0:
            return {'name': name, 'dimension': 'date_range', 'compliant': True,
                    'note': '空数据集'}

        out_of_range = ((dates < valid_start) | (dates > valid_end)).sum()
        total = len(dates)
        min_date = dates.min()
        max_date = dates.max()

        report = {
            'name': name,
            'dimension': 'date_range_compliance',
            'valid_range': f'{VALID_DATE_START} ~ {VALID_DATE_END}',
            'actual_range': f'{min_date} ~ {max_date}',
            'total_records': int(total),
            'out_of_range_records': int(out_of_range),
            'compliant': bool(out_of_range == 0),
            'compliance_rate': float((total - out_of_range) / total * 100) if total > 0 else 100,
            'score': float((total - out_of_range) / total * 100) if total > 0 else 100
        }
        self.reports[f'{name}_date_range'] = report
        if out_of_range > 0:
            logger.warning(f"数据日期范围违规: {name} 有 {out_of_range}/{total} 条记录超出"
                          f" [{VALID_DATE_START}, {VALID_DATE_END}]")
        return report

    def check_value_continuity(self, df: pd.DataFrame,
                                 date_col: str = 'date',
                                 name: str = 'dataset',
                                 max_gap_days: int = None) -> Dict[str, Any]:
        if date_col not in df.columns and not isinstance(df.index, pd.DatetimeIndex):
            return {'name': name, 'dimension': 'continuity', 'note': '无日期列，跳过'}

        if max_gap_days is None:
            if self.data_type == 'futures':
                max_gap_days = 5
            elif self.data_type == 'remote_sensing':
                max_gap_days = 35
            else:
                max_gap_days = 7

        dates = pd.to_datetime(df[date_col], errors='coerce') if date_col in df.columns else df.index
        if isinstance(dates, pd.Series):
            dates = pd.DatetimeIndex(dates.values)
        dates_sorted = dates.sort_values()
        gaps = dates_sorted[1:] - dates_sorted[:-1]
        if isinstance(gaps, pd.TimedeltaIndex):
            gap_days = pd.Series(gaps.days.values, dtype=int)
        elif hasattr(gaps, 'dt'):
            gap_days = pd.Series(gaps.dt.days.values, dtype=int)
        else:
            gap_days = pd.Series(gaps, dtype=int)

        if self.data_type == 'futures':
            large_gaps = 0
            for i in range(len(gap_days)):
                gap = gap_days.iloc[i]
                if gap <= 3:
                    continue
                start_dt = dates_sorted[i]
                end_dt = dates_sorted[i + 1]
                current = start_dt + pd.Timedelta(days=1)
                non_trading = 0
                while current < end_dt:
                    if self._is_non_trading_day(current):
                        non_trading += 1
                    current += pd.Timedelta(days=1)
                trading_gap = gap - non_trading
                if trading_gap > max_gap_days:
                    large_gaps += 1
        else:
            large_gaps = (gap_days > max_gap_days).sum()

        max_gap = gap_days.max() if len(gap_days) > 0 else 0
        median_gap = pd.Series(gap_days).median() if len(gap_days) > 0 else 0

        report = {
            'name': name,
            'dimension': 'value_continuity',
            'max_gap_days': int(max_gap),
            'median_gap_days': float(median_gap),
            'large_gaps_count': int(large_gaps),
            'max_gap_threshold': max_gap_days,
            'data_type': self.data_type,
            'continuous': bool(large_gaps == 0),
            'score': max(0, 100 - large_gaps * 5)
        }
        self.reports[f'{name}_continuity'] = report
        return report

    def check_completeness(self, df: pd.DataFrame,
                             name: str = 'dataset') -> Dict[str, Any]:
        total_cells = df.shape[0] * df.shape[1]
        missing_total = df.isnull().sum().sum()
        missing_pct = missing_total / total_cells * 100 if total_cells > 0 else 0
        col_missing = (df.isnull().sum() / len(df) * 100).to_dict()
        row_missing = (df.isnull().sum(axis=1) / df.shape[1] * 100).describe().to_dict()
        report = {
            'name': name,
            'dimension': 'completeness',
            'total_cells': int(total_cells),
            'missing_cells': int(missing_total),
            'missing_pct': float(missing_pct),
            'columns_with_missing': sum(1 for v in col_missing.values() if v > 0),
            'max_col_missing_pct': max(col_missing.values()) if col_missing else 0,
            'avg_row_missing_pct': float(row_missing.get('mean', 0)),
            'score': 100.0 if missing_pct < 2.0 else max(0, 100 - missing_pct)
        }
        self.reports[f'{name}_completeness'] = report
        return report

    def check_consistency(self, df: pd.DataFrame,
                            name: str = 'dataset') -> Dict[str, Any]:
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        skip_const_cols = {'year', 'month', 'day', 'quarter', 'week', 'weekday', 'season',
                           'latitude', 'longitude', 'lat', 'lon', 'lng',
                           'elevation', 'altitude', '经度', '纬度', '海拔'}
        for col in numeric_cols:
            if col.lower() in skip_const_cols:
                continue
            if df[col].nunique() == 1 and len(df) > 10:
                issues.append(f'{col}: 常数列')
        date_cols = [c for c in df.columns if 'date' in c.lower()]
        for col in date_cols:
            try:
                pd.to_datetime(df[col])
            except (ValueError, TypeError):
                issues.append(f'{col}: 非法日期格式')
        duplicates = df.duplicated().sum()
        report = {
            'name': name,
            'dimension': 'consistency',
            'issues_found': len(issues),
            'issue_details': issues[:10],
            'duplicate_rows': int(duplicates),
            'duplicate_pct': float(duplicates / len(df) * 100) if len(df) > 0 else 0,
            'score': max(0, 100 - len(issues) * 5 - duplicates / len(df) * 10)
        }
        self.reports[f'{name}_consistency'] = report
        return report

    def check_accuracy(self, df: pd.DataFrame,
                         name: str = 'dataset') -> Dict[str, Any]:
        numeric_df = df.select_dtypes(include=[np.number])
        n_outliers_total = 0
        outlier_details = {}
        iqr_multiplier = 3.0
        if self.data_type == 'futures':
            iqr_multiplier = 4.0
        elif self.data_type == 'weather':
            iqr_multiplier = 3.5
        physical_limit_cols = {
            'precipitation': (0, 300), 'rainfall': (0, 300), 'rain': (0, 300),
            'precip': (0, 300), '降水量': (0, 300),
            'humidity': (0, 100), '湿度': (0, 100),
            'latitude': (-90, 90), 'longitude': (-180, 180),
            'lat': (-90, 90), 'lon': (-180, 180), 'lng': (-180, 180),
            'ndvi': (-1, 1), 'evi': (-1, 1), 'ndwi': (-1, 1),
            'vhi': (0, 100), 'drought_index': (0, 100),
            'lst_drought_index': (-5, 5), '干旱指数': (0, 100),
            'spi': (-4, 4), 'lst_anomaly': (-20, 20),
        }
        high_iqr_cols = {'volume', 'vol', 'turnover', '成交量',
                          'wind_speed', 'wind', '风速', 'gust', '阵风',
                          'hold', 'open_interest', '持仓量', '持仓',
                          'open', 'high', 'low', 'close', 'settle',
                          '开盘价', '最高价', '最低价', '收盘价', '结算价'}
        for col in numeric_df.columns:
            col_lower = col.lower()
            if col_lower in physical_limit_cols:
                pmin, pmax = physical_limit_cols[col_lower]
                outliers = ((numeric_df[col] < pmin) | (numeric_df[col] > pmax)).sum()
            else:
                col_iqr = iqr_multiplier
                if col_lower in high_iqr_cols:
                    col_iqr = 5.0
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                if IQR == 0:
                    continue
                lower, upper = Q1 - col_iqr * IQR, Q3 + col_iqr * IQR
                outliers = ((numeric_df[col] < lower) | (numeric_df[col] > upper)).sum()
            n_outliers_total += outliers
            if outliers > 0:
                outlier_details[col] = int(outliers)
        total_values = len(df) * len(numeric_df.columns)
        outlier_pct = n_outliers_total / total_values * 100 if total_values > 0 else 0
        if outlier_pct < 0.5:
            score = 100.0
        elif self.data_type == 'futures':
            score = max(0, 100 - outlier_pct * 5)
        elif self.data_type == 'weather':
            score = max(0, 100 - outlier_pct * 3)
        else:
            score = max(0, 100 - n_outliers_total / len(df) * 2)
        report = {
            'name': name,
            'dimension': 'accuracy',
            'total_outliers': int(n_outliers_total),
            'outlier_pct': float(outlier_pct),
            'outlier_columns': outlier_details,
            'iqr_multiplier': iqr_multiplier,
            'score': float(score)
        }
        self.reports[f'{name}_accuracy'] = report
        return report

    def generate_overall_report(self) -> Dict[str, Any]:
        scores = []
        for key, report in self.reports.items():
            if isinstance(report, dict) and 'score' in report:
                scores.append(report['score'])
        overall_score = np.mean(scores) if scores else 0
        return {
            'total_checks': len(self.reports),
            'overall_score': float(overall_score),
            'grade': 'A' if overall_score >= 90 else 'B' if overall_score >= 70 else 'C' if overall_score >= 50 else 'D',
            'details': self.reports
        }

    def reset(self):
        self.reports.clear()
