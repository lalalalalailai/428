ALGORITHM_COMPLEXITY = {
    'agri_pc': {
        'name': 'Agri-PC 农险时序因果发现',
        'time': 'O(n²·p²)',
        'space': 'O(p²)',
        'params': {'n': '样本数', 'p': '变量数'},
        'description': 'PC算法的条件独立性检验需遍历变量对与条件集，最坏情况O(n²·p²)',
        'typical_values': {'n': 1200, 'p': 15},
        'bottleneck': '条件独立性检验的样本复杂度随条件集大小指数增长'
    },
    'acml': {
        'name': 'ACML 农业异质性因果定价元学习器',
        'time': 'O(n·T·K)',
        'space': 'O(n·K)',
        'params': {'n': '样本数', 'T': '树数量', 'K': '特征数'},
        'description': '基于XGBoost的元学习器，训练复杂度与树数量和特征数线性相关',
        'typical_values': {'n': 1200, 'T': 200, 'K': 28},
        'bottleneck': '多模型训练(倾向得分+响应模型)的串行开销'
    },
    'ccp': {
        'name': 'CCP 因果保形预测定价',
        'time': 'O(n·log(n))',
        'space': 'O(n)',
        'params': {'n': '校准集大小'},
        'description': '保形预测需对校准集非一致性分数排序，排序复杂度O(n·log(n))',
        'typical_values': {'n': 240},
        'bottleneck': '校准集规模与预测区间宽度的权衡'
    },
    'psm': {
        'name': 'PSM 倾向得分匹配',
        'time': 'O(n·T·K)',
        'space': 'O(n·K)',
        'params': {'n': '样本数', 'T': '树数量', 'K': '特征数'},
        'description': '倾向得分估计基于树模型，匹配阶段为O(n²)但可优化至O(n·log(n))',
        'typical_values': {'n': 1200, 'T': 200, 'K': 28},
        'bottleneck': '最近邻匹配在大样本下的二次复杂度'
    },
    'xgboost': {
        'name': 'XGBoost 梯度提升树',
        'time': 'O(T·K·d·n)',
        'space': 'O(T·2^d)',
        'params': {'T': '树数量', 'K': '特征数', 'd': '最大深度', 'n': '样本数'},
        'description': '每棵树遍历所有特征与样本，深度d控制叶节点数2^d',
        'typical_values': {'T': 100, 'K': 28, 'd': 6, 'n': 1200},
        'bottleneck': '树深度与数量的联合增长导致空间爆炸'
    }
}

BASELINE_COMPLEXITY = {
    'pc_standard': {
        'name': '标准PC算法',
        'time': 'O(n²·p²)',
        'space': 'O(p²)',
        'note': '无时序约束，搜索空间更大'
    },
    't_learner': {
        'name': 'T-Learner元学习器',
        'time': 'O(2·n·T·K)',
        'space': 'O(2·n·K)',
        'note': '需训练两个独立模型，复杂度翻倍'
    },
    's_learner': {
        'name': 'S-Learner元学习器',
        'time': 'O(n·T·K)',
        'space': 'O(n·K)',
        'note': '单模型但CATE估计偏差较大'
    },
    'conformal_standard': {
        'name': '标准保形预测',
        'time': 'O(n·log(n))',
        'space': 'O(n)',
        'note': '无因果约束，区间覆盖保证但宽度较大'
    },
    'random_forest': {
        'name': '随机森林',
        'time': 'O(T·K·d·n·log(n))',
        'space': 'O(T·2^d)',
        'note': '每棵树需排序，比XGBoost多log(n)因子'
    },
    'linear_regression': {
        'name': '线性回归(OLS)',
        'time': 'O(n·p² + p³)',
        'space': 'O(p²)',
        'note': '矩阵求逆O(p³)，但无法捕获非线性'
    }
}


def get_complexity_report() -> str:
    lines = [
        '# 算法复杂度分析报告',
        '',
        '## 核心算法复杂度',
        '',
        '| 算法 | 时间复杂度 | 空间复杂度 | 关键参数 | 典型规模 | 瓶颈 |',
        '|------|-----------|-----------|---------|---------|------|'
    ]
    for key, info in ALGORITHM_COMPLEXITY.items():
        params_str = ', '.join(f'{k}={v}' for k, v in info['typical_values'].items())
        lines.append(
            f"| {info['name']} | {info['time']} | {info['space']} | "
            f"{params_str} | {info['description'][:30]}... | {info['bottleneck'][:25]}... |"
        )

    lines.extend([
        '',
        '## 参数说明',
        ''
    ])
    param_defs = {}
    for info in ALGORITHM_COMPLEXITY.values():
        for k, v in info['params'].items():
            if k not in param_defs:
                param_defs[k] = v
    for k, v in param_defs.items():
        lines.append(f'- **{k}**: {v}')

    lines.extend([
        '',
        '## 典型运行规模估算',
        ''
    ])
    for key, info in ALGORITHM_COMPLEXITY.items():
        tv = info['typical_values']
        tv_str = ', '.join(f'{k}={v}' for k, v in tv.items())
        lines.append(f'- **{info["name"]}**: {tv_str}')

    return '\n'.join(lines)


def compare_with_baselines() -> str:
    comparisons = {
        'agri_pc': 'pc_standard',
        'acml': 't_learner',
        'ccp': 'conformal_standard',
        'xgboost': 'random_forest'
    }

    lines = [
        '# 核心算法 vs 基线方法复杂度对比',
        '',
        '| 核心算法 | 核心时间 | 基线方法 | 基线时间 | 优势分析 |',
        '|---------|---------|---------|---------|---------|'
    ]

    for core_key, baseline_key in comparisons.items():
        core = ALGORITHM_COMPLEXITY.get(core_key)
        baseline = BASELINE_COMPLEXITY.get(baseline_key)
        if core and baseline:
            if core_key == 'agri_pc':
                advantage = '时序约束缩减搜索空间，实际O(n²·p)优于标准O(n²·p²)'
            elif core_key == 'acml':
                advantage = '共享表征减少一半训练开销 vs T-Learner的2×复杂度'
            elif core_key == 'ccp':
                advantage = '因果约束缩小校准集需求，区间更窄且覆盖保证不变'
            elif core_key == 'xgboost':
                advantage = '省去排序开销，histogram加速后实际O(T·K·d·n/bins)'
            else:
                advantage = '-'
            lines.append(
                f"| {core['name']} | {core['time']} | {baseline['name']} | "
                f"{baseline['time']} | {advantage} |"
            )

    lines.extend([
        '',
        '## 基线方法详细复杂度',
        '',
        '| 方法 | 时间复杂度 | 空间复杂度 | 说明 |',
        '|------|-----------|-----------|------|'
    ])
    for key, info in BASELINE_COMPLEXITY.items():
        lines.append(f"| {info['name']} | {info['time']} | {info['space']} | {info['note']} |")

    return '\n'.join(lines)
