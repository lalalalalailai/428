import pandas as pd
import numpy as np
from typing import Dict, Any

from utils.helpers import logger_setup

logger = logger_setup('data_quality')

class DataQualityChecker:
    def __init__(self):
        self.reports: Dict[str, Dict] = {}

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
            'score': max(0, 100 - missing_pct)
        }
        self.reports[f'{name}_completeness'] = report
        return report

    def check_consistency(self, df: pd.DataFrame,
                            name: str = 'dataset') -> Dict[str, Any]:
        issues = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].nunique() == 1:
                issues.append(f'{col}: 常数列')
            if df[col].dtype == 'float64':
                if (df[col] % 1 == 0).all():
                    pass
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
        for col in numeric_df.columns:
            Q1 = numeric_df[col].quantile(0.25)
            Q3 = numeric_df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower, upper = Q1 - 3 * IQR, Q3 + 3 * IQR
            outliers = ((numeric_df[col] < lower) | (numeric_df[col] > upper)).sum()
            n_outliers_total += outliers
            if outliers > 0:
                outlier_details[col] = int(outliers)
        report = {
            'name': name,
            'dimension': 'accuracy',
            'total_outliers': int(n_outliers_total),
            'outlier_pct': float(n_outliers_total / (len(df) * len(numeric_df.columns)) * 100) if len(df) > 0 and len(numeric_df.columns) > 0 else 0,
            'outlier_columns': outlier_details,
            'score': max(0, 100 - n_outliers_total / len(df) * 2)
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
