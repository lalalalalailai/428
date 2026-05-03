import os
import sys
import importlib
import inspect
import textwrap
from typing import Dict, List, Optional, Tuple, Any, get_type_hints

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

MODULE_MAP = {
    'data': {
        'data_loader': 'data.data_loader',
        'data_preprocessor': 'data.data_preprocessor',
        'data_quality_checker': 'data.data_quality_checker',
        'feature_engineer': 'data.feature_engineer',
    },
    'models': {
        'agri_pc': 'models.agri_pc',
        'acml': 'models.acml',
        'ccp': 'models.ccp',
        'quintuple_validator': 'models.quintuple_validator',
        'causal_consensus': 'models.causal_consensus',
        'causal_discovery': 'models.causal_discovery',
        'causal_estimation': 'models.causal_estimation',
        'pricing_model': 'models.pricing_model',
        'risk_assessor': 'models.risk_assessor',
        'premium_calculator': 'models.premium_calculator',
        'dynamic_premium': 'models.dynamic_premium',
        'cross_market_risk': 'models.cross_market_risk',
        'extreme_risk_warning': 'models.extreme_risk_warning',
        'dml_estimator': 'models.dml_estimator',
        'iv_estimator': 'models.iv_estimator',
        'policy_evaluation': 'models.policy_evaluation',
        'social_value': 'models.social_value',
        'statistical_tests': 'models.statistical_tests',
        'theorem_proofs': 'models.theorem_proofs',
        'ablation_study': 'models.ablation_study',
        'ablation_fine_grained': 'models.ablation_fine_grained',
        'algorithm_comparison': 'models.algorithm_comparison',
        'baseline_comparison': 'models.baseline_comparison',
        'arima_baseline': 'models.arima_baseline',
    },
    'utils': {
        'config': 'utils.config',
        'constants': 'utils.constants',
        'helpers': 'utils.helpers',
        'algorithm_registry': 'utils.algorithm_registry',
        'performance_monitor': 'utils.performance_monitor',
        'cache_utils': 'utils.cache_utils',
        'anti_overfit_defense': 'utils.anti_overfit_defense',
        'complexity_analysis': 'utils.complexity_analysis',
        'debug_manager': 'utils.debug_manager',
        'reproducibility': 'utils.reproducibility',
        'paper_validator': 'utils.paper_validator',
        'cssci_benchmark': 'utils.cssci_benchmark',
        'literature_db': 'utils.literature_db',
        'issue_tracker': 'utils.issue_tracker',
        'architecture_doc': 'utils.architecture_doc',
    },
    'visualization': {
        'plot_utils': 'visualization.plot_utils',
        'plot_performance': 'visualization.plot_performance',
        'plot_pricing': 'visualization.plot_pricing',
        'plot_risk': 'visualization.plot_risk',
        'plot_causal_graph': 'visualization.plot_causal_graph',
        'plot_3d_enhanced': 'visualization.plot_3d_enhanced',
    },
}

PROJECT_INFO = {
    'name': '农险期货因果定价系统',
    'name_en': 'Agricultural Insurance Futures Causal Pricing System',
    'version': '1.0.0',
    'standard': 'GB/T 8567-2006',
    'date': '2026-04',
    'organization': 'Project Team',
}


