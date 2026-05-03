# -*- coding: utf-8 -*-
ISSUE_REGISTRY = [
    {
        "id": "ISSUE-001",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'AlgorithmComparison' from 'models.algorithm_comparison'",
        "root_cause": "models/algorithm_comparison.py 中不存在 AlgorithmComparison 类，该模块仅导出函数 compare_causal_discovery / compare_causal_estimation，调用方使用了错误的类名",
        "solution": "将调用方 from models.algorithm_comparison import AlgorithmComparison 改为 from models.algorithm_comparison import compare_causal_discovery, compare_causal_estimation",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.algorithm_comparison import compare_causal_discovery, compare_causal_estimation\" 无报错"
    },
    {
        "id": "ISSUE-002",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'ACMLCausalEstimator' from 'models.acml'",
        "root_cause": "models/acml.py 中类名为 ACML 而非 ACMLCausalEstimator，调用方使用了不存在的类名",
        "solution": "将调用方 from models.acml import ACMLCausalEstimator 改为 from models.acml import ACML",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.acml import ACML\" 无报错"
    },
    {
        "id": "ISSUE-003",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'PolicyEvaluation' from 'models.policy_evaluation'",
        "root_cause": "models/policy_evaluation.py 中类名为 PolicyEvaluator 而非 PolicyEvaluation，调用方使用了错误的类名",
        "solution": "将调用方 from models.policy_evaluation import PolicyEvaluation 改为 from models.policy_evaluation import PolicyEvaluator",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.policy_evaluation import PolicyEvaluator\" 无报错"
    },
    {
        "id": "ISSUE-004",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'AgriPC' from 'models.causal_discovery'",
        "root_cause": "AgriPC 类定义在 models/agri_pc.py 中而非 models/causal_discovery.py，causal_discovery.py 仅导出 CausalDiscovery 和 CausalGraph",
        "solution": "将调用方 from models.causal_discovery import AgriPC 改为 from models.agri_pc import AgriPC",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.agri_pc import AgriPC\" 无报错"
    },
    {
        "id": "ISSUE-005",
        "severity": "P0",
        "category": "attribute_error",
        "description": "'Index' object has no attribute 'median'",
        "root_cause": "某处代码对 pandas Index 对象调用了 .median() 方法，而 pandas Index 不支持 median()，仅 Series 支持。可能出现在 gap_days 为 Index 类型或 df.columns.median() 等场景",
        "solution": "将 xxx.median() 改为 pd.Series(xxx).median() 或 float(np.median(xxx))，确保操作对象为 Series 或 ndarray",
        "status": "pending",
        "verification_method": "全局搜索 .median() 调用，确认所有调用对象均为 Series 或 ndarray 类型"
    },
    {
        "id": "ISSUE-006",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'CCPModel' from 'models.ccp'",
        "root_cause": "models/ccp.py 中类名为 CausalConformalPricing 而非 CCPModel，verify_fixes.py 使用了错误的类名",
        "solution": "将 from models.ccp import CCPModel 改为 from models.ccp import CausalConformalPricing",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.ccp import CausalConformalPricing\" 无报错"
    },
    {
        "id": "ISSUE-007",
        "severity": "P0",
        "category": "import_error",
        "description": "cannot import name 'ACMLModel' from 'models.acml'",
        "root_cause": "models/acml.py 中类名为 ACML 而非 ACMLModel，verify_fixes.py 使用了错误的类名",
        "solution": "将 from models.acml import ACMLModel 改为 from models.acml import ACML",
        "status": "fixed",
        "verification_method": "运行 python -c \"from models.acml import ACML\" 无报错"
    },
    {
        "id": "ISSUE-008",
        "severity": "P1",
        "category": "relative_import",
        "description": "attempted relative import beyond top-level package (消融实验模块)",
        "root_cause": "models/ablation_fine_grained.py 在被直接执行或以非包方式导入时，其内部 from models.xxx import 语句可能因 sys.path 未包含 src/ 而触发相对导入错误",
        "solution": "确保所有模块入口通过 src/ 目录运行(streamlit run app.py)，或在 ablation_fine_grained.py 顶部添加 sys.path 保障逻辑",
        "status": "pending",
        "verification_method": "在 src/ 目录下运行 streamlit run app.py，进入原创算法页面点击消融实验，确认无报错"
    },
    {
        "id": "ISSUE-009",
        "severity": "P1",
        "category": "reproducibility",
        "description": "可复现性检查仅通过 1/5 项 (models_importable)，data_exists/app_launchable/tests_pass/requirements_locked 均失败",
        "root_cause": "1) 数据目录路径检测失败(data_exists) 2) app启动依赖缺失(app_launchable) 3) 测试套件未通过(tests_pass) 4) requirements.txt 未锁定版本(requirements_locked)",
        "solution": "1) 确保 data/ 目录存在于正确位置 2) 修复所有 ImportError 后重试 3) 运行 pytest 修复失败用例 4) pip freeze > requirements.txt 锁定版本",
        "status": "pending",
        "verification_method": "运行 verify_reproducibility() 函数，确认 5/5 项全部通过"
    },
    {
        "id": "ISSUE-010",
        "severity": "P1",
        "category": "exception_handling",
        "description": "app.py 中存在 30+ 处 except Exception 吞没异常，可能导致关键错误被静默忽略",
        "root_cause": "大量 try-except Exception as e 块仅记录日志或显示 st.error，不抛出异常，使得运行时问题难以追踪",
        "solution": "对关键模块(数据加载/模型训练/因果推断)的 except 块增加 ErrorCollector.capture() 调用，并在日志中记录完整堆栈；非关键路径保留但增加 DEBUG 级别日志",
        "status": "pending",
        "verification_method": "检查 app.py 中所有 except Exception 块，确认关键路径均有 ErrorCollector.capture() 或完整堆栈记录"
    },
    {
        "id": "ISSUE-011",
        "severity": "P1",
        "category": "exception_handling",
        "description": "auto_test.py 中存在 20+ 处 except Exception 吞没异常，测试失败可能被静默忽略",
        "root_cause": "测试脚本中大量 except Exception 仅打印错误信息，不标记测试失败状态，可能导致测试通过率虚高",
        "solution": "将 except Exception 中的 pass/continue 改为记录失败并标记 test_passed=False，确保测试结果真实反映系统状态",
        "status": "pending",
        "verification_method": "运行 auto_test.py，确认所有异常都被正确记录为测试失败"
    },
    {
        "id": "ISSUE-012",
        "severity": "P1",
        "category": "missing_class",
        "description": "models/__init__.py 中 from .ccp import CausalConformalPricing 但未导出其他常用类(AblationStudy, SocialValueCalculator, PremiumCalculator 等)",
        "root_cause": "__init__.py 仅导出 7 个核心类，app.py 中直接 import 的类(如 SocialValueCalculator, PremiumCalculator, ExtremeRiskWarning, PolicyEvaluator, QuintupleCausalValidator)均未在 __init__.py 中导出",
        "solution": "在 models/__init__.py 中补充导出: AblationStudy, SocialValueCalculator, PremiumCalculator, ExtremeRiskWarning, PolicyEvaluator, QuintupleCausalValidator, SOTABaselineComparison, ARIMABaseline 等",
        "status": "pending",
        "verification_method": "运行 python -c \"from models import AblationStudy, SocialValueCalculator, PremiumCalculator\" 无报错"
    },
    {
        "id": "ISSUE-013",
        "severity": "P2",
        "category": "code_quality",
        "description": "src/ 目录下存在 19 处相对导入(from .xxx import)，仅在 __init__.py 中使用，但若模块被直接执行将报错",
        "root_cause": "Python 相对导入仅在包内有效，直接运行子模块(如 python models/causal_discovery.py)会触发 ValueError",
        "solution": "保持 __init__.py 中的相对导入(这是正确用法)，但确保所有入口点(app.py, streamlit_app.py)通过 sys.path 设置正确的工作目录",
        "status": "fixed",
        "verification_method": "确认 app.py 已包含 sys.path.insert(0, SRC_DIR) 逻辑，且所有入口通过 streamlit run app.py 启动"
    },
    {
        "id": "ISSUE-014",
        "severity": "P2",
        "category": "code_quality",
        "description": "39 处 except ImportError 静默降级，可能导致依赖缺失时功能静默失效",
        "root_cause": "多处模块在 ImportError 时设置 xxx_AVAILABLE=False 并跳过，用户无法感知功能缺失",
        "solution": "在 ImportError 处增加 logging.warning() 记录缺失的依赖包名，并在系统诊断页面汇总所有缺失依赖",
        "status": "pending",
        "verification_method": "检查所有 except ImportError 块，确认均有 logger.warning() 或 st.warning() 提示"
    },
    {
        "id": "ISSUE-015",
        "severity": "P2",
        "category": "code_quality",
        "description": "data/feature_engineer.py 中多处 .median() 调用，若输入为空 Series 可能返回 NaN",
        "root_cause": "feature_engineer.py 第339/423/455行调用 .median()，当 Series 为空时返回 NaN 而非 0，可能导致下游计算异常",
        "solution": "将 xxx.median() 改为 xxx.median() if len(xxx) > 0 else 0.0，或使用 .fillna(0) 保障",
        "status": "pending",
        "verification_method": "对空 DataFrame 运行特征工程流程，确认无 NaN 传播"
    },
    {
        "id": "ISSUE-016",
        "severity": "P0",
        "category": "compliance",
        "description": "参赛要求: 必须使用15款国产免费AI工具或自研AI工具，本项目使用豆包AI需在文档中明确声明",
        "root_cause": "参赛要求第五章规定只能使用指定AI工具，需在 AI工具使用说明(04-3模板) 中填写豆包AI的使用详情",
        "solution": "按04-3模板填写豆包AI使用说明，包含: 工具名称/版本/访问方式/使用时间/使用环节/Prompt/AI回复/人工修改/采纳比例",
        "status": "fixed",
        "verification_method": "检查 03_设计与开发文档/ 目录下是否存在 AI工具使用说明.docx 且包含豆包AI条目"
    },
    {
        "id": "ISSUE-017",
        "severity": "P0",
        "category": "compliance",
        "description": "参赛要求: 省赛匿名评审，所有文件不得出现学校名称/作者姓名/指导教师姓名/LOGO",
        "root_cause": "省赛采用匿名评审模式，任何文件中出现身份信息即视为违规，可能导致取消资格",
        "solution": "全局搜索所有提交文件(源码/文档/PPT/视频)，移除学校名/姓名/LOGO/水印等身份信息",
        "status": "pending",
        "verification_method": "使用 grep -r 搜索所有文件中的学校名/姓名关键词，确认无泄露"
    },
    {
        "id": "ISSUE-018",
        "severity": "P0",
        "category": "compliance",
        "description": "参赛要求: 文件夹结构必须按 4C2026 四文件夹规范组织，每个子文件夹需有 README.md",
        "root_cause": "当前目录结构可能不符合 2026012345-01作品与答辩材料/02素材与源码/03设计与开发文档/04作品演示视频 的规范",
        "solution": "按规范重组文件夹: 01作品与答辩材料(可执行程序+PPT+展示视频) / 02素材与源码(src+models+data+agent_interaction_log.json) / 03设计与开发文档(作品报告PDF+AI工具说明) / 04作品演示视频(demo_video.mp4)，每个子文件夹创建 README.md",
        "status": "pending",
        "verification_method": "检查提交文件夹结构是否与4C2026规范完全一致，且每个子文件夹含 README.md"
    },
    {
        "id": "ISSUE-019",
        "severity": "P0",
        "category": "compliance",
        "description": "参赛要求: 必须提交智能体交互记录 agent_interaction_log.json (2026年新增)",
        "root_cause": "2026年大赛新增要求，涉及AI Agent应用的队伍必须提交交互记录，展示智能体在需求理解/方法建议/代码生成/结果解释中的贡献",
        "solution": "整理与豆包AI的交互记录，按 JSON 格式保存为 agent_interaction_log.json，包含 session_id/messages(role+content) 等字段",
        "status": "fixed",
        "verification_method": "检查 02素材与源码/ 目录下是否存在 agent_interaction_log.json 且格式符合规范"
    },
    {
        "id": "ISSUE-020",
        "severity": "P1",
        "category": "compliance",
        "description": "参赛要求: 作品报告PDF正文不超过20页，需包含8章结构(含智能体使用情况章节)",
        "root_cause": "当前研究报告v5.1可能超过20页限制，且需确保包含第5章'智能体使用情况'(2026新增)",
        "solution": "从v5.1研究报告中提炼核心内容至20页以内，确保8章结构完整，特别是第5章智能体使用情况需详细填写",
        "status": "pending",
        "verification_method": "检查作品报告PDF页数<=20，且包含8章结构(含第5章智能体使用情况)"
    },
    {
        "id": "ISSUE-021",
        "severity": "P1",
        "category": "compliance",
        "description": "参赛要求: 展示视频不超过10分钟，必须有语音解说或字幕",
        "root_cause": "需录制系统功能演示+核心亮点展示+操作流程的视频，含配音解说",
        "solution": "使用录屏软件录制系统演示视频(<=10分钟)，包含语音解说，导出为MP4格式",
        "status": "pending",
        "verification_method": "检查 04作品演示视频/ 目录下是否存在 demo_video.mp4 且时长<=10分钟"
    },
    {
        "id": "ISSUE-022",
        "severity": "P1",
        "category": "compliance",
        "description": "参赛要求: 源码提交不得包含编译中间产物(.pyc, __pycache__, node_modules等)",
        "root_cause": "提交前需清理所有 __pycache__ 目录、.pyc 文件、.pyo 文件等编译中间产物",
        "solution": "运行 find . -type d -name __pycache__ -exec rm -rf {} + 和 find . -name '*.pyc' -delete 清理中间产物",
        "status": "fixed",
        "verification_method": "检查 02素材与源码/src/ 目录下不存在 __pycache__ 目录和 .pyc 文件"
    },
    {
        "id": "ISSUE-023",
        "severity": "P2",
        "category": "compliance",
        "description": "参赛要求: 作品报告中图片必须有图例(自动题注)，表格必须采用三线表形式",
        "root_cause": "评审规范要求图1 XXX / 表1 XXX 格式的自动题注，三线表形式(顶线+栏目线+底线)",
        "solution": "在Word中为所有图片插入自动题注(引用→插入题注)，所有表格改为三线表样式",
        "status": "pending",
        "verification_method": "检查作品报告中所有图片有图例标注、所有表格为三线表格式"
    },
    {
        "id": "ISSUE-024",
        "severity": "P2",
        "category": "compliance",
        "description": "参赛要求: 地图使用需符合《公开地图内容表示规范》，注明审图号和地图来源",
        "root_cause": "若项目中涉及地图可视化(如各省农险数据地图)，需确保使用合规地图并注明审图号",
        "solution": "检查所有地图可视化，若存在则替换为天地图/标准地图服务来源，并注明审图号；若不涉及地图则忽略",
        "status": "pending",
        "verification_method": "检查项目中是否存在地图可视化，若存在则确认有审图号和来源标注"
    },
    {
        "id": "ISSUE-025",
        "severity": "P1",
        "category": "model_quality",
        "description": "纯预测验证(无lag特征)未返回有效结果，模型独立预测能力未验证",
        "root_cause": "移除所有滞后特征后重新训练的纯预测验证模块返回空结果，可能因特征工程依赖 lag 特征导致训练失败",
        "solution": "检查 pure_prediction_validate() 函数实现，修复无 lag 特征时的数据处理逻辑，确保能完成训练和评估",
        "status": "pending",
        "verification_method": "在定价模型页面运行纯预测验证，确认返回有效MAPE结果"
    },
    {
        "id": "ISSUE-026",
        "severity": "P2",
        "category": "model_quality",
        "description": "三时段样本敏感性分析显示模型不稳定(CV=37.2%>20%)",
        "root_cause": "模型在不同时间段(2020-2021/2022-2023/2024-2025)的MAPE差异较大，变异系数超过20%阈值",
        "solution": "检查特定时期的市场异常数据，考虑增加时间自适应权重或分时段训练策略，降低CV至20%以下",
        "status": "pending",
        "verification_method": "重新运行三时段敏感性分析，确认CV<=20%"
    },
    {
        "id": "ISSUE-027",
        "severity": "P2",
        "category": "model_quality",
        "description": "因果分析五重验证仅达弱共识(一致性=45/100)，方法间存在分歧",
        "root_cause": "PSM/T-Learner不显著，S-Learner无明确结论，仅DML和IV-2SLS显著，五重验证一致性低",
        "solution": "在报告中如实说明五重验证结果，强调DML和IV-2SLS的显著性，讨论PSM不显著的可能原因(处理组/对照组样本不平衡: 1060 vs 16)",
        "status": "pending",
        "verification_method": "检查作品报告第6章是否如实报告五重验证结果及局限性讨论"
    },
    {
        "id": "ISSUE-028",
        "severity": "P2",
        "category": "code_quality",
        "description": "cache_utils.py 中 5 处 except Exception 吞没缓存读写异常",
        "root_cause": "缓存读写失败时静默忽略，可能导致缓存数据不一致但系统无感知",
        "solution": "在 except Exception 块中增加 logger.warning() 记录缓存操作失败详情，便于排查缓存一致性问题",
        "status": "pending",
        "verification_method": "检查 cache_utils.py 所有 except 块，确认有日志记录"
    },
    {
        "id": "ISSUE-029",
        "severity": "P2",
        "category": "code_quality",
        "description": "data/preprocessor.py 第94行 numeric_df.median() 可能对含非数值列的 DataFrame 调用失败",
        "root_cause": "fillna(numeric_df.median()) 在某些 pandas 版本中对混合类型 DataFrame 可能产生意外行为",
        "solution": "改为 numeric_df.fillna(numeric_df.median(numeric_only=True))，明确指定仅计算数值列中位数",
        "status": "pending",
        "verification_method": "对含混合类型列的 DataFrame 运行 DataPreprocessor，确认无 TypeError"
    },
    {
        "id": "ISSUE-030",
        "severity": "P1",
        "category": "compliance",
        "description": "参赛要求: AI工具使用说明需附带佐证材料(对话截图/代码diff/Prompt-Response记录)",
        "root_cause": "05.3节要求每个AI工具使用条目都需附带对话截图、代码diff对比、Prompt-Response完整记录",
        "solution": "整理豆包AI的完整交互记录，截图关键对话，记录代码修改diff，作为AI工具使用说明的附录",
        "status": "pending",
        "verification_method": "检查 AI工具使用说明.docx 是否包含佐证材料附录(截图/diff/Prompt记录)"
    },
]


