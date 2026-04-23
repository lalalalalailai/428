import pandas as pd
import numpy as np
from typing import Dict, Optional

try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
except ImportError:
    go = None

from utils.helpers import logger_setup

logger = logger_setup('plot_performance')

def _make_layout(title: str, height: int = 400, margin_b: int = 100,
                 xaxis_title: str = '', yaxis_title: str = '',
                 showlegend: bool = False) -> dict:
    layout_dict = {
        'title': dict(text=title, font=dict(size=16, color='#475569', family='Microsoft YaHei')),
        'template': 'plotly_white',
        'paper_bgcolor': '#f8fafc',
        'plot_bgcolor': '#ffffff',
        'height': height,
        'margin': dict(l=60, r=40, t=60, b=margin_b),
        'xaxis': dict(gridcolor='#e2e8f0', tickfont=dict(color='#94a3b8', size=10)),
        'yaxis': dict(gridcolor='#e2e8f0', tickfont=dict(color='#94a3b8'))
    }
    if xaxis_title:
        layout_dict['xaxis']['title'] = xaxis_title
    if yaxis_title:
        layout_dict['yaxis']['title'] = yaxis_title
    if showlegend:
        layout_dict['legend'] = dict(font=dict(color='#475569'), orientation='h',
                                      yanchor='bottom', y=1.02, xanchor='right', x=1)
    return layout_dict

def plot_model_performance(metrics: Dict[str, float],
                             title: str = "模型性能指标") -> 'go.Figure':
    if go is None:
        return _placeholder_fig("需要安装plotly")
    display_names = {
        'mae': 'MAE (平均绝对误差)',
        'rmse': 'RMSE (均方根误差)',
        'mape': 'MAPE (%)',
        'r2': 'R² (决定系数)',
        'error_le_5_pct': '误差≤5%占比',
        'error_le_10_pct': '误差≤10%占比',
        'error_le_20_pct': '误差≤20%占比'
    }
    keys = ['mape', 'r2', 'mae', 'rmse', 'error_le_5_pct', 'error_le_10_pct']
    values = [metrics.get(k, 0) for k in keys]
    labels = [display_names.get(k, k) for k in keys]
    colors = ['#4caf50' if k == 'mape' else '#d97706' if k == 'r2' else '#1a237e' for k in keys]
    fig = go.Figure(data=[go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f'{v:.4f}' if k != 'mape' else f'{v:.2f}%' for k, v in zip(keys, values)],
        textposition='outside',
        textfont=dict(color='#475569', size=11)
    )])
    fig.update_layout(**_make_layout(title, height=400, margin_b=100))
    fig.update_xaxes(tickangle=-30)
    return fig


def plot_prediction_comparison(dates, actual, predicted,
                                  confidence_interval=None,
                                  title: str = "价格预测对比") -> 'go.Figure':
    if go is None:
        return _placeholder_fig("需要安装plotly")
    actual = np.array(actual).flatten()
    predicted = np.array(predicted).flatten()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=actual,
        name='实际价格', line=dict(color='#4caf50', width=2),
        mode='lines'
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=predicted,
        name='预测价格', line=dict(color='#d97706', width=2, dash='dash'),
        mode='lines'
    ))
    if confidence_interval is not None:
        ci_lower, ci_upper = confidence_interval
        fig.add_trace(go.Scatter(
            x=list(dates) + list(reversed(dates)),
            y=list(ci_upper) + list(reversed(ci_lower)),
            fill='toself', fillcolor='rgba(255,215,0,0.15)',
            line=dict(color='rgba(255,215,0,0)'),
            name='95%置信区间',
            showlegend=True
        ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color='#475569', family='Microsoft YaHei')),
        template='plotly_white',
        paper_bgcolor='#f8fafc',
        plot_bgcolor='#f8fafc',
        legend=dict(font=dict(color='#475569'), orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(title='日期', gridcolor='#e2e8f0', tickfont=dict(color='#94a3b8')),
        yaxis=dict(title='价格', gridcolor='#e2e8f0', tickfont=dict(color='#94a3b8')),
        height=450,
        margin=dict(l=60, r=40, t=60, b=60),
        hovermode='x unified'
    )
    return fig


def plot_feature_importance(feature_importance: pd.Series,
                               top_n: int = 15,
                               title: str = "特征重要性 Top 15") -> 'go.Figure':
    if go is None or feature_importance.empty:
        return _placeholder_fig("无数据或缺少plotly")
    fi_top = feature_importance.head(top_n).sort_values(ascending=True)
    colors = ['#d97706' if i >= len(fi_top)-3 else '#1a237e' for i in range(len(fi_top))]
    fig = go.Figure(data=[go.Bar(
        x=fi_top.values,
        y=fi_top.index,
        orientation='h',
        marker_color=colors[::-1],
        text=[f'{v:.4f}' for v in fi_top.values],
        textposition='outside',
        textfont=dict(color='#475569', size=10)
    )])
    fig.update_layout(**_make_layout(title, height=max(350, top_n * 25), margin_b=40))
    return fig


def plot_error_distribution(errors, title: str = "预测误差分布") -> 'go.Figure':
    if go is None:
        return _placeholder_fig("需要安装plotly")
    errors = np.array(errors).flatten()
    fig = go.Figure(data=[
        go.Histogram(x=errors, nbinsx=50, marker_color='#2563eb',
                     opacity=0.75, name='误差分布')
    ])
    fig.update_layout(**_make_layout(title, height=350, margin_b=60,
                                     xaxis_title='误差百分比 (%)', yaxis_title='频次'))
    return fig


def _placeholder_fig(msg):
    if go is None:
        class D:
            def show(self): print(msg)
        return D()
    fig = go.Figure()
    fig.update_layout(title=msg, template='plotly_white')
    return fig