class TechnicalDocGenerator:

    def __init__(self):
        self._modules_cache: Dict[str, Any] = {}
        self._scan_errors: List[str] = []

    def _import_module(self, module_path: str) -> Optional[Any]:
        if module_path in self._modules_cache:
            return self._modules_cache[module_path]
        try:
            mod = importlib.import_module(module_path)
            self._modules_cache[module_path] = mod
            return mod
        except Exception as e:
            self._scan_errors.append(f"{module_path}: {str(e)[:80]}")
            return None

    def _extract_classes(self, mod: Any) -> List[Tuple[str, type]]:
        classes = []
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if obj.__module__ == mod.__name__ and not name.startswith('_'):
                classes.append((name, obj))
        return classes

    def _extract_functions(self, mod: Any) -> List[Tuple[str, Any]]:
        funcs = []
        for name, obj in inspect.getmembers(mod, inspect.isfunction):
            if obj.__module__ == mod.__name__ and not name.startswith('_'):
                funcs.append((name, obj))
        return funcs

    def _format_signature(self, func: Any) -> str:
        try:
            sig = inspect.signature(func)
            return str(sig)
        except (ValueError, TypeError):
            return '()'

    def _format_type_annotation(self, annotation: Any) -> str:
        if annotation is inspect.Parameter.empty:
            return ''
        if hasattr(annotation, '__name__'):
            return annotation.__name__
        return str(annotation).replace('typing.', '')

    def _get_return_type(self, func: Any) -> str:
        try:
            sig = inspect.signature(func)
            if sig.return_annotation is not inspect.Parameter.empty:
                return self._format_type_annotation(sig.return_annotation)
        except (ValueError, TypeError):
            pass
        return ''

    def _get_param_details(self, func: Any) -> List[Dict]:
        try:
            sig = inspect.signature(func)
            params = []
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                p = {
                    'name': name,
                    'type': self._format_type_annotation(param.annotation),
                    'default': str(param.default) if param.default is not inspect.Parameter.empty else '',
                }
                params.append(p)
            return params
        except (ValueError, TypeError):
            return []

    def _get_docstring(self, obj: Any) -> str:
        doc = inspect.getdoc(obj) or ''
        return textwrap.dedent(doc).strip()

    def _scan_all_modules(self) -> Dict[str, Dict]:
        result = {}
        for pkg_name, modules in MODULE_MAP.items():
            result[pkg_name] = {}
            for mod_name, mod_path in modules.items():
                mod = self._import_module(mod_path)
                if mod is None:
                    continue
                classes = self._extract_classes(mod)
                functions = self._extract_functions(mod)
                mod_doc = self._get_docstring(mod)
                result[pkg_name][mod_name] = {
                    'module_path': mod_path,
                    'docstring': mod_doc,
                    'classes': classes,
                    'functions': functions,
                }
        return result

    def generate_api_doc(self) -> str:
        scanned = self._scan_all_modules()
        lines = []
        lines.append(f"# {PROJECT_INFO['name']} — API接口文档")
        lines.append("")
        lines.append(f"> 文档标准: {PROJECT_INFO['standard']} | 版本: {PROJECT_INFO['version']} | 日期: {PROJECT_INFO['date']}")
        lines.append("")

        lines.append("## 目录")
        lines.append("")
        toc_idx = 1
        for pkg_name in scanned:
            lines.append(f"{toc_idx}. {pkg_name} 包")
            sub_idx = 1
            for mod_name in scanned[pkg_name]:
                lines.append(f"   {toc_idx}.{sub_idx}. {mod_name}")
                sub_idx += 1
            toc_idx += 1
        lines.append("")

        for pkg_name, modules in scanned.items():
            lines.append(f"---")
            lines.append(f"## {pkg_name} 包")
            lines.append("")

            for mod_name, mod_info in modules.items():
                lines.append(f"### {mod_name}")
                lines.append(f"**模块路径**: `{mod_info['module_path']}`")
                lines.append("")

                if mod_info['docstring']:
                    doc_preview = mod_info['docstring'][:500]
                    lines.append(f"> {doc_preview}")
                    lines.append("")

                for cls_name, cls_obj in mod_info['classes']:
                    lines.append(f"#### class `{cls_name}`")
                    cls_doc = self._get_docstring(cls_obj)
                    if cls_doc:
                        lines.append(f"```")
                        lines.append(cls_doc[:600])
                        lines.append(f"```")
                        lines.append("")

                    for method_name, method_obj in inspect.getmembers(cls_obj, inspect.isfunction):
                        if method_name.startswith('_') and not method_name.startswith('__init__'):
                            continue
                        sig = self._format_signature(method_obj)
                        ret = self._get_return_type(method_obj)
                        ret_str = f" → `{ret}`" if ret else ''
                        lines.append(f"##### `{method_name}{sig}{ret_str}`")

                        params = self._get_param_details(method_obj)
                        if params:
                            lines.append("")
                            lines.append("| 参数 | 类型 | 默认值 |")
                            lines.append("|------|------|--------|")
                            for p in params:
                                default_str = p['default'] if p['default'] else '—'
                                lines.append(f"| `{p['name']}` | `{p['type']}` | {default_str} |")
                            lines.append("")

                        method_doc = self._get_docstring(method_obj)
                        if method_doc:
                            lines.append(method_doc[:400])
                            lines.append("")
                    lines.append("")

                for func_name, func_obj in mod_info['functions']:
                    sig = self._format_signature(func_obj)
                    ret = self._get_return_type(func_obj)
                    ret_str = f" → `{ret}`" if ret else ''
                    lines.append(f"#### `{func_name}{sig}{ret_str}`")

                    params = self._get_param_details(func_obj)
                    if params:
                        lines.append("")
                        lines.append("| 参数 | 类型 | 默认值 |")
                        lines.append("|------|------|--------|")
                        for p in params:
                            default_str = p['default'] if p['default'] else '—'
                            lines.append(f"| `{p['name']}` | `{p['type']}` | {default_str} |")
                        lines.append("")

                    func_doc = self._get_docstring(func_obj)
                    if func_doc:
                        lines.append(func_doc[:400])
                        lines.append("")
                    lines.append("")

        if self._scan_errors:
            lines.append("---")
            lines.append("## 扫描异常记录")
            lines.append("")
            for err in self._scan_errors:
                lines.append(f"- `{err}`")
            lines.append("")

        return "\n".join(lines)

    def generate_architecture_doc(self) -> str:
        lines = []
        lines.append(f"# {PROJECT_INFO['name']} — 架构设计文档")
        lines.append("")
        lines.append(f"> 文档标准: {PROJECT_INFO['standard']} | 版本: {PROJECT_INFO['version']}")
        lines.append("")

        lines.append("## 1. 系统概述")
        lines.append("")
        lines.append("本系统基于因果推断框架，实现农业保险期货的智能定价。"
                      "核心创新包括Agri-PC因果发现、ACML异质性因果定价、"
                      "CCP保形预测定价、五重因果验证四大原创算法。")
        lines.append("")

        lines.append("## 2. 系统架构")
        lines.append("")
        lines.append("```")
        lines.append("┌─────────────────────────────────────────────────────┐")
        lines.append("│                   表现层 (Presentation)              │")
        lines.append("│  Streamlit App / REST API / 可视化仪表盘             │")
        lines.append("├─────────────────────────────────────────────────────┤")
        lines.append("│                   业务逻辑层 (Business)              │")
        lines.append("│  定价模型 / 风险评估 / 保费计算 / 动态调整 / 预警     │")
        lines.append("├─────────────────────────────────────────────────────┤")
        lines.append("│                   因果推断层 (Causal)                │")
        lines.append("│  Agri-PC / ACML / CCP / 五重验证 / 共识机制          │")
        lines.append("├─────────────────────────────────────────────────────┤")
        lines.append("│                   数据层 (Data)                      │")
        lines.append("│  数据加载 / 预处理 / 质量检查 / 特征工程              │")
        lines.append("├─────────────────────────────────────────────────────┤")
        lines.append("│                   基础设施层 (Infrastructure)         │")
        lines.append("│  配置管理 / 日志 / 缓存 / 性能监控 / 可复现性          │")
        lines.append("└─────────────────────────────────────────────────────┘")
        lines.append("```")
        lines.append("")

        lines.append("## 3. 核心模块说明")
        lines.append("")
        lines.append("### 3.1 数据层 (data/)")
        lines.append("")
        lines.append("| 模块 | 职责 | 核心类/函数 |")
        lines.append("|------|------|-------------|")
        lines.append("| data_loader | 多源数据加载(期货/天气/宏观/遥感) | DataLoader |")
        lines.append("| data_preprocessor | 数据清洗、缺失值处理、标准化 | DataPreprocessor |")
        lines.append("| data_quality_checker | 数据质量评估与报告 | DataQualityChecker |")
        lines.append("| feature_engineer | 因果特征工程、滞后特征、交互特征 | FeatureEngineer |")
        lines.append("")

        lines.append("### 3.2 因果推断层 (models/)")
        lines.append("")
        lines.append("| 模块 | 职责 | 核心算法 |")
        lines.append("|------|------|----------|")
        lines.append("| agri_pc | 农险时序因果发现 | AgriPC (三重约束PC算法) |")
        lines.append("| acml | 异质性因果定价元学习器 | ACML (风险正则+交割权重+双重正交) |")
        lines.append("| ccp | 因果保形预测定价 | CausalConformalPricing (CQR+自适应) |")
        lines.append("| quintuple_validator | 五重因果验证 | QuintupleCausalValidator (PSM/S/T/DML/IV) |")
        lines.append("| causal_consensus | 共识机制 | CausalConsensus |")
        lines.append("| causal_discovery | 基础因果发现 | CausalDiscovery |")
        lines.append("| causal_estimation | 因果效应估计 | TLearner, SLearner |")
        lines.append("| dml_estimator | 双重机器学习 | DoubleMachineLearning |")
        lines.append("| iv_estimator | 工具变量法 | InstrumentalVariable |")
        lines.append("| pricing_model | XGBoost定价模型 | PricingModel |")
        lines.append("| risk_assessor | 多维风险评估 | RiskAssessor |")
        lines.append("| premium_calculator | 保费精算计算 | PremiumCalculator |")
        lines.append("| dynamic_premium | 动态保费调整 | DynamicPremiumAdjuster |")
        lines.append("| cross_market_risk | 跨市场风险传导 | CrossMarketRiskConductor |")
        lines.append("| extreme_risk_warning | 极端风险预警 | ExtremeRiskWarning |")
        lines.append("")

        lines.append("### 3.3 业务逻辑层")
        lines.append("")
        lines.append("| 模块 | 职责 |")
        lines.append("|------|------|")
        lines.append("| policy_evaluation | 政策效果评估 |")
        lines.append("| social_value | 社会价值量化 |")
        lines.append("| statistical_tests | 统计检验 |")
        lines.append("| theorem_proofs | 定理证明验证 |")
        lines.append("| ablation_study | 消融实验 |")
        lines.append("| algorithm_comparison | 算法对比 |")
        lines.append("| baseline_comparison | 基线对比 |")
        lines.append("")

        lines.append("### 3.4 可视化层 (visualization/)")
        lines.append("")
        lines.append("| 模块 | 职责 |")
        lines.append("|------|------|")
        lines.append("| plot_performance | 性能可视化 |")
        lines.append("| plot_pricing | 定价可视化 |")
        lines.append("| plot_risk | 风险可视化 |")
        lines.append("| plot_causal_graph | 因果图可视化 |")
        lines.append("| plot_3d_enhanced | 3D增强可视化 |")
        lines.append("")

        lines.append("## 4. 数据流")
        lines.append("")
        lines.append("```")
        lines.append("原始数据 → DataLoader → DataPreprocessor → FeatureEngineer")
        lines.append("    ↓")
        lines.append("Agri-PC(因果发现) → ACML(因果定价) → CCP(保形预测)")
        lines.append("    ↓                           ↓")
        lines.append("五重验证(共识)          PricingModel(基准价)")
        lines.append("    ↓                           ↓")
        lines.append("RiskAssessor → PremiumCalculator → DynamicPremiumAdjuster")
        lines.append("    ↓")
        lines.append("CrossMarketRisk + ExtremeRiskWarning → 最终定价输出")
        lines.append("```")
        lines.append("")

        lines.append("## 5. 理论贡献")
        lines.append("")
        lines.append("| 定理 | 内容 | 模块 |")
        lines.append("|------|------|------|")
        lines.append("| 定理1 | Agri-PC时序偏序约束下的因果识别充分条件 | agri_pc |")
        lines.append("| 定理2 | 带业务约束的因果结构一致性 | agri_pc |")
        lines.append("| 定理3 | ACML的CATE估计√n一致性 | acml |")
        lines.append("| 定理4 | 农险风险溢价的因果无偏定价公式 | acml |")
        lines.append("| 定理5 | CCP有限样本覆盖保证(无需i.i.d.) | ccp |")
        lines.append("| 定理6 | 因果残差的保形有效性 | ccp |")
        lines.append("")

        lines.append("## 6. 技术栈")
        lines.append("")
        lines.append("| 类别 | 技术 |")
        lines.append("|------|------|")
        lines.append("| 语言 | Python 3.9+ |")
        lines.append("| 机器学习 | XGBoost, scikit-learn, LightGBM |")
        lines.append("| 因果推断 | DoWhy思路, 自研Agri-PC/ACML/CCP |")
        lines.append("| 可视化 | Matplotlib, Plotly, SHAP |")
        lines.append("| Web框架 | Streamlit |")
        lines.append("| 数据处理 | Pandas, NumPy, SciPy |")
        lines.append("| 图算法 | NetworkX |")
        lines.append("")

        return "\n".join(lines)

    def generate_deployment_doc(self) -> str:
        lines = []
        lines.append(f"# {PROJECT_INFO['name']} — 部署文档")
        lines.append("")
        lines.append(f"> 文档标准: {PROJECT_INFO['standard']} | 版本: {PROJECT_INFO['version']}")
        lines.append("")

        lines.append("## 1. 环境要求")
        lines.append("")
        lines.append("### 1.1 硬件要求")
        lines.append("")
        lines.append("| 项目 | 最低配置 | 推荐配置 |")
        lines.append("|------|----------|----------|")
        lines.append("| CPU | 4核 | 8核+ |")
        lines.append("| 内存 | 8GB | 16GB+ |")
        lines.append("| 硬盘 | 10GB | 50GB+ SSD |")
        lines.append("| GPU | 无 | 可选(加速SHAP计算) |")
        lines.append("")

        lines.append("### 1.2 软件要求")
        lines.append("")
        lines.append("| 软件 | 版本 |")
        lines.append("|------|------|")
        lines.append("| Python | 3.9+ |")
        lines.append("| pip | 21.0+ |")
        lines.append("| Git | 2.30+ |")
        lines.append("")

        lines.append("## 2. 安装步骤")
        lines.append("")
        lines.append("### 2.1 克隆项目")
        lines.append("```bash")
        lines.append("git clone <repository_url>")
        lines.append("cd 03_源码及说明/src")
        lines.append("```")
        lines.append("")

        lines.append("### 2.2 安装依赖")
        lines.append("```bash")
        lines.append("pip install -r requirements.txt")
        lines.append("```")
        lines.append("")
        lines.append("核心依赖:")
        lines.append("- pandas>=1.5.0")
        lines.append("- numpy>=1.23.0")
        lines.append("- scikit-learn>=1.2.0")
        lines.append("- xgboost>=1.7.0")
        lines.append("- networkx>=2.8.0")
        lines.append("- scipy>=1.9.0")
        lines.append("- matplotlib>=3.6.0")
        lines.append("- streamlit>=1.20.0")
        lines.append("- shap>=0.41.0 (可选)")
        lines.append("")

        lines.append("### 2.3 数据准备")
        lines.append("```")
        lines.append("05_数据集/")
        lines.append("├── futures/          # 期货价格数据(CSV)")
        lines.append("├── weather/          # 气象数据(CSV)")
        lines.append("├── macro/            # 宏观经济数据(CSV)")
        lines.append("├── remote_sensing/   # 遥感数据(NDVI/EVI/LST)")
        lines.append("└── supplementary_data/  # 补充数据")
        lines.append("```")
        lines.append("")

        lines.append("## 3. 启动方式")
        lines.append("")
        lines.append("### 3.1 Web应用")
        lines.append("```bash")
        lines.append("cd src")
        lines.append("streamlit run streamlit_app.py")
        lines.append("```")
        lines.append("")

        lines.append("### 3.2 命令行运行")
        lines.append("```bash")
        lines.append("cd src")
        lines.append("python app.py")
        lines.append("```")
        lines.append("")

        lines.append("### 3.3 测试")
        lines.append("```bash")
        lines.append("cd src")
        lines.append("pytest tests/ -v")
        lines.append("```")
        lines.append("")

        lines.append("## 4. 配置说明")
        lines.append("")
        lines.append("系统配置通过 `utils/config.py` 管理，支持环境变量覆盖:")
        lines.append("")
        lines.append("| 配置项 | 默认值 | 说明 |")
        lines.append("|--------|--------|------|")
        lines.append("| DATA_ROOT | 自动检测 | 数据根目录 |")
        lines.append("| CACHE_DIR | .cache | 缓存目录 |")
        lines.append("| LOG_LEVEL | INFO | 日志级别 |")
        lines.append("")

        lines.append("## 5. 目录结构")
        lines.append("```")
        lines.append("src/")
        lines.append("├── data/               # 数据处理模块")
        lines.append("├── models/             # 核心算法模块")
        lines.append("├── utils/              # 工具模块")
        lines.append("├── visualization/      # 可视化模块")
        lines.append("├── tests/              # 测试模块")
        lines.append("├── app.py              # 主应用入口")
        lines.append("└── streamlit_app.py    # Web界面入口")
        lines.append("```")
        lines.append("")

        return "\n".join(lines)

    def generate_user_manual(self) -> str:
        lines = []
        lines.append(f"# {PROJECT_INFO['name']} — 用户手册")
        lines.append("")
        lines.append(f"> 文档标准: {PROJECT_INFO['standard']} | 版本: {PROJECT_INFO['version']}")
        lines.append("")

        lines.append("## 1. 系统简介")
        lines.append("")
        lines.append("本系统面向农业保险定价场景，提供从数据采集、因果发现、"
                      "因果定价、保形预测到保费精算的全流程智能定价能力。")
        lines.append("")

        lines.append("## 2. 快速开始")
        lines.append("")
        lines.append("### 2.1 启动系统")
        lines.append("```bash")
        lines.append("cd src && streamlit run streamlit_app.py")
        lines.append("```")
        lines.append("浏览器访问 http://localhost:8501")
        lines.append("")

        lines.append("### 2.2 基本使用流程")
        lines.append("")
        lines.append("1. **数据加载**: 选择期货品种，系统自动加载多源数据")
        lines.append("2. **因果发现**: 运行Agri-PC算法，发现变量间因果关系")
        lines.append("3. **因果定价**: 使用ACML估计异质性处理效应(CATE)")
        lines.append("4. **保形预测**: 通过CCP生成带覆盖保证的预测区间")
        lines.append("5. **五重验证**: 运行5种因果推断方法交叉验证结论")
        lines.append("6. **保费计算**: 基于精算标准计算最终保费")
        lines.append("7. **风险评估**: 多维度风险评估与极端风险预警")
        lines.append("")

        lines.append("## 3. 核心功能说明")
        lines.append("")
        lines.append("### 3.1 因果发现 (Agri-PC)")
        lines.append("- 在标准PC算法基础上增加三重约束: 时序因果、农业周期、期货交割")
        lines.append("- 输出因果DAG图，展示变量间因果关系方向与强度")
        lines.append("- 支持季节性自适应调整")
        lines.append("")

        lines.append("### 3.2 因果定价 (ACML)")
        lines.append("- 估计条件平均处理效应(CATE)，量化因果效应异质性")
        lines.append("- 农业风险正则项防止极端天气下CATE估计偏差")
        lines.append("- 交割月自适应权重解决期货到期定价漂移")
        lines.append("- 因果无偏风险溢价定价公式(定理4)")
        lines.append("")

        lines.append("### 3.3 保形预测 (CCP)")
        lines.append("- 提供有限样本覆盖保证的预测区间(无需i.i.d.假设)")
        lines.append("- 支持CQR(Conformalized Quantile Regression)和Split Conformal")
        lines.append("- 时序自适应更新应对分布偏移")
        lines.append("")

        lines.append("### 3.4 五重因果验证")
        lines.append("- PSM + S-Learner + T-Learner + DML + IV 五种方法交叉验证")
        lines.append("- 共识度评分体系(0-100)")
        lines.append("- 自动识别稳健发现与冲突发现")
        lines.append("")

        lines.append("### 3.5 保费计算")
        lines.append("- 符合《中国精算师协会农业保险费率厘定指引2023》")
        lines.append("- 支持省份系数、种植周期、保障水平等参数")
        lines.append("- 动态保费调整(风险加载+市场调整+季节因子)")
        lines.append("")

        lines.append("## 4. 常见问题")
        lines.append("")
        lines.append("### Q: 数据加载失败怎么办?")
        lines.append("A: 检查数据目录路径是否正确，确保CSV文件编码为UTF-8或GBK。")
        lines.append("")
        lines.append("### Q: SHAP分析报错?")
        lines.append("A: 需安装shap库: `pip install shap`，该功能为可选。")
        lines.append("")
        lines.append("### Q: 内存不足?")
        lines.append("A: 减少滚动窗口数量，或使用性能模式运行。")
        lines.append("")

        return "\n".join(lines)

    def generate_test_doc(self) -> str:
        lines = []
        lines.append(f"# {PROJECT_INFO['name']} — 测试文档")
        lines.append("")
        lines.append(f"> 文档标准: {PROJECT_INFO['standard']} | 版本: {PROJECT_INFO['version']}")
        lines.append("")

        lines.append("## 1. 测试概述")
        lines.append("")
        lines.append("本项目采用pytest测试框架，覆盖数据层、模型层、工具层三大模块。")
        lines.append("")

        lines.append("## 2. 测试目录结构")
        lines.append("```")
        lines.append("tests/")
        lines.append("├── conftest.py           # 测试配置与共享fixtures")
        lines.append("├── test_data_modules.py  # 数据模块测试")
        lines.append("├── test_model_modules.py # 模型模块测试")
        lines.append("└── test_utils_modules.py # 工具模块测试")
        lines.append("```")
        lines.append("")

        lines.append("## 3. 测试范围")
        lines.append("")
        lines.append("### 3.1 数据模块测试 (test_data_modules.py)")
        lines.append("")
        lines.append("| 测试项 | 覆盖内容 |")
        lines.append("|--------|----------|")
        lines.append("| DataLoader | 数据加载、缓存、编码兼容 |")
        lines.append("| DataPreprocessor | 缺失值处理、标准化、异常值 |")
        lines.append("| DataQualityChecker | 质量评分、完整性检查 |")
        lines.append("| FeatureEngineer | 特征构造、滞后特征、交互特征 |")
        lines.append("")

        lines.append("### 3.2 模型模块测试 (test_model_modules.py)")
        lines.append("")
        lines.append("| 测试项 | 覆盖内容 |")
        lines.append("|--------|----------|")
        lines.append("| AgriPC | 因果发现、三重约束、定理验证 |")
        lines.append("| ACML | CATE估计、风险正则、交割权重 |")
        lines.append("| CCP | 保形预测、覆盖保证、自适应更新 |")
        lines.append("| QuintupleValidator | 五重验证、共识分析 |")
        lines.append("| PricingModel | 训练、预测、评估 |")
        lines.append("| RiskAssessor | 风险评估、预警 |")
        lines.append("| PremiumCalculator | 保费计算 |")
        lines.append("| DynamicPremiumAdjuster | 动态调整 |")
        lines.append("| CrossMarketRiskConductor | 溢出指数、传染检测 |")
        lines.append("")

        lines.append("### 3.3 工具模块测试 (test_utils_modules.py)")
        lines.append("")
        lines.append("| 测试项 | 覆盖内容 |")
        lines.append("|--------|----------|")
        lines.append("| Config | 配置加载、路径解析 |")
        lines.append("| Helpers | 日志、计时器、格式化 |")
        lines.append("| CacheUtils | 缓存读写、键生成 |")
        lines.append("| AlgorithmRegistry | 算法注册与查询 |")
        lines.append("| PerformanceMonitor | 性能监控 |")
        lines.append("")

        lines.append("## 4. 运行测试")
        lines.append("")
        lines.append("```bash")
        lines.append("cd src")
        lines.append("pytest tests/ -v --tb=short")
        lines.append("```")
        lines.append("")

        lines.append("## 5. 验证性实验")
        lines.append("")
        lines.append("| 实验 | 目的 | 模块 |")
        lines.append("|------|------|------|")
        lines.append("| 滚动窗口验证 | 样本外预测精度 | pricing_model |")
        lines.append("| 纯预测验证 | 过拟合防御(无lag) | pricing_model |")
        lines.append("| 消融实验 | 各组件贡献度 | ablation_study |")
        lines.append("| 基线对比 | vs GLM/RF/LightGBM | baseline_comparison |")
        lines.append("| 定理验证 | 定理1-6理论保证 | theorem_proofs |")
        lines.append("| 鲁棒性检验 | 参数敏感性 | anti_overfit_defense |")
        lines.append("")

        return "\n".join(lines)

    def generate_all(self) -> Dict[str, str]:
        return {
            'api_doc': self.generate_api_doc(),
            'architecture_doc': self.generate_architecture_doc(),
            'deployment_doc': self.generate_deployment_doc(),
            'user_manual': self.generate_user_manual(),
            'test_doc': self.generate_test_doc(),
        }
