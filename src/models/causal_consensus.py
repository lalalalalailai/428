import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats

from utils.helpers import logger_setup

logger = logger_setup('causal_consensus')


class CausalConsensus:
    """
    五重因果验证共识机制

    整合PSM/S-Learner/T-Learner/DML/IV五种因果推断方法的结果，
    计算共识度、识别稳健发现与冲突发现，生成共识报告。

    理论基础:
    - 多方法三角验证 (Triangulation): 不同方法基于不同假设，
      若结论一致则增强可信度
    - Rosenbaum敏感性分析思想: 评估结论对方法选择的敏感性
    - Imbens & Rubin (2015) 因果推断框架: 强调多角度验证

    共识度评分体系 (0-100):
    - 符号一致性 (30分): ATE方向是否一致
    - 效应量一致性 (30分): ATE变异系数是否较小
    - 显著性一致性 (20分): 统计显著性是否一致
    - 方法覆盖度 (20分): 有效方法数量
    """

    METHOD_NAMES = ['PSM', 'S-Learner', 'T-Learner', 'DML', 'IV-2SLS']

    METHOD_DESCRIPTIONS = {
        'PSM': {
            'full_name': 'Propensity Score Matching',
            'chinese': '倾向得分匹配',
            'strength': '控制选择偏误，半参数方法',
            'assumption': '条件独立性假设(CIA)',
            'reference': 'Rosenbaum & Rubin (1983), Biometrika'
        },
        'S-Learner': {
            'full_name': 'Single-Learner',
            'chinese': '单一学习器',
            'strength': '训练高效，避免过分割样本',
            'assumption': '处理效应可被基学习器捕捉',
            'reference': 'Kunzel et al. (2019), PNAS'
        },
        'T-Learner': {
            'full_name': 'Two-Learner',
            'chinese': '双学习器',
            'strength': '捕捉异质性处理效应(CATE)',
            'assumption': '处理/控制组模型独立',
            'reference': 'Kunzel et al. (2019), PNAS'
        },
        'DML': {
            'full_name': 'Double Machine Learning',
            'chinese': '双重机器学习',
            'strength': '消除高维混杂偏误，√n一致',
            'assumption': '部分线性模型设定',
            'reference': 'Chernozhukov et al. (2018), Econometrica'
        },
        'IV-2SLS': {
            'full_name': 'Instrumental Variable (2SLS)',
            'chinese': '工具变量法',
            'strength': '解决内生性问题',
            'assumption': 'IV相关性+外生性+排他性',
            'reference': 'Angrist & Imbens (1995), JASA'
        }
    }

    CONSENSUS_LEVELS = {
        'STRONG': {
            'min_score': 80,
            'label': '✅ 强共识',
            'color': 'green',
            'description': '多种方法高度一致，因果效应估计可靠，可直接用于定价决策和学术发表'
        },
        'MODERATE': {
            'min_score': 60,
            'label': '🟡 中等共识',
            'color': 'orange',
            'description': '大部分方法一致，结论基本可信，建议补充敏感性分析'
        },
        'WEAK': {
            'min_score': 40,
            'label': '⚠️ 弱共识',
            'color': 'red',
            'description': '方法间存在分歧，需进一步验证差异来源'
        },
        'NONE': {
            'min_score': 0,
            'label': '❌ 无共识',
            'color': 'darkred',
            'description': '方法间严重不一致，需检查数据质量或模型设定'
        }
    }

    def __init__(self, results: Dict[str, Dict]):
        """
        初始化因果共识分析器

        Args:
            results: 五重因果估计结果字典
                格式: {
                    'PSM': {'ate': float, 'ci': [lower, upper], 'p_value': float, ...},
                    'S-Learner': {'ate': float, 'ci': [lower, upper], ...},
                    'T-Learner': {'ate': float, 'ci': [lower, upper], 'cate_std': float, ...},
                    'DML': {'ate': float, 'ci': [lower, upper], 'p_value': float, ...},
                    'IV-2SLS': {'ate': float, 'ci': [lower, upper], 'p_value': float, ...}
                }
        """
        self.results = results
        self._valid_results = {}
        self._consensus = None
        self._robust_findings = None
        self._conflicting_findings = None

        self._filter_valid_results()
        logger.info(f"CausalConsensus初始化: {len(self._valid_results)}/{len(results)}个方法有效")

    def _filter_valid_results(self):
        valid = {}
        for method, res in self.results.items():
            if not isinstance(res, dict):
                continue
            if 'error' in res and res.get('ate') is None:
                continue
            if res.get('skipped'):
                continue
            ate = res.get('ate')
            if ate is not None and not (isinstance(ate, float) and np.isnan(ate)):
                valid[method] = res
        self._valid_results = valid

    def compute_consensus(self) -> Dict[str, Any]:
        """
        计算五重验证共识度

        Returns:
            共识分析结果字典，包含:
            - consensus_score: 共识度评分(0-100)
            - consensus_level: 共识等级(STRONG/MODERATE/WEAK/NONE)
            - sign_agreement: 符号一致性
            - effect_consistency: 效应量一致性
            - significance_consistency: 显著性一致性
            - method_coverage: 方法覆盖度
            - ate_statistics: ATE统计摘要
        """
        if self._consensus is not None:
            return self._consensus

        n_valid = len(self._valid_results)

        if n_valid < 2:
            self._consensus = {
                'consensus_score': 0,
                'consensus_level': 'NONE',
                'consensus_label': '❌ 数据不足',
                'n_valid_methods': n_valid,
                'message': f'有效方法仅{n_valid}个，无法进行共识分析'
            }
            return self._consensus

        ates = []
        ci_list = []
        p_values = []
        method_ates = {}

        for method, res in self._valid_results.items():
            ate = res.get('ate', 0)
            ates.append(ate)
            method_ates[method] = ate

            ci = res.get('ci', res.get('ci_lower', None))
            if isinstance(ci, (list, tuple)) and len(ci) == 2:
                ci_list.append(ci)
            elif res.get('ci_lower') is not None and res.get('ci_upper') is not None:
                ci_list.append([res['ci_lower'], res['ci_upper']])

            p = res.get('p_value', None)
            if p is not None:
                p_values.append(p)

        ates_arr = np.array(ates)
        mean_ate = float(np.mean(ates_arr))
        std_ate = float(np.std(ates_arr))
        cv_ate = std_ate / (abs(mean_ate) + 1e-8) * 100

        nonzero_ates = ates_arr[ates_arr != 0]
        signs = np.sign(nonzero_ates) if len(nonzero_ates) > 0 else np.array([])
        sign_agreement = len(set(signs.tolist())) <= 1 if len(signs) > 0 else False

        sign_score = 30 if sign_agreement else 10

        if cv_ate < 20:
            effect_score = 30
        elif cv_ate < 50:
            effect_score = 22
        elif cv_ate < 100:
            effect_score = 12
        else:
            effect_score = 5

        n_significant = sum(1 for p in p_values if p < 0.05)
        significance_ratio = n_significant / len(p_values) if p_values else 0
        significance_score = 20 * significance_ratio

        coverage_score = min(20, n_valid * 4)

        consensus_score = sign_score + effect_score + significance_score + coverage_score

        if consensus_score >= 80:
            level = 'STRONG'
        elif consensus_score >= 60:
            level = 'MODERATE'
        elif consensus_score >= 40:
            level = 'WEAK'
        else:
            level = 'NONE'

        level_info = self.CONSENSUS_LEVELS[level]

        overlap_ci = self._compute_ci_overlap(ci_list)

        self._consensus = {
            'consensus_score': round(consensus_score, 1),
            'consensus_level': level,
            'consensus_label': level_info['label'],
            'consensus_description': level_info['description'],
            'n_valid_methods': n_valid,
            'methods_used': list(self._valid_results.keys()),
            'sign_agreement': sign_agreement,
            'sign_score': sign_score,
            'effect_consistency_cv': round(cv_ate, 2),
            'effect_score': effect_score,
            'significance_ratio': round(significance_ratio, 2),
            'significance_score': round(significance_score, 1),
            'coverage_score': coverage_score,
            'ate_statistics': {
                'mean': round(mean_ate, 6),
                'std': round(std_ate, 6),
                'cv_percent': round(cv_ate, 2),
                'min': round(float(np.min(ates_arr)), 6),
                'max': round(float(np.max(ates_arr)), 6),
                'median': round(float(np.median(ates_arr)), 6)
            },
            'individual_ates': {k: round(v, 6) for k, v in method_ates.items()},
            'ci_overlap': overlap_ci,
            'p_values': {m: round(p, 4) for m, p in zip(self._valid_results.keys(), p_values)} if p_values else {}
        }

        logger.info(f"共识分析完成: 得分={consensus_score:.1f}, 等级={level}, "
                    f"ATE均值={mean_ate:.6f}, CV={cv_ate:.2f}%")

        return self._consensus

    def _compute_ci_overlap(self, ci_list: List) -> Dict:
        if len(ci_list) < 2:
            return {'has_overlap': None, 'overlap_range': None, 'description': '置信区间不足2个'}

        lower_bounds = [ci[0] for ci in ci_list]
        upper_bounds = [ci[1] for ci in ci_list]

        overlap_lower = max(lower_bounds)
        overlap_upper = min(upper_bounds)

        has_overlap = overlap_lower <= overlap_upper

        if has_overlap:
            return {
                'has_overlap': True,
                'overlap_range': [round(overlap_lower, 6), round(overlap_upper, 6)],
                'description': f'置信区间存在重叠区域[{overlap_lower:.4f}, {overlap_upper:.4f}]，共识区间可靠'
            }
        else:
            gap = overlap_lower - overlap_upper
            return {
                'has_overlap': False,
                'overlap_range': None,
                'gap': round(gap, 6),
                'description': f'置信区间无重叠，间隔={gap:.4f}，方法间效应估计存在显著差异'
            }

    def get_robust_findings(self) -> List[Dict[str, Any]]:
        """
        获取稳健发现（多数方法一致的结论）

        判定标准:
        1. 符号一致: ≥60%方法的ATE同号
        2. 效应量一致: 变异系数CV < 100%
        3. 显著性一致: ≥50%有p值的方法达到显著

        Returns:
            稳健发现列表
        """
        if self._robust_findings is not None:
            return self._robust_findings

        consensus = self.compute_consensus()
        findings = []

        if consensus['n_valid_methods'] < 2:
            self._robust_findings = []
            return self._robust_findings

        ates = []
        for method, res in self._valid_results.items():
            ate = res.get('ate', 0)
            ates.append((method, ate))

        nonzero = [(m, a) for m, a in ates if a != 0]
        if nonzero:
            positive = sum(1 for _, a in nonzero if a > 0)
            negative = len(nonzero) - positive
            majority_sign = 'positive' if positive >= negative else 'negative'
            majority_ratio = max(positive, negative) / len(nonzero)
        else:
            majority_sign = 'zero'
            majority_ratio = 0

        if majority_ratio >= 0.6:
            direction = '正向(+)' if majority_sign == 'positive' else '负向(-)'
            mean_ate = consensus['ate_statistics']['mean']
            cv = consensus['effect_consistency_cv']

            robustness_level = 'HIGH'
            if cv < 50 and majority_ratio >= 0.8:
                robustness_level = 'VERY_HIGH'
            elif cv >= 100:
                robustness_level = 'MODERATE'

            finding = {
                'finding_type': '因果效应方向',
                'conclusion': f'处理变量对结果变量存在{direction}因果效应',
                'evidence': f'{len(nonzero)}个方法中{max(positive, negative)}个估计为{direction}',
                'consensus_ratio': round(majority_ratio, 2),
                'mean_ate': round(mean_ate, 6),
                'cv_percent': round(cv, 2),
                'robustness_level': robustness_level,
                'supporting_methods': [m for m, a in nonzero
                                       if (a > 0 and majority_sign == 'positive')
                                       or (a < 0 and majority_sign == 'negative')]
            }
            findings.append(finding)

        ci_overlap = consensus.get('ci_overlap', {})
        if ci_overlap.get('has_overlap'):
            overlap_range = ci_overlap['overlap_range']
            finding = {
                'finding_type': '效应量置信区间',
                'conclusion': f'共识效应量区间[{overlap_range[0]:.4f}, {overlap_range[1]:.4f}]',
                'evidence': ci_overlap['description'],
                'consensus_ratio': None,
                'mean_ate': consensus['ate_statistics']['mean'],
                'cv_percent': consensus['effect_consistency_cv'],
                'robustness_level': 'HIGH' if consensus['consensus_score'] >= 60 else 'MODERATE',
                'supporting_methods': list(self._valid_results.keys())
            }
            findings.append(finding)

        p_values = consensus.get('p_values', {})
        if p_values:
            sig_methods = [m for m, p in p_values.items() if p < 0.05]
            if len(sig_methods) >= 2:
                finding = {
                    'finding_type': '统计显著性',
                    'conclusion': f'因果效应在{len(sig_methods)}种方法中达到统计显著(p<0.05)',
                    'evidence': f'显著方法: {", ".join(sig_methods)}',
                    'consensus_ratio': round(len(sig_methods) / len(p_values), 2),
                    'mean_ate': consensus['ate_statistics']['mean'],
                    'cv_percent': consensus['effect_consistency_cv'],
                    'robustness_level': 'HIGH' if len(sig_methods) >= 3 else 'MODERATE',
                    'supporting_methods': sig_methods
                }
                findings.append(finding)

        self._robust_findings = findings
        return findings

    def get_conflicting_findings(self) -> List[Dict[str, Any]]:
        """
        获取冲突发现（方法间不一致的结论）

        识别标准:
        1. 符号冲突: 不同方法估计的ATE方向相反
        2. 量级冲突: ATE变异系数CV > 100%
        3. 显著性冲突: 部分方法显著而部分不显著

        Returns:
            冲突发现列表
        """
        if self._conflicting_findings is not None:
            return self._conflicting_findings

        consensus = self.compute_consensus()
        conflicts = []

        if consensus['n_valid_methods'] < 2:
            self._conflicting_findings = []
            return conflicts

        ates = []
        for method, res in self._valid_results.items():
            ate = res.get('ate', 0)
            ates.append((method, ate))

        nonzero = [(m, a) for m, a in ates if a != 0]
        if nonzero:
            positive_methods = [m for m, a in nonzero if a > 0]
            negative_methods = [m for m, a in nonzero if a < 0]

            if positive_methods and negative_methods:
                conflict = {
                    'conflict_type': '效应方向冲突',
                    'description': f'部分方法估计为正向效应({", ".join(positive_methods)})，'
                                   f'部分为负向效应({", ".join(negative_methods)})',
                    'severity': 'HIGH',
                    'possible_causes': [
                        '不同方法对混杂变量的控制策略不同',
                        '处理效应存在异质性(不同子群体效应方向不同)',
                        'S-Learner可能因正则化忽略处理变量',
                        'IV方法可能捕捉的是LATE而非ATE'
                    ],
                    'recommendation': '优先参考PSM+T-Learner组合结果，检查处理效应异质性',
                    'positive_methods': positive_methods,
                    'negative_methods': negative_methods
                }
                conflicts.append(conflict)

        cv = consensus['effect_consistency_cv']
        if cv > 100:
            conflict = {
                'conflict_type': '效应量级冲突',
                'description': f'ATE变异系数CV={cv:.1f}%>100%，方法间效应量级差异极大',
                'severity': 'MODERATE',
                'possible_causes': [
                    '不同方法的假设条件不同导致估计目标不同(ATE vs LATE vs CATE)',
                    'DML/IV可能更准确地控制了混杂偏误',
                    'S-Learner可能低估处理效应(正则化偏差)'
                ],
                'recommendation': '关注置信区间重叠区域，优先采用DML和IV的估计',
                'cv_percent': round(cv, 2)
            }
            conflicts.append(conflict)

        p_values = consensus.get('p_values', {})
        if p_values:
            sig_methods = [m for m, p in p_values.items() if p < 0.05]
            nonsig_methods = [m for m, p in p_values.items() if p >= 0.05]
            if sig_methods and nonsig_methods:
                conflict = {
                    'conflict_type': '显著性冲突',
                    'description': f'部分方法显著({", ".join(sig_methods)})，'
                                   f'部分不显著({", ".join(nonsig_methods)})',
                    'severity': 'LOW',
                    'possible_causes': [
                        '统计检验力差异(样本量/模型复杂度不同)',
                        '不同方法对效应的标准误估计不同',
                        '不显著的方法可能因过度正则化导致估计偏差'
                    ],
                    'recommendation': '综合判断，若多数方法显著则结论基本可靠',
                    'significant_methods': sig_methods,
                    'nonsignificant_methods': nonsig_methods
                }
                conflicts.append(conflict)

        self._conflicting_findings = conflicts
        return conflicts

    def generate_consensus_report(self) -> str:
        """
        生成共识报告（Markdown格式）

        Returns:
            Markdown格式的共识报告字符串
        """
        consensus = self.compute_consensus()
        robust = self.get_robust_findings()
        conflicting = self.get_conflicting_findings()

        lines = []
        lines.append("## 🎯 五重因果验证共识报告")
        lines.append("")

        lines.append("### 一、共识度总览")
        lines.append("")
        lines.append(f"| 指标 | 值 |")
        lines.append(f"|------|------|")
        lines.append(f"| 共识度评分 | **{consensus['consensus_score']}/100** |")
        lines.append(f"| 共识等级 | {consensus['consensus_label']} |")
        lines.append(f"| 有效方法数 | {consensus['n_valid_methods']}/5 |")
        lines.append(f"| ATE均值 | {consensus['ate_statistics']['mean']:.6f} |")
        lines.append(f"| ATE标准差 | {consensus['ate_statistics']['std']:.6f} |")
        lines.append(f"| 变异系数CV | {consensus['effect_consistency_cv']:.2f}% |")
        lines.append(f"| 符号一致性 | {'✅ 一致' if consensus['sign_agreement'] else '⚠️ 不一致'} |")
        lines.append(f"| 显著性比例 | {consensus.get('significance_ratio', 0):.0%} |")
        lines.append("")

        lines.append("### 二、各方法估计结果")
        lines.append("")
        lines.append("| 方法 | ATE | 95% CI | P值 | 显著性 |")
        lines.append("|------|-----|--------|-----|--------|")
        for method in self.METHOD_NAMES:
            res = self._valid_results.get(method, {})
            if not res:
                lines.append(f"| {method} | — | — | — | 未运行 |")
                continue
            ate = res.get('ate', 'N/A')
            ate_str = f"{ate:.6f}" if isinstance(ate, (int, float)) else str(ate)
            ci = res.get('ci', None)
            if ci and isinstance(ci, (list, tuple)) and len(ci) == 2:
                ci_str = f"[{ci[0]:.4f}, {ci[1]:.4f}]"
            elif res.get('ci_lower') is not None and res.get('ci_upper') is not None:
                ci_str = f"[{res['ci_lower']:.4f}, {res['ci_upper']:.4f}]"
            else:
                ci_str = '—'
            p = res.get('p_value', None)
            p_str = f"{p:.4f}" if isinstance(p, (int, float)) else '—'
            sig = '✅' if (isinstance(p, (int, float)) and p < 0.05) else '❌'
            lines.append(f"| {method} | {ate_str} | {ci_str} | {p_str} | {sig} |")
        lines.append("")

        lines.append("### 三、评分分解")
        lines.append("")
        lines.append(f"| 评分维度 | 得分 | 满分 | 说明 |")
        lines.append(f"|----------|------|------|------|")
        lines.append(f"| 符号一致性 | {consensus.get('sign_score', 0)} | 30 | {'全部同号' if consensus['sign_agreement'] else '存在异号'} |")
        lines.append(f"| 效应量一致性 | {consensus.get('effect_score', 0)} | 30 | CV={consensus['effect_consistency_cv']:.1f}% |")
        lines.append(f"| 显著性一致性 | {consensus.get('significance_score', 0):.0f} | 20 | {consensus.get('significance_ratio', 0):.0%}显著 |")
        lines.append(f"| 方法覆盖度 | {consensus.get('coverage_score', 0)} | 20 | {consensus['n_valid_methods']}个方法有效 |")
        lines.append("")

        if robust:
            lines.append("### 四、稳健发现 ✅")
            lines.append("")
            for i, f in enumerate(robust, 1):
                lines.append(f"**发现{i}: {f['finding_type']}**")
                lines.append(f"- 结论: {f['conclusion']}")
                lines.append(f"- 证据: {f['evidence']}")
                lines.append(f"- 稳健性等级: {f['robustness_level']}")
                lines.append(f"- 支持方法: {', '.join(f['supporting_methods'])}")
                lines.append("")

        if conflicting:
            lines.append("### 五、冲突发现 ⚠️")
            lines.append("")
            for i, c in enumerate(conflicting, 1):
                lines.append(f"**冲突{i}: {c['conflict_type']}**")
                lines.append(f"- 描述: {c['description']}")
                lines.append(f"- 严重程度: {c['severity']}")
                lines.append(f"- 可能原因:")
                for cause in c.get('possible_causes', []):
                    lines.append(f"  - {cause}")
                lines.append(f"- 建议: {c['recommendation']}")
                lines.append("")

        ci_overlap = consensus.get('ci_overlap', {})
        if ci_overlap and ci_overlap.get('has_overlap') is not None:
            lines.append("### 六、置信区间重叠分析")
            lines.append("")
            if ci_overlap['has_overlap']:
                rng = ci_overlap['overlap_range']
                lines.append(f"✅ {len(self._valid_results)}个方法的置信区间存在重叠区域: "
                             f"[{rng[0]:.4f}, {rng[1]:.4f}]")
                lines.append(f"该区间可作为因果效应的**共识置信区间**，具有更高的统计可信度")
            else:
                lines.append(f"⚠️ 置信区间无重叠: {ci_overlap['description']}")
                lines.append(f"建议深入分析各方法的假设差异，优先采用假设更弱的方法(DML/IV)")
            lines.append("")

        lines.append("### 七、最终建议")
        lines.append("")
        if consensus['consensus_level'] == 'STRONG':
            lines.append("✅ **强烈推荐**: 五重验证达成强共识，因果效应估计高度可靠")
            lines.append(f"- 共识ATE ≈ {consensus['ate_statistics']['mean']:.4f}")
            lines.append("- 可直接用于定价决策和学术发表")
        elif consensus['consensus_level'] == 'MODERATE':
            lines.append("🟡 **推荐**: 大部分方法一致，结论基本可信")
            lines.append(f"- 共识ATE ≈ {consensus['ate_statistics']['mean']:.4f}")
            lines.append("- 建议补充敏感性分析，关注冲突发现中的建议")
        elif consensus['consensus_level'] == 'WEAK':
            lines.append("⚠️ **谨慎参考**: 方法间存在分歧")
            lines.append("- 建议优先采用PSM+T-Learner组合结果")
            lines.append("- 需进一步验证差异来源")
        else:
            lines.append("❌ **暂不推荐**: 方法间严重不一致")
            lines.append("- 需检查数据质量和模型设定")
            lines.append("- 建议重新审视研究设计")

        lines.append("")
        lines.append("---")
        lines.append("*报告由五重因果验证共识机制自动生成*")

        return "\n".join(lines)
