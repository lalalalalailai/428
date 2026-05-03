import numpy as np
import pandas as pd
from typing import Dict, Optional
from utils.helpers import logger_setup
from utils.constants import DYNAMIC_PREMIUM_CONFIG

logger = logger_setup('dynamic_premium')


class DynamicPremiumAdjuster:
    GUIDELINE_SOURCE = '中国精算师协会《农业保险费率厘定指引2023》第四章 动态费率调整机制'
    ACTUARIAL_STANDARD = '银保监会《保险产品费率厘定监管办法》(银保监会令2021年第5号)'

    def __init__(self, base_premium: float, risk_score: float = 50.0,
                 market_volatility: float = 0.2):
        self.base_premium = base_premium
        self.risk_score = min(100.0, max(0.0, risk_score))
        self.market_volatility = min(1.0, max(0.0, market_volatility))
        self._config = DYNAMIC_PREMIUM_CONFIG
        self._adjustment_factor = None
        self._risk_loading = None
        self._market_adjustment = None
        self._seasonal_factor = None
        self._final_premium = None

    def compute_adjustment_factor(self) -> float:
        risk_component = self.risk_score / 100.0
        vol_component = self.market_volatility
        raw_factor = 1.0 + 0.5 * risk_component + 0.3 * vol_component
        self._adjustment_factor = round(max(0.5, min(2.0, raw_factor)), 6)
        return self._adjustment_factor

    def apply_risk_loading(self, confidence_level: float = 0.95) -> float:
        base_risk_loading = self._config.get('base_risk_loading', 0.15)
        if confidence_level <= 0.90:
            quantile_mult = 1.0
        elif confidence_level <= 0.95:
            quantile_mult = 1.645
        elif confidence_level <= 0.99:
            quantile_mult = 2.326
        else:
            quantile_mult = 2.576
        risk_ratio = self.risk_score / 100.0
        self._risk_loading = self.base_premium * base_risk_loading * quantile_mult * risk_ratio
        self._risk_loading = round(self._risk_loading, 4)
        return self._risk_loading

    def apply_market_adjustment(self, volatility_index: float = None) -> float:
        if volatility_index is None:
            volatility_index = self.market_volatility
        volatility_index = min(1.0, max(0.0, volatility_index))
        market_cap = self._config.get('market_adjustment_cap', 0.3)
        reference_vol = 0.2
        vol_ratio = volatility_index / reference_vol if reference_vol > 0 else 1.0
        adjustment_rate = min(market_cap, max(-market_cap, (vol_ratio - 1.0) * 0.5))
        self._market_adjustment = round(self.base_premium * adjustment_rate, 4)
        return self._market_adjustment

    def apply_seasonal_factor(self, month: int) -> float:
        month = int(month)
        if month < 1 or month > 12:
            month = 1
        seasonal_factors = self._config.get('seasonal_factors', {
            1: 1.05, 2: 1.0, 3: 1.0, 4: 0.95, 5: 0.95,
            6: 1.0, 7: 1.10, 8: 1.15, 9: 1.10, 10: 1.0,
            11: 0.95, 12: 1.05
        })
        self._seasonal_factor = seasonal_factors.get(month, 1.0)
        seasonal_premium = round(self.base_premium * (self._seasonal_factor - 1.0), 4)
        return seasonal_premium

    def get_final_premium(self) -> float:
        if self._adjustment_factor is None:
            self.compute_adjustment_factor()
        if self._risk_loading is None:
            self.apply_risk_loading()
        if self._market_adjustment is None:
            self.apply_market_adjustment()
        if self._seasonal_factor is None:
            import datetime
            self.apply_seasonal_factor(datetime.datetime.now().month)
        adjusted_base = self.base_premium * self._adjustment_factor
        self._final_premium = round(
            adjusted_base + self._risk_loading + self._market_adjustment + self.base_premium * (self._seasonal_factor - 1.0),
            2
        )
        min_premium = self.base_premium * 0.5
        max_premium = self.base_premium * 3.0
        self._final_premium = round(max(min_premium, min(max_premium, self._final_premium)), 2)
        logger.info(f"动态保费: 基础{self.base_premium}→最终{self._final_premium}, 调整因子{self._adjustment_factor}")
        return self._final_premium

    def get_premium_decomposition(self) -> Dict:
        if self._final_premium is None:
            self.get_final_premium()
        import datetime
        current_month = datetime.datetime.now().month
        seasonal_premium = round(self.base_premium * (self._seasonal_factor - 1.0), 4) if self._seasonal_factor else 0.0
        adjusted_base = round(self.base_premium * self._adjustment_factor, 4) if self._adjustment_factor else self.base_premium
        decomposition = {
            'base_premium': self.base_premium,
            'adjustment_factor': self._adjustment_factor,
            'adjusted_base': adjusted_base,
            'risk_loading': self._risk_loading or 0.0,
            'market_adjustment': self._market_adjustment or 0.0,
            'seasonal_factor': self._seasonal_factor or 1.0,
            'seasonal_premium': seasonal_premium,
            'final_premium': self._final_premium,
            'components': {
                '基础保费(调整后)': adjusted_base,
                '风险加载': self._risk_loading or 0.0,
                '市场调整': self._market_adjustment or 0.0,
                '季节调整': seasonal_premium,
            },
            'ratios': {
                '基础占比': round(adjusted_base / self._final_premium * 100, 2) if self._final_premium else 0,
                '风险占比': round((self._risk_loading or 0) / self._final_premium * 100, 2) if self._final_premium else 0,
                '市场占比': round((self._market_adjustment or 0) / self._final_premium * 100, 2) if self._final_premium else 0,
                '季节占比': round(seasonal_premium / self._final_premium * 100, 2) if self._final_premium else 0,
            },
            'current_month': current_month,
            'risk_score': self.risk_score,
            'market_volatility': self.market_volatility,
            'compliance': self.GUIDELINE_SOURCE,
            'regulatory_basis': self.ACTUARIAL_STANDARD,
        }
        return decomposition