def get_issue_summary():
    total = len(ISSUE_REGISTRY)
    p0_count = sum(1 for i in ISSUE_REGISTRY if i["severity"] == "P0")
    p1_count = sum(1 for i in ISSUE_REGISTRY if i["severity"] == "P1")
    p2_count = sum(1 for i in ISSUE_REGISTRY if i["severity"] == "P2")
    fixed_count = sum(1 for i in ISSUE_REGISTRY if i["status"] == "fixed")
    pending_count = sum(1 for i in ISSUE_REGISTRY if i["status"] == "pending")

    categories = {}
    for issue in ISSUE_REGISTRY:
        cat = issue["category"]
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total": total,
        "by_severity": {"P0": p0_count, "P1": p1_count, "P2": p2_count},
        "by_status": {"fixed": fixed_count, "pending": pending_count},
        "by_category": categories,
        "compliance_issues": sum(1 for i in ISSUE_REGISTRY if i["category"] == "compliance"),
        "code_issues": sum(1 for i in ISSUE_REGISTRY if i["category"] in ("import_error", "attribute_error", "relative_import", "exception_handling", "missing_class", "code_quality")),
        "model_issues": sum(1 for i in ISSUE_REGISTRY if i["category"] == "model_quality"),
    }


def verify_all_fixes():
    results = []
    for issue in ISSUE_REGISTRY:
        if issue["status"] == "fixed":
            results.append({
                "id": issue["id"],
                "description": issue["description"],
                "verification_method": issue["verification_method"],
                "verified": False,
                "note": "需手动执行验证方法确认修复生效"
            })
    return results


