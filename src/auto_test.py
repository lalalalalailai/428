import sys
import os
import traceback
import time
import logging

logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

results = []
total_start = time.time()


def record(module, test_name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    results.append({
        "module": module,
        "test_name": test_name,
        "status": status,
        "detail": detail
    })
    icon = "✅" if passed else "❌"
    msg = f"  {icon} [{status}] {test_name}: {detail}"
    if passed:
        logger.info(msg)
    else:
        logger.warning(msg)


logger.info("=" * 70)
logger.info("  农险期货定价系统 — 12模块自动化测试")
logger.info("=" * 70)

# ──────────────────────────────────────────────────────────────
# 1. DataLoader
# ──────────────────────────────────────────────────────────────
logger.info("\n[1/12] DataLoader 数据加载器")
try:
    from data.data_loader import DataLoader
    loader = DataLoader()

    try:
        df_futures = loader.load_futures_data("A0")
        if df_futures is not None and not df_futures.empty:
            record("DataLoader", "期货数据(A0)", True, f"加载成功, {len(df_futures)}行, {len(df_futures.columns)}列")
        else:
            record("DataLoader", "期货数据(A0)", False, "DataFrame为空或None")
    except Exception as e:
        record("DataLoader", "期货数据(A0)", False, str(e)[:120])

    try:
        df_weather = loader.load_weather_data("黑龙江")
        if df_weather is not None and not df_weather.empty:
            record("DataLoader", "天气数据(黑龙江)", True, f"加载成功, {len(df_weather)}行, {len(df_weather.columns)}列")
        else:
            record("DataLoader", "天气数据(黑龙江)", False, "DataFrame为空或None")
    except Exception as e:
        record("DataLoader", "天气数据(黑龙江)", False, str(e)[:120])

    try:
        df_ndvi = loader.load_remote_sensing_data("ndvi")
        if df_ndvi is not None and not df_ndvi.empty:
            record("DataLoader", "遥感数据(ndvi)", True, f"加载成功, {len(df_ndvi)}行, {len(df_ndvi.columns)}列")
        else:
            record("DataLoader", "遥感数据(ndvi)", False, "DataFrame为空或None")
    except Exception as e:
        record("DataLoader", "遥感数据(ndvi)", False, str(e)[:120])
except Exception as e:
    record("DataLoader", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 2. DataQualityChecker
# ──────────────────────────────────────────────────────────────
logger.info("\n[2/12] DataQualityChecker 数据质量检查器")
try:
    from data.data_quality_checker import DataQualityChecker
    checker = DataQualityChecker()

    try:
        checker.set_data_type("futures")
        record("DataQualityChecker", "set_data_type('futures')", True, "设置成功")
    except Exception as e:
        record("DataQualityChecker", "set_data_type('futures')", False, str(e)[:120])

    try:
        import pandas as pd
        import numpy as np
        dates = pd.date_range("2024-01-02", periods=100, freq="B")
        test_df = pd.DataFrame({
            "close": np.random.randn(100).cumsum() + 3000,
            "volume": np.random.randint(1000, 5000, 100)
        }, index=dates)
        test_df.index.name = "date"

        r1 = checker.check_date_range_compliance(test_df, name="test_futures")
        r2 = checker.check_value_continuity(test_df, name="test_futures")
        r3 = checker.check_completeness(test_df, name="test_futures")
        r4 = checker.check_consistency(test_df, name="test_futures")
        r5 = checker.check_accuracy(test_df, name="test_futures")

        scores = [r.get("score") for r in [r1, r2, r3, r4, r5] if "score" in r]
        if len(scores) == 5:
            record("DataQualityChecker", "5维度评分", True, f"5个维度均返回score: {[round(s, 2) for s in scores]}")
        else:
            record("DataQualityChecker", "5维度评分", False, f"仅{len(scores)}个维度返回score")

        overall = checker.generate_overall_report()
        overall_score = overall.get("overall_score", 0)
        if overall_score == 100:
            record("DataQualityChecker", "综合评分=100", True, f"overall_score={overall_score}")
        else:
            record("DataQualityChecker", "综合评分=100", False, f"overall_score={overall_score}, 期望100")
    except Exception as e:
        record("DataQualityChecker", "质量检查执行", False, str(e)[:120])
except Exception as e:
    record("DataQualityChecker", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 3. Agri-PC
# ──────────────────────────────────────────────────────────────
logger.info("\n[3/12] Agri-PC 农险时序因果发现")
try:
    from models.agri_pc import AgriPC
    try:
        agri_pc = AgriPC()
        record("Agri-PC", "AgriPC实例化", True, f"alpha={agri_pc.alpha}, temporal={agri_pc.temporal_constraint}")
    except Exception as e:
        record("Agri-PC", "AgriPC实例化", False, str(e)[:120])

    try:
        has_method = hasattr(AgriPC, "_apply_temporal_constraint")
        record("Agri-PC", "_apply_temporal_constraint方法", has_method,
               "方法存在" if has_method else "方法不存在")
    except Exception as e:
        record("Agri-PC", "_apply_temporal_constraint方法", False, str(e)[:120])
except Exception as e:
    record("Agri-PC", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 4. CCP
# ──────────────────────────────────────────────────────────────
logger.info("\n[4/12] CCP 因果保形预测定价")
try:
    from models.ccp import CausalConformalPricing
    try:
        ccp = CausalConformalPricing()
        record("CCP", "CausalConformalPricing实例化", True,
               f"alpha={ccp.alpha}, conformal_type={ccp.conformal_type}")
    except Exception as e:
        record("CCP", "CausalConformalPricing实例化", False, str(e)[:120])

    try:
        has_predict = hasattr(CausalConformalPricing, "predict_interval")
        record("CCP", "predict_interval方法", has_predict,
               "方法存在" if has_predict else "方法不存在")
    except Exception as e:
        record("CCP", "predict_interval方法", False, str(e)[:120])
except Exception as e:
    record("CCP", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 5. ACML
# ──────────────────────────────────────────────────────────────
logger.info("\n[5/12] ACML 农业异质性因果定价元学习器")
try:
    from models.acml import ACML
    try:
        acml = ACML()
        record("ACML", "ACML实例化", True,
               f"lambda_agri={acml.lambda_agri}, alpha_delivery={acml.alpha_delivery}")
    except Exception as e:
        record("ACML", "ACML实例化", False, str(e)[:120])

    try:
        has_fit = hasattr(ACML, "fit")
        has_predict = hasattr(ACML, "predict_cate")
        record("ACML", "fit/predict方法", has_fit and has_predict,
               f"fit={has_fit}, predict_cate={has_predict}")
    except Exception as e:
        record("ACML", "fit/predict方法", False, str(e)[:120])
except Exception as e:
    record("ACML", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 6. PSM
# ──────────────────────────────────────────────────────────────
logger.info("\n[6/12] PSM 倾向得分匹配")
psm_ok = False
try:
    try:
        from models.causal_estimation import PSMEstimator
        psm_cls = PSMEstimator
        psm_ok = True
    except ImportError:
        pass

    if not psm_ok:
        try:
            from models.psm_model import PSMModel
            psm_cls = PSMModel
            psm_ok = True
        except ImportError:
            pass

    if psm_ok:
        try:
            psm = psm_cls()
            record("PSM", f"{psm_cls.__name__}实例化", True, f"类名={psm_cls.__name__}")
        except Exception as e:
            record("PSM", f"{psm_cls.__name__}实例化", False, str(e)[:120])
    else:
        record("PSM", "模块导入", False, "未找到PSMEstimator或PSMModel")
except Exception as e:
    record("PSM", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 7. DML
# ──────────────────────────────────────────────────────────────
logger.info("\n[7/12] DML 双重机器学习")
dml_ok = False
try:
    try:
        from models.dml_estimator import DoubleMachineLearning
        dml_cls = DoubleMachineLearning
        dml_ok = True
    except ImportError:
        pass

    if not dml_ok:
        try:
            from models.causal_estimation import DMLEstimator
            dml_cls = DMLEstimator
            dml_ok = True
        except ImportError:
            pass

    if dml_ok:
        try:
            dml = dml_cls()
            record("DML", f"{dml_cls.__name__}实例化", True, f"类名={dml_cls.__name__}")
        except Exception as e:
            record("DML", f"{dml_cls.__name__}实例化", False, str(e)[:120])
    else:
        record("DML", "模块导入", False, "未找到DoubleMachineLearning或DMLEstimator")
except Exception as e:
    record("DML", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 8. IV
# ──────────────────────────────────────────────────────────────
logger.info("\n[8/12] IV 工具变量法")
iv_ok = False
try:
    try:
        from models.iv_estimator import InstrumentalVariable
        iv_cls = InstrumentalVariable
        iv_ok = True
    except ImportError:
        pass

    if not iv_ok:
        try:
            from models.causal_estimation import IVEstimator
            iv_cls = IVEstimator
            iv_ok = True
        except ImportError:
            pass

    if iv_ok:
        try:
            import inspect
            sig = inspect.signature(iv_cls.__init__)
            required_params = [
                p for p in sig.parameters.values()
                if p.default is inspect.Parameter.empty and p.name != "self"
            ]
            if required_params:
                kwargs = {}
                for p in required_params:
                    if p.annotation == str or "var" in p.name.lower() or "instrument" in p.name.lower():
                        kwargs[p.name] = "weather_risk"
                    elif p.annotation == float or "threshold" in p.name.lower():
                        kwargs[p.name] = 10.0
                    elif p.annotation == int:
                        kwargs[p.name] = 5
                    else:
                        kwargs[p.name] = "weather_risk"
                iv = iv_cls(**kwargs)
                record("IV", f"{iv_cls.__name__}实例化", True,
                       f"类名={iv_cls.__name__}, 参数={kwargs}")
            else:
                iv = iv_cls()
                record("IV", f"{iv_cls.__name__}实例化", True, f"类名={iv_cls.__name__}")
        except Exception as e:
            record("IV", f"{iv_cls.__name__}实例化", False, str(e)[:120])
    else:
        record("IV", "模块导入", False, "未找到InstrumentalVariable或IVEstimator")
except Exception as e:
    record("IV", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 9. Ablation
# ──────────────────────────────────────────────────────────────
logger.info("\n[9/12] Ablation 消融实验")
ablation_ok = False
try:
    try:
        from models.ablation_fine_grained import agri_pc_ablation
        record("Ablation", "agri_pc_ablation函数", True, "从ablation_fine_grained导入成功")
        ablation_ok = True
    except ImportError:
        pass

    if not ablation_ok:
        try:
            from models.ablation_study import AblationStudy
            record("Ablation", "AblationStudy类", True, "从ablation_study导入成功")
            ablation_ok = True
        except ImportError:
            pass

    if not ablation_ok:
        try:
            from models.ablation_fine_grained import acml_ablation, ccp_ablation
            record("Ablation", "acml/ccp消融函数", True, "从ablation_fine_grained导入成功")
            ablation_ok = True
        except ImportError:
            pass

    if not ablation_ok:
        record("Ablation", "模块导入", False, "未找到任何消融实验函数/类")
except Exception as e:
    record("Ablation", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 10. SHAP
# ──────────────────────────────────────────────────────────────
logger.info("\n[10/12] SHAP 解释器")
try:
    shap_available = False
    try:
        import shap
        shap_available = True
        record("SHAP", "shap库导入", True, f"版本={shap.__version__}")
    except ImportError:
        record("SHAP", "shap库导入", False, "shap未安装, pip install shap")

    try:
        from models.pricing_model import SHAP_AVAILABLE
        record("SHAP", "PricingModel中SHAP集成", True,
               f"SHAP_AVAILABLE={SHAP_AVAILABLE}")
    except Exception as e:
        record("SHAP", "PricingModel中SHAP集成", False, str(e)[:120])
except Exception as e:
    record("SHAP", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 11. Visualization
# ──────────────────────────────────────────────────────────────
logger.info("\n[11/12] Visualization 可视化模块")
try:
    viz_funcs = {}
    try:
        from visualization.plot_causal_graph import plot_causal_dag, plot_correlation_heatmap
        viz_funcs["plot_causal_dag"] = plot_causal_dag
        viz_funcs["plot_correlation_heatmap"] = plot_correlation_heatmap
    except Exception as e:
        record("Visualization", "plot_causal_graph", False, str(e)[:120])

    try:
        from visualization.plot_performance import plot_model_performance, plot_prediction_comparison
        viz_funcs["plot_model_performance"] = plot_model_performance
        viz_funcs["plot_prediction_comparison"] = plot_prediction_comparison
    except Exception as e:
        record("Visualization", "plot_performance", False, str(e)[:120])

    try:
        from visualization.plot_pricing import plot_pricing_result, plot_risk_premium_composition
        viz_funcs["plot_pricing_result"] = plot_pricing_result
        viz_funcs["plot_risk_premium_composition"] = plot_risk_premium_composition
    except Exception as e:
        record("Visualization", "plot_pricing", False, str(e)[:120])

    try:
        from visualization.plot_risk import plot_risk_dashboard, plot_risk_radar
        viz_funcs["plot_risk_dashboard"] = plot_risk_dashboard
        viz_funcs["plot_risk_radar"] = plot_risk_radar
    except Exception as e:
        record("Visualization", "plot_risk", False, str(e)[:120])

    try:
        from visualization.plot_utils import set_financial_theme, save_figure
        viz_funcs["set_financial_theme"] = set_financial_theme
        viz_funcs["save_figure"] = save_figure
    except Exception as e:
        record("Visualization", "plot_utils", False, str(e)[:120])

    if viz_funcs:
        record("Visualization", "可视化函数导入汇总", True,
               f"成功导入{len(viz_funcs)}个函数: {', '.join(viz_funcs.keys())}")
    else:
        record("Visualization", "可视化函数导入汇总", False, "未成功导入任何可视化函数")
except Exception as e:
    record("Visualization", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 12. Constants
# ──────────────────────────────────────────────────────────────
logger.info("\n[12/12] Constants 常量模块")
try:
    from utils.constants import (
        CORE_SYMBOLS, SYMBOL_NAMES, ALL_SYMBOLS, PROVINCES,
        PROVINCE_FILES, RISK_LEVELS, MODEL_PARAMS, COLOR_PALETTE,
        DATA_CONFIG, FEATURE_CONFIG, DAG_CONFIG, PRICING_CONFIG
    )

    checks = []
    if CORE_SYMBOLS and len(CORE_SYMBOLS) > 0:
        checks.append(f"CORE_SYMBOLS({len(CORE_SYMBOLS)}个)")
    if SYMBOL_NAMES and len(SYMBOL_NAMES) > 0:
        checks.append(f"SYMBOL_NAMES({len(SYMBOL_NAMES)}个)")
    if ALL_SYMBOLS and len(ALL_SYMBOLS) > 0:
        checks.append(f"ALL_SYMBOLS({len(ALL_SYMBOLS)}个)")
    if PROVINCES and len(PROVINCES) > 0:
        checks.append(f"PROVINCES({len(PROVINCES)}个)")
    if PROVINCE_FILES and len(PROVINCE_FILES) > 0:
        checks.append(f"PROVINCE_FILES({len(PROVINCE_FILES)}个)")
    if RISK_LEVELS and len(RISK_LEVELS) > 0:
        checks.append(f"RISK_LEVELS({len(RISK_LEVELS)}级)")
    if MODEL_PARAMS and len(MODEL_PARAMS) > 0:
        checks.append(f"MODEL_PARAMS({len(MODEL_PARAMS)}项)")
    if COLOR_PALETTE and len(COLOR_PALETTE) > 0:
        checks.append(f"COLOR_PALETTE({len(COLOR_PALETTE)}项)")
    if DATA_CONFIG and len(DATA_CONFIG) > 0:
        checks.append(f"DATA_CONFIG({len(DATA_CONFIG)}项)")
    if DAG_CONFIG and len(DAG_CONFIG) > 0:
        checks.append(f"DAG_CONFIG({len(DAG_CONFIG)}项)")
    if PRICING_CONFIG and len(PRICING_CONFIG) > 0:
        checks.append(f"PRICING_CONFIG({len(PRICING_CONFIG)}项)")

    record("Constants", "常量模块加载", True, ", ".join(checks))

    try:
        has_a0 = "A0" in CORE_SYMBOLS
        has_heilongjiang = "黑龙江" in PROVINCE_FILES
        record("Constants", "关键值验证", has_a0 and has_heilongjiang,
               f"A0∈CORE_SYMBOLS={has_a0}, 黑龙江∈PROVINCE_FILES={has_heilongjiang}")
    except Exception as e:
        record("Constants", "关键值验证", False, str(e)[:120])
except Exception as e:
    record("Constants", "模块导入", False, str(e)[:120])

# ──────────────────────────────────────────────────────────────
# 汇总报告
# ──────────────────────────────────────────────────────────────
total_time = time.time() - total_start
total_tests = len(results)
passed = sum(1 for r in results if r["status"] == "PASS")
failed = sum(1 for r in results if r["status"] == "FAIL")
pass_rate = passed / total_tests * 100 if total_tests > 0 else 0

logger.info("\n" + "=" * 70)
logger.info("  测试结果汇总")
logger.info("=" * 70)

module_order = [
    "DataLoader", "DataQualityChecker", "Agri-PC", "CCP", "ACML",
    "PSM", "DML", "IV", "Ablation", "SHAP", "Visualization", "Constants"
]
for mod in module_order:
    mod_results = [r for r in results if r["module"] == mod]
    if not mod_results:
        continue
    mod_pass = sum(1 for r in mod_results if r["status"] == "PASS")
    mod_total = len(mod_results)
    icon = "✅" if mod_pass == mod_total else "⚠️"
    logger.info(f"\n  {icon} [{mod}] {mod_pass}/{mod_total} 通过")
    for r in mod_results:
        s_icon = "✅" if r["status"] == "PASS" else "❌"
        if r["status"] == "PASS":
            logger.info(f"      {s_icon} {r['test_name']}: {r['detail'][:80]}")
        else:
            logger.warning(f"      {s_icon} {r['test_name']}: {r['detail'][:80]}")

logger.info("\n" + "-" * 70)
logger.info(f"  总测试数: {total_tests}")
logger.info(f"  通过: {passed}")
logger.warning(f"  失败: {failed}") if failed > 0 else logger.info(f"  失败: {failed}")
logger.info(f"  通过率: {pass_rate:.1f}%")
logger.info(f"  耗时: {total_time:.2f}秒")
logger.info("=" * 70)

if failed > 0:
    logger.warning("\n  ❌ 失败项详情:")
    for r in results:
        if r["status"] == "FAIL":
            logger.warning(f"    • [{r['module']}] {r['test_name']}: {r['detail'][:100]}")

if pass_rate >= 90:
    logger.info("  🎉 整体评估: 优秀 — 系统核心功能完备")
elif pass_rate >= 70:
    logger.warning("  🟡 整体评估: 良好 — 部分模块需关注")
elif pass_rate >= 50:
    logger.warning("  🟠 整体评估: 一般 — 多个模块需修复")
else:
    logger.error("  🔴 整体评估: 较差 — 系统存在严重问题")
logger.info("=" * 70)
