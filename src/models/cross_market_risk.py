import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from utils.helpers import logger_setup
from utils.constants import CROSS_MARKET_CONFIG, SYMBOL_NAMES

logger = logger_setup('cross_market_risk')


class CrossMarketRiskConductor:
    SPILLOVER_SOURCE = 'Diebold-Yilmaz(2012) "Measuring and Forecasting Financial Connectedness", Journal of Econometrics, Vol.171(1), pp.1-17'

    def __init__(self, symbols: List[str], data_loader=None):
        self.symbols = symbols
        self.data_loader = data_loader
        self.forecast_horizon = CROSS_MARKET_CONFIG.get('forecast_horizon', 10)
        self.var_lag = CROSS_MARKET_CONFIG.get('var_lag', 2)
        self.spillover_threshold = CROSS_MARKET_CONFIG.get('spillover_threshold', 0.05)
        self._connectedness_matrix = None
        self._spillover_index = None
        self._var_coeffs = None
        self._returns_df = None

    def _estimate_var(self, returns_df: pd.DataFrame) -> np.ndarray:
        T, N = returns_df.shape
        p = min(self.var_lag, max(1, T // (N + 1) - 1))
        Y = returns_df.values[p:]
        Z_list = []
        for lag in range(1, p + 1):
            Z_list.append(returns_df.values[p - lag: T - lag])
        Z = np.hstack(Z_list)
        Z = np.column_stack([Z, np.ones(len(Y))])
        try:
            B = np.linalg.lstsq(Z, Y, rcond=None)[0]
        except np.linalg.LinAlgError:
            B = np.zeros((Z.shape[1], N))
        self._var_coeffs = B
        return B

    def _compute_mae_representations(self, B: np.ndarray, N: int, H: int) -> List[np.ndarray]:
        p = min(self.var_lag, max(1, B.shape[0] // N - 1))
        Phi_list = [np.eye(N)]
        A_list = []
        for lag in range(p):
            A_list.append(B[lag * N:(lag + 1) * N, :])
        for h in range(1, H):
            Phi_h = np.zeros((N, N))
            for k in range(1, min(h, p) + 1):
                if k - 1 < len(A_list):
                    Phi_h += Phi_list[h - k] @ A_list[k - 1]
            Phi_list.append(Phi_h)
        return Phi_list

    def _var_residual_cov(self, returns_df: pd.DataFrame, B: np.ndarray) -> np.ndarray:
        T, N = returns_df.shape
        p = min(self.var_lag, max(1, T // (N + 1) - 1))
        Y = returns_df.values[p:]
        Z_list = []
        for lag in range(1, p + 1):
            Z_list.append(returns_df.values[p - lag: T - lag])
        Z = np.column_stack([np.hstack(Z_list), np.ones(len(Y))])
        residuals = Y - Z @ B
        Sigma = (residuals.T @ residuals) / (T - p - N * p - 1)
        Sigma = (Sigma + Sigma.T) / 2
        diag = np.diag(np.diag(Sigma))
        off_diag = Sigma - diag
        Sigma_reg = diag + 0.01 * off_diag
        min_eig = np.min(np.linalg.eigvalsh(Sigma_reg))
        if min_eig < 1e-8:
            Sigma_reg += (abs(min_eig) + 1e-6) * np.eye(N)
        return Sigma_reg

    def compute_spillover_index(self, returns_df: pd.DataFrame) -> Dict:
        self._returns_df = returns_df
        N = returns_df.shape[1]
        H = self.forecast_horizon
        B = self._estimate_var(returns_df)
        Phi_list = self._compute_mae_representations(B, N, H)
        Sigma = self._var_residual_cov(returns_df, B)
        try:
            P = np.linalg.cholesky(Sigma)
        except np.linalg.LinAlgError:
            eigvals, eigvecs = np.linalg.eigh(Sigma)
            eigvals = np.maximum(eigvals, 1e-6)
            P = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T
        total_var = np.zeros(N)
        own_var = np.zeros((N, N))
        for h in range(H):
            Theta_h = Phi_list[h] @ P
            for i in range(N):
                total_var[i] += np.sum(Theta_h[i, :] ** 2)
                for j in range(N):
                    own_var[i, j] += Theta_h[i, j] ** 2
        connectedness = np.zeros((N, N))
        for i in range(N):
            for j in range(N):
                if i != j and total_var[i] > 0:
                    connectedness[i, j] = own_var[i, j] / total_var[i]
        self._connectedness_matrix = connectedness
        total_spillover = 0.0
        for i in range(N):
            for j in range(N):
                if i != j:
                    total_spillover += connectedness[i, j]
        total_spillover_pct = total_spillover / N * 100
        self._spillover_index = total_spillover_pct
        directional_to = np.zeros(N)
        directional_from = np.zeros(N)
        for i in range(N):
            directional_to[i] = np.sum(connectedness[i, :]) - connectedness[i, i]
            directional_from[i] = np.sum(connectedness[:, i]) - connectedness[i, i]
        net_spillover = directional_to - directional_from
        symbols = list(returns_df.columns)
        result = {
            'total_spillover_index': round(total_spillover_pct, 4),
            'connectedness_matrix': pd.DataFrame(
                connectedness,
                index=symbols,
                columns=symbols
            ),
            'directional_to': pd.Series(directional_to, index=symbols),
            'directional_from': pd.Series(directional_from, index=symbols),
            'net_spillover': pd.Series(net_spillover, index=symbols),
            'forecast_horizon': H,
            'var_lag': self.var_lag,
            'method': 'Diebold-Yilmaz(2012) VAR方差分解',
            'source': self.SPILLOVER_SOURCE,
        }
        logger.info(f"溢出指数计算完成: 总溢出={total_spillover_pct:.2f}%, H={H}, lag={self.var_lag}")
        return result

    def detect_risk_contagion(self, shock_symbol: str, threshold: float = None) -> Dict:
        if self._connectedness_matrix is None:
            raise ValueError("请先调用compute_spillover_index()计算连通性矩阵")
        if threshold is None:
            threshold = self.spillover_threshold
        symbols = list(self._connectedness_matrix.index)
        if shock_symbol not in symbols:
            raise ValueError(f"品种{shock_symbol}不在连通性矩阵中")
        shock_idx = symbols.index(shock_symbol)
        contagion_paths = []
        direct_effects = {}
        for j, sym in enumerate(symbols):
            if j != shock_idx:
                spillover_val = self._connectedness_matrix.iloc[j, shock_idx]
                direct_effects[sym] = spillover_val
                if spillover_val >= threshold:
                    contagion_paths.append({
                        'from': shock_symbol,
                        'to': sym,
                        'spillover': round(spillover_val, 6),
                        'strength': 'strong' if spillover_val >= threshold * 3 else ('medium' if spillover_val >= threshold * 2 else 'weak')
                    })
        contagion_paths.sort(key=lambda x: x['spillover'], reverse=True)
        second_order_paths = []
        for path in contagion_paths[:5]:
            intermediate = path['to']
            if intermediate in symbols:
                inter_idx = symbols.index(intermediate)
                for j, sym in enumerate(symbols):
                    if j != inter_idx and j != shock_idx:
                        so_val = self._connectedness_matrix.iloc[j, inter_idx]
                        if so_val >= threshold:
                            second_order_paths.append({
                                'from': intermediate,
                                'to': sym,
                                'via': shock_symbol,
                                'spillover': round(so_val, 6),
                                'total_path_strength': round(path['spillover'] * so_val, 6)
                            })
        second_order_paths.sort(key=lambda x: x['total_path_strength'], reverse=True)
        result = {
            'shock_symbol': shock_symbol,
            'shock_name': SYMBOL_NAMES.get(shock_symbol, shock_symbol),
            'threshold': threshold,
            'direct_contagion_count': len(contagion_paths),
            'contagion_paths': contagion_paths,
            'second_order_paths': second_order_paths[:10],
            'direct_effects': direct_effects,
            'max_contagion': contagion_paths[0] if contagion_paths else None,
            'method': '基于Diebold-Yilmaz溢出指数的风险传染路径检测',
        }
        logger.info(f"风险传染检测: {shock_symbol}直接传染{len(contagion_paths)}个品种")
        return result

    def build_connectedness_matrix(self, forecast_horizon: int = None) -> pd.DataFrame:
        if forecast_horizon is not None and forecast_horizon != self.forecast_horizon:
            self.forecast_horizon = forecast_horizon
            if self._returns_df is not None:
                self.compute_spillover_index(self._returns_df)
        if self._connectedness_matrix is None:
            raise ValueError("请先调用compute_spillover_index()计算连通性矩阵")
        return self._connectedness_matrix

    def get_top_risk_transmitters(self, n: int = 5) -> pd.DataFrame:
        if self._connectedness_matrix is None:
            raise ValueError("请先调用compute_spillover_index()计算连通性矩阵")
        symbols = list(self._connectedness_matrix.index)
        transmit_scores = {}
        for i, sym in enumerate(symbols):
            transmit_scores[sym] = np.sum(self._connectedness_matrix.iloc[:, i]) - self._connectedness_matrix.iloc[i, i]
        sorted_transmitters = sorted(transmit_scores.items(), key=lambda x: x[1], reverse=True)[:n]
        rows = []
        for rank, (sym, score) in enumerate(sorted_transmitters, 1):
            rows.append({
                'rank': rank,
                'symbol': sym,
                'name': SYMBOL_NAMES.get(sym, sym),
                'transmit_score': round(score, 6),
                'role': '主要风险传播者'
            })
        return pd.DataFrame(rows)

    def get_top_risk_receivers(self, n: int = 5) -> pd.DataFrame:
        if self._connectedness_matrix is None:
            raise ValueError("请先调用compute_spillover_index()计算连通性矩阵")
        symbols = list(self._connectedness_matrix.index)
        receive_scores = {}
        for i, sym in enumerate(symbols):
            receive_scores[sym] = np.sum(self._connectedness_matrix.iloc[i, :]) - self._connectedness_matrix.iloc[i, i]
        sorted_receivers = sorted(receive_scores.items(), key=lambda x: x[1], reverse=True)[:n]
        rows = []
        for rank, (sym, score) in enumerate(sorted_receivers, 1):
            rows.append({
                'rank': rank,
                'symbol': sym,
                'name': SYMBOL_NAMES.get(sym, sym),
                'receive_score': round(score, 6),
                'role': '主要风险接收者'
            })
        return pd.DataFrame(rows)