def get_pending_issues(severity=None):
    issues = [i for i in ISSUE_REGISTRY if i["status"] == "pending"]
    if severity:
        issues = [i for i in issues if i["severity"] == severity]
    return issues


def get_compliance_issues():
    return [i for i in ISSUE_REGISTRY if i["category"] == "compliance"]


def get_code_issues():
    code_cats = {"import_error", "attribute_error", "relative_import", "exception_handling", "missing_class", "code_quality"}
    return [i for i in ISSUE_REGISTRY if i["category"] in code_cats]


if __name__ == "__main__":
    summary = get_issue_summary()
    print("=" * 60)
    print("  评审问题清单统计")
    print("=" * 60)
    print(f"  总问题数: {summary['total']}")
    print(f"  按严重程度: P0={summary['by_severity']['P0']}, P1={summary['by_severity']['P1']}, P2={summary['by_severity']['P2']}")
    print(f"  按状态: 已修复={summary['by_status']['fixed']}, 待修复={summary['by_status']['pending']}")
    print(f"  合规性问题: {summary['compliance_issues']}")
    print(f"  代码问题: {summary['code_issues']}")
    print(f"  模型问题: {summary['model_issues']}")
    print()
    print("  按类别分布:")
    for cat, count in sorted(summary["by_category"].items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")
    print()
    print("  待修复 P0 问题:")
    for issue in get_pending_issues("P0"):
        print(f"    [{issue['id']}] {issue['description'][:80]}")
    print()
    print("  合规性问题清单:")
    for issue in get_compliance_issues():
        print(f"    [{issue['id']}][{issue['severity']}] {issue['description'][:80]}")
