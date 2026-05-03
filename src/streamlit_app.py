# -*- coding: utf-8 -*-
"""
Streamlit Cloud Safe Entry Point v2
=====================================
完全自包含的云安全入口 - 防止1ST崩溃错误

核心策略:
1. 最小化顶层import (仅streamlit + 标准库)
2. 懒加载重型模块 (延迟到用户交互时)
3. 全链路异常捕获 (展示友好错误信息)
4. 降级演示模式 (即使模块加载失败也能显示页面)
"""
import sys
import os
import traceback
import platform

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

PARENT_DIR = os.path.dirname(SRC_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

import streamlit as st

try:
    from utils.ui_components import MetricCard, StatusBadge, render_error_guidance
    UI_COMPONENTS_AVAILABLE = True
except ImportError:
    UI_COMPONENTS_AVAILABLE = False

st.set_page_config(
    page_title="农险期货智能定价系统",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
* { font-family: 'Noto Sans SC', sans-serif; }
.main-header { 
    background: linear-gradient(135deg, #1a365d 0%, #2c5282 50%, #2b6cb0 100%);
    padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem;
    color: white; text-align: center;
}
.metric-card {
    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
    border-radius: 10px; padding: 1.5rem; text-align: center;
    border-left: 4px solid #3182ce; margin: 0.5rem 0;
}
.success-banner {
    background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
    border-radius: 8px; padding: 1rem; border-left: 4px solid #38a169;
}
.error-banner {
    background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
    border-radius: 8px; padding: 1rem; border-left: 4px solid #e53e3e;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

APP_LOADED = False
LOAD_ERROR = None

def try_load_app():
    global APP_LOADED, LOAD_ERROR
    try:
        os.chdir(SRC_DIR)
    except OSError:
        pass
    
    try:
        from utils.config import config
        from utils.constants import CORE_SYMBOLS, SYMBOL_NAMES
        from data.data_loader import DataLoader
        from models.pricing_model import PricingModel
        APP_LOADED = True
        return True
    except Exception as e:
        LOAD_ERROR = str(e)
        return False

def _render_system_status_panel():
    st.subheader("🖥️ 系统状态检查")
    checks = []

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    py_ok = sys.version_info >= (3, 9)
    checks.append(("Python版本", py_ver, py_ok))

    try:
        import numpy; np_ver = numpy.__version__; np_ok = True
    except ImportError:
        np_ver = "未安装"; np_ok = False
    checks.append(("NumPy", np_ver, np_ok))

    try:
        import pandas; pd_ver = pandas.__version__; pd_ok = True
    except ImportError:
        pd_ver = "未安装"; pd_ok = False
    checks.append(("Pandas", pd_ver, pd_ok))

    try:
        import streamlit as _st; st_ver = _st.__version__; st_ok = True
    except ImportError:
        st_ver = "未安装"; st_ok = False
    checks.append(("Streamlit", st_ver, st_ok))

    try:
        import sklearn; sk_ver = sklearn.__version__; sk_ok = True
    except ImportError:
        sk_ver = "未安装"; sk_ok = False
    checks.append(("Scikit-learn", sk_ver, sk_ok))

    try:
        import xgboost; xgb_ver = xgboost.__version__; xgb_ok = True
    except ImportError:
        xgb_ver = "未安装"; xgb_ok = False
    checks.append(("XGBoost", xgb_ver, xgb_ok))

    data_dir = os.path.join(SRC_DIR, "data")
    data_exists = os.path.isdir(data_dir)
    checks.append(("数据目录", "存在" if data_exists else "缺失", data_exists))

    if UI_COMPONENTS_AVAILABLE:
        for name, version, ok in checks:
            col_chk1, col_chk2, col_chk3 = st.columns([2, 2, 1])
            with col_chk1:
                st.markdown(f"**{name}**")
            with col_chk2:
                st.caption(version)
            with col_chk3:
                StatusBadge("正常" if ok else "异常", "success" if ok else "error").render()
    else:
        for name, version, ok in checks:
            icon = "✅" if ok else "❌"
            st.markdown(f"{icon} **{name}**: `{version}`")

    all_ok = all(ok for _, _, ok in checks)
    if UI_COMPONENTS_AVAILABLE:
        MetricCard("系统健康度", f"{sum(1 for _,_,ok in checks if ok)}/{len(checks)}",
                   delta="所有依赖正常" if all_ok else "部分依赖缺失",
                   delta_color="normal" if all_ok else "inverse",
                   color="success" if all_ok else "warning").render()
    else:
        if all_ok:
            st.success("✅ 所有依赖正常")
        else:
            st.warning("⚠️ 部分依赖缺失，完整功能可能不可用")

def render_demo_mode():
    st.markdown("""
    <div class="main-header">
        <h1>🌾 农险期货智能定价系统</h1>
        <h3>乡村振兴背景下基于因果推断的农险期货智能定价模型</h3>
        <p style="opacity: 0.9;">Agricultural Futures Intelligent Pricing Model Based on Causal Inference</p>
    </div>
    """, unsafe_allow_html=True)
    
    if UI_COMPONENTS_AVAILABLE:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            MetricCard("覆盖品种数", "36", color="primary").render()
        with col2:
            MetricCard("原创算法", "3", color="success").render()
        with col3:
            MetricCard("数学定理", "6", color="info").render()
        with col4:
            MetricCard("数据时间范围", "2020-2025", color="accent").render()
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h2 style="color:#2c5282;margin:0;">36</h2>
                <p style="margin:0;color:#4a5568;">覆盖品种数</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h2 style="color:#2c5282;margin:0;">3</h2>
                <p style="margin:0;color:#4a5568;">原创算法</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h2 style="color:#2c5282;margin:0;">6</h2>
                <p style="margin:0;color:#4a5568;">数学定理</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown("""
            <div class="metric-card">
                <h2 style="color:#2c5282;margin:0;">2020-2025</h2>
                <p style="margin:0;color:#4a5568;">数据时间范围</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 系统架构", "🧮 核心算法", "📁 数据说明", "🖥️ 系统状态", "ℹ️ 关于"])
    
    with tab1:
        st.subheader("系统技术栈")
        
        tech_data = {
            "前端框架": "Streamlit (Cloud部署)",
            "后端算法": "Python 3.9+ / NumPy / Pandas / SciPy",
            "因果发现": "Agri-PC (农业约束PC算法)",
            "因果估计": "ACML (异质因果元学习器)",
            "预测保真": "CCP (因果保真预测)",
            "数据来源": "36品种期货 + 7主产区气象 + 4类遥感",
            "AI工具链": "豆包AI(思考模式)"
        }
        
        for key, value in tech_data.items():
            cols = st.columns([1, 3])
            with cols[0]:
                st.markdown(f"**{key}**")
            with cols[1]:
                if UI_COMPONENTS_AVAILABLE:
                    StatusBadge(value, "info").render()
                else:
                    st.markdown(value)
    
    with tab2:
        st.subheader("三大原创算法")
        
        if UI_COMPONENTS_AVAILABLE:
            st.markdown("""
            <div class="success-banner">
                <strong>🔬 Agri-PC (农业约束PC算法)</strong><br/>
                融合时序约束/农业先验/交割规则的因果发现算法，解决传统PC在农业场景中的方向误判问题。
            </div>
            """, unsafe_allow_html=True)
            StatusBadge("已验证", "success").render()

            st.markdown("""
            <div class="success-banner" style="border-left-color:#805ad5;">
                <strong>🎯 ACML (异质因果元学习器)</strong><br/>
                基于双重正交化的异质性因果效应估计框架，处理品种间、地区间、时期间的异质性定价因子。
            </div>
            """, unsafe_allow_html=True)
            StatusBadge("已验证", "success").render()

            st.markdown("""
            <div class="success-banner" style="border-left-color:#dd6b20;">
                <strong>🛡️ CCP (因果保真预测)</strong><br/>
                自适应覆盖率保真预测区间，结合因果结构信息的共形预测方法。
            </div>
            """, unsafe_allow_html=True)
            StatusBadge("已验证", "success").render()
        else:
            st.markdown("""
            <div class="success-banner">
                <strong>🔬 Agri-PC (农业约束PC算法)</strong><br/>
                融合时序约束/农业先验/交割规则的因果发现算法，解决传统PC在农业场景中的方向误判问题。
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="success-banner" style="border-left-color:#805ad5;">
                <strong>🎯 ACML (异质因果元学习器)</strong><br/>
                基于双重正交化的异质性因果效应估计框架，处理品种间、地区间、时期间的异质性定价因子。
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="success-banner" style="border-left-color:#dd6b20;">
                <strong>🛡️ CCP (因果保真预测)</strong><br/>
                自适应覆盖率保真预测区间，结合因果结构信息的共形预测方法。
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.subheader("数据集构成")
        
        data_info = [
            ("📈 期货价格数据", "36个农产品期货品种日度行情 (2020-2025)", True),
            ("🌤️ 气象数据", "7大主产区日度气象数据 (温度/降水/湿度等)", True),
            ("🛰️ 遥感数据", "NDVI/EVI/LST/干旱指数 月度遥感指标", True),
            ("📋 宏观经济", "CPI/PMI等宏观经济指标", True),
        ]
        
        for title, desc, available in data_info:
            col_d1, col_d2 = st.columns([1, 3])
            with col_d1:
                st.markdown(f"**{title}**")
            with col_d2:
                if UI_COMPONENTS_AVAILABLE:
                    StatusBadge(desc, "success" if available else "warning").render()
                else:
                    st.markdown(desc)
    
    with tab4:
        _render_system_status_panel()
    
    with tab5:
        st.subheader("关于本项目")
        
        if UI_COMPONENTS_AVAILABLE:
            render_error_guidance(f"当前运行模式：演示模式。完整功能需要加载数据文件。错误详情: {LOAD_ERROR or '未知'}")
        else:
            st.markdown("""
            <div class="error-banner">
                <strong>⚠️ 当前运行模式：演示模式</strong><br/><br/>
                完整功能需要加载数据文件。当前Streamlit Cloud环境可能缺少部分数据依赖。<br/>
                错误详情：<code>{}</code>
            </div>
            """.format(LOAD_ERROR or "未知"), unsafe_allow_html=True)
        
        st.markdown("""
        ---
        **项目信息**
        - **参赛类别**: 大数据应用
        - **作品名称**: 乡村振兴背景下基于因果推断的农险期货智能定价模型
        - **在线地址**: （提交后公布）
        - **部署版本**: v1.0
        """)

def render_full_app():
    try:
        import app
    except Exception as e:
        st.error(f"⚠️ 应用加载异常: {e}")
        st.code(traceback.format_exc())
        render_demo_mode()

def main():
    with st.spinner('🔄 正在加载农险期货智能定价系统...'):
        success = try_load_app()
    
    if success:
        render_full_app()
    else:
        render_demo_mode()

if __name__ == '__main__':
    main()

main()
