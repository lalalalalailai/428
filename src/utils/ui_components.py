# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time


class MetricCard:
    def __init__(self, title, value, delta=None, delta_color="normal", color="primary"):
        self.title = title
        self.value = value
        self.delta = delta
        self.delta_color = delta_color
        self.color = color

    _COLOR_MAP = {
        "primary": ("#1B6B48", "#E8F5EE"),
        "success": ("#1E8A5A", "#EDFAF3"),
        "warning": ("#D4790C", "#FEF9EC"),
        "danger": ("#C7302D", "#FDF0EF"),
        "info": ("#2A7AB8", "#EBF4FC"),
        "accent": ("#C4880C", "#FBF5E6"),
    }

    def render(self):
        border_color, bg_color = self._COLOR_MAP.get(self.color, self._COLOR_MAP["primary"])
        delta_html = ""
        if self.delta is not None:
            dc = self.delta_color
            if dc == "normal":
                delta_style = "color:#1E8A5A;"
            elif dc == "inverse":
                delta_style = "color:#C7302D;"
            else:
                delta_style = "color:#6B7A68;"
            delta_html = f'<div style="font-size:12px;margin-top:4px;{delta_style}">{self.delta}</div>'
        html = f"""
        <div style="
            background:{bg_color};
            border-left:4px solid {border_color};
            border-radius:10px;
            padding:16px 20px;
            margin:4px 0;
            box-shadow:0 1px 3px rgba(26,31,22,0.04);
            transition:box-shadow 0.2s;
        ">
            <div style="font-size:12px;color:#6B7A68;font-weight:500;margin-bottom:6px;">{self.title}</div>
            <div style="font-size:26px;font-weight:700;color:#1A1F16;letter-spacing:-0.5px;">{self.value}</div>
            {delta_html}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)


class StatusBadge:
    _STYLES = {
        "success": ("#1E8A5A", "#EDFAF3", "✅"),
        "warning": ("#D4790C", "#FEF9EC", "⚠️"),
        "error": ("#C7302D", "#FDF0EF", "❌"),
        "info": ("#2A7AB8", "#EBF4FC", "ℹ️"),
    }

    def __init__(self, text, status="info"):
        self.text = text
        self.status = status

    def render(self):
        fg, bg, icon = self._STYLES.get(self.status, self._STYLES["info"])
        html = f"""
        <span style="
            display:inline-block;
            background:{bg};
            color:{fg};
            border:1px solid {fg}22;
            border-radius:20px;
            padding:4px 14px;
            font-size:13px;
            font-weight:600;
            margin:2px 4px;
            line-height:1.6;
        ">{icon} {self.text}</span>
        """
        st.markdown(html, unsafe_allow_html=True)

    @classmethod
    def render_inline(cls, text, status="info"):
        fg, bg, icon = cls._STYLES.get(status, cls._STYLES["info"])
        return f'<span style="display:inline-block;background:{bg};color:{fg};border:1px solid {fg}22;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:600;margin:2px 4px;line-height:1.6;">{icon} {text}</span>'


class ProgressTracker:
    def __init__(self, steps, current=0):
        self.steps = steps
        self.current = current

    def render(self):
        html_parts = ['<div style="display:flex;align-items:center;gap:0;margin:16px 0;flex-wrap:wrap;">']
        for i, step in enumerate(self.steps):
            if i < self.current:
                bg = "#1B6B48"
                fg = "#FFFFFF"
                border = "#1B6B48"
                icon = "✓"
            elif i == self.current:
                bg = "#E8F5EE"
                fg = "#1B6B48"
                border = "#1B6B48"
                icon = str(i + 1)
            else:
                bg = "#F2F4EF"
                fg = "#94A192"
                border = "#D0D9CE"
                icon = str(i + 1)
            html_parts.append(f"""
            <div style="
                display:flex;align-items:center;gap:6px;
                background:{bg};color:{fg};
                border:2px solid {border};
                border-radius:8px;
                padding:6px 14px;
                font-size:13px;font-weight:600;
                white-space:nowrap;
            ">
                <span style="width:20px;height:20px;border-radius:50%;
                    background:{'rgba(255,255,255,0.25)' if i < self.current else 'transparent'};
                    display:flex;align-items:center;justify-content:center;
                    font-size:11px;font-weight:700;">{icon}</span>
                {step}
            </div>""")
            if i < len(self.steps) - 1:
                line_color = "#1B6B48" if i < self.current else "#D0D9CE"
                html_parts.append(f'<div style="width:24px;height:2px;background:{line_color};flex-shrink:0;"></div>')
        html_parts.append('</div>')
        st.markdown(''.join(html_parts), unsafe_allow_html=True)

    def update(self, current):
        self.current = current
        self.render()


class DataPreviewTable:
    def __init__(self, df, page_size=100, key="data_preview"):
        self.df = df.reset_index(drop=True) if not isinstance(df.index, pd.RangeIndex) else df.copy()
        self.page_size = page_size
        self.key = key

    def render(self):
        if self.df.empty:
            st.info("📭 暂无数据")
            return
        col_search, col_page_size = st.columns([3, 1])
        with col_search:
            search_term = st.text_input("🔍 搜索", placeholder="输入关键词过滤...", key=f"{self.key}_search")
        with col_page_size:
            ps_options = [50, 100, 200, 500]
            selected_ps = st.selectbox("每页条数", ps_options, index=ps_options.index(self.page_size) if self.page_size in ps_options else 1, key=f"{self.key}_ps")
            self.page_size = selected_ps

        filtered_df = self.df
        if search_term:
            mask = self.df.astype(str).apply(lambda row: search_term.lower() in row.str.lower().sum(), axis=1)
            try:
                mask = self.df.apply(lambda row: any(search_term.lower() in str(v).lower() for v in row), axis=1)
            except Exception:
                mask = pd.Series([True] * len(self.df))
            filtered_df = self.df[mask]

        total_rows = len(filtered_df)
        total_pages = max(1, (total_rows + self.page_size - 1) // self.page_size)

        col_pg, col_info, col_sort = st.columns([1, 2, 1])
        with col_pg:
            page = st.number_input("页码", min_value=1, max_value=total_pages, value=1, key=f"{self.key}_page")
        with col_info:
            st.caption(f"共 {total_rows:,} 条记录，每页 {self.page_size} 条，共 {total_pages} 页")
        with col_sort:
            numeric_cols = filtered_df.select_dtypes(include=[np.number]).columns.tolist()
            sort_options = ["默认"] + list(filtered_df.columns)
            sort_col = st.selectbox("排序列", sort_options, key=f"{self.key}_sort_col")
            if sort_col != "默认" and sort_col in filtered_df.columns:
                sort_order = st.selectbox("排序", ["升序", "降序"], key=f"{self.key}_sort_order")
                ascending = sort_order == "升序"
                filtered_df = filtered_df.sort_values(by=sort_col, ascending=ascending)

        start_idx = (page - 1) * self.page_size
        end_idx = min(start_idx + self.page_size, total_rows)
        st.dataframe(filtered_df.iloc[start_idx:end_idx], use_container_width=True, height=350)


class ChartContainer:
    def __init__(self, title, chart_fig=None, caption=None, download_prefix="chart"):
        self.title = title
        self.chart_fig = chart_fig
        self.caption = caption
        self.download_prefix = download_prefix

    def render(self):
        st.markdown(f"""
        <div style="
            background:#FFFFFF;
            border:1px solid #E0E5DD;
            border-radius:12px;
            padding:20px;
            margin:8px 0;
            box-shadow:0 2px 6px rgba(26,31,22,0.04);
        ">
            <div style="font-size:16px;font-weight:700;color:#1A1F16;margin-bottom:8px;">{self.title}</div>
            {f'<div style="font-size:12px;color:#6B7A68;margin-bottom:12px;">{self.caption}</div>' if self.caption else ''}
        </div>
        """, unsafe_allow_html=True)
        if self.chart_fig is not None:
            st.plotly_chart(self.chart_fig, use_container_width=True)
            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                try:
                    img_bytes = self.chart_fig.to_image(format="png", width=1200, height=600, scale=2)
                    st.download_button(
                        "📥 下载PNG", img_bytes,
                        file_name=f"{self.download_prefix}.png", mime="image/png",
                        key=f"dl_png_{self.download_prefix}"
                    )
                except Exception:
                    pass
            with col_dl2:
                try:
                    html_str = self.chart_fig.to_html(include_plotlyjs='cdn', full_html=False)
                    st.download_button(
                        "📥 下载HTML", html_str.encode('utf-8'),
                        file_name=f"{self.download_prefix}.html", mime="text/html",
                        key=f"dl_html_{self.download_prefix}"
                    )
                except Exception:
                    pass


def render_quick_analysis(symbol, data):
    if data is None or (isinstance(data, pd.DataFrame) and data.empty):
        st.warning("⚠️ 无可用数据，请先加载数据")
        return None

    results = {}

    with st.expander("🚀 一键智能分析", expanded=False):
        st.markdown(f"**品种**: `{symbol}` | **数据量**: {len(data):,} 条记录")

        progress = st.progress(0, text="正在执行快速分析...")

        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        results['numeric_cols'] = numeric_cols
        results['n_rows'] = len(data)
        results['n_cols'] = len(data.columns)
        progress.progress(20, text="基础统计...")

        if len(numeric_cols) > 0:
            desc = data[numeric_cols].describe().T
            results['describe'] = desc
            results['missing_pct'] = (data[numeric_cols].isnull().sum() / len(data) * 100).to_dict()

        progress.progress(50, text="趋势分析...")

        if len(numeric_cols) > 0:
            first_col = numeric_cols[0]
            if len(data) >= 30:
                ma7 = data[first_col].rolling(7).mean()
                ma30 = data[first_col].rolling(30).mean()
                latest = data[first_col].iloc[-1]
                ma7_latest = ma7.iloc[-1]
                ma30_latest = ma30.iloc[-1]
                trend_7 = "📈 上升" if latest > ma7_latest else "📉 下降"
                trend_30 = "📈 上升" if latest > ma30_latest else "📉 下降"
                results['trend'] = {'ma7_trend': trend_7, 'ma30_trend': trend_30, 'latest': latest}

        progress.progress(75, text="异常检测...")

        if len(numeric_cols) > 0:
            anomalies = {}
            for col in numeric_cols[:5]:
                series = data[col].dropna()
                if len(series) > 10:
                    q1, q3 = series.quantile(0.25), series.quantile(0.75)
                    iqr = q3 - q1
                    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                    n_outliers = ((series < lower) | (series > upper)).sum()
                    anomalies[col] = {'n_outliers': int(n_outliers), 'pct': round(n_outliers / len(series) * 100, 2)}
            results['anomalies'] = anomalies

        progress.progress(100, text="分析完成！")

        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        with col_r1:
            MetricCard("总记录数", f"{results['n_rows']:,}", color="primary").render()
        with col_r2:
            MetricCard("特征数", f"{results['n_cols']}", color="info").render()
        with col_r3:
            missing_avg = np.mean(list(results.get('missing_pct', {0: 0}).values()))
            MetricCard("平均缺失率", f"{missing_avg:.2f}%",
                       delta="良好" if missing_avg < 5 else "需关注",
                       delta_color="normal" if missing_avg < 5 else "inverse",
                       color="success" if missing_avg < 5 else "warning").render()
        with col_r4:
            if 'trend' in results:
                MetricCard("短期趋势", results['trend']['ma7_trend'], color="info").render()
            else:
                MetricCard("短期趋势", "N/A", color="info").render()

        if results.get('anomalies'):
            st.markdown("**🔍 异常值检测**")
            anom_rows = []
            for col, info in results['anomalies'].items():
                anom_rows.append({'特征': col, '异常数量': info['n_outliers'], '异常占比(%)': info['pct']})
            st.dataframe(pd.DataFrame(anom_rows), use_container_width=True, hide_index=True)

    return results


_ERROR_SOLUTIONS = {
    "未找到": {
        "icon": "📁",
        "suggestion": "请检查数据目录是否存在对应文件，确认文件命名格式正确",
        "actions": ["检查 data/ 目录下的文件", "确认品种代码是否正确", "查看 README 中的数据格式要求"]
    },
    "加载失败": {
        "icon": "🔄",
        "suggestion": "数据加载可能因格式不匹配或文件损坏而失败",
        "actions": ["确认文件编码为 UTF-8", "检查 CSV 文件是否完整", "尝试重新下载数据"]
    },
    "内存": {
        "icon": "💾",
        "suggestion": "系统内存不足，建议减少数据量或优化计算",
        "actions": ["缩小时间范围", "减少特征数量", "重启应用释放内存"]
    },
    "超时": {
        "icon": "⏱️",
        "suggestion": "操作耗时过长，可能是数据量过大或计算复杂度高",
        "actions": ["缩小分析范围", "减少交叉验证折数", "降低模型复杂度"]
    },
    "训练": {
        "icon": "🎯",
        "suggestion": "模型训练失败，可能是数据或参数问题",
        "actions": ["检查数据是否包含 NaN 值", "调整模型参数", "确认训练数据量充足"]
    },
    "连接": {
        "icon": "🌐",
        "suggestion": "网络连接问题，部分功能可能需要在线资源",
        "actions": ["检查网络连接", "使用离线模式", "稍后重试"]
    },
}


def render_error_guidance(error_msg):
    matched_key = None
    for key in _ERROR_SOLUTIONS:
        if key in error_msg:
            matched_key = key
            break

    if matched_key:
        info = _ERROR_SOLUTIONS[matched_key]
    else:
        info = {"icon": "🔧", "suggestion": "遇到了一个未预期的错误，请尝试以下通用解决方案", "actions": ["刷新页面重试", "检查输入参数", "查看系统日志"]}

    html = f"""
    <div style="
        background:#FDF0EF;
        border:1px solid #C7302D33;
        border-left:4px solid #C7302D;
        border-radius:10px;
        padding:16px 20px;
        margin:8px 0;
    ">
        <div style="font-size:15px;font-weight:700;color:#C7302D;margin-bottom:8px;">{info['icon']} 操作遇到问题</div>
        <div style="font-size:13px;color:#3D4A3A;margin-bottom:8px;">{info['suggestion']}</div>
        <div style="font-size:12px;color:#6B7A68;margin-bottom:4px;">💡 建议操作：</div>
        <ul style="margin:0;padding-left:20px;font-size:13px;color:#3D4A3A;">
            {''.join(f'<li style="margin-bottom:2px;">{a}</li>' for a in info['actions'])}
        </ul>
        <div style="font-size:11px;color:#94A192;margin-top:10px;border-top:1px solid #E0E5DD;padding-top:8px;">
            错误详情: <code style="background:#FDF0EF;padding:2px 6px;border-radius:4px;font-size:11px;">{error_msg[:120]}</code>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_loading_placeholder(operation="加载中"):
    html = f"""
    <div style="
        background:#F2F4EF;
        border:1px solid #E0E5DD;
        border-radius:12px;
        padding:24px;
        margin:8px 0;
        text-align:center;
    ">
        <div style="
            height:16px;width:60%;margin:0 auto 12px;
            background:linear-gradient(90deg,#E0E5DD 25%,#D0D9CE 50%,#E0E5DD 75%);
            background-size:200% 100%;
            border-radius:4px;
            animation:finShimmer 1.5s infinite;
        "></div>
        <div style="
            height:12px;width:40%;margin:0 auto 8px;
            background:linear-gradient(90deg,#E0E5DD 25%,#D0D9CE 50%,#E0E5DD 75%);
            background-size:200% 100%;
            border-radius:4px;
            animation:finShimmer 1.5s infinite 0.2s;
        "></div>
        <div style="
            height:12px;width:80%;margin:0 auto;
            background:linear-gradient(90deg,#E0E5DD 25%,#D0D9CE 50%,#E0E5DD 75%);
            background-size:200% 100%;
            border-radius:4px;
            animation:finShimmer 1.5s infinite 0.4s;
        "></div>
        <div style="margin-top:16px;font-size:13px;color:#6B7A68;">⏳ {operation}...</div>
    </div>
    <style>
    @keyframes finShimmer {{
        from {{ background-position: -120% 0; }}
        to {{ background-position: 120% 0; }}
    }}
    </style>
    """
    st.markdown(html, unsafe_allow_html=True)
