from typing import Dict, List

LITERATURE_DB: Dict[str, List[Dict]] = {
    "Agri-PC": [
        {
            "title": "Order-independent constraint-based causal structure learning",
            "authors": "Colombo, D., Maathuis, M. H.",
            "year": 2014,
            "journal": "Journal of Machine Learning Research",
            "doi": "",
            "relevance": "PC/FCI算法核心改进: 提出顺序无关的约束因果结构学习, 消除PC算法对变量排序的依赖, "
                        "高维场景下显著提升因果图发现稳定性, 为Agri-PC三重约束剪枝提供理论基础",
        },
        {
            "title": "Detecting and quantifying causal associations in large nonlinear time series datasets",
            "authors": "Runge, J., Nowack, P., Kretschmer, M., Flaxman, S., Sejdinovic, D.",
            "year": 2019,
            "journal": "Science Advances",
            "doi": "10.1126/sciadv.aau4996",
            "relevance": "时序因果推断核心方法: 提出PCMCI算法, 结合PC条件独立检验与MCI条件互信息检验, "
                        "解决高维非线性时序数据的因果发现难题, 为Agri-PC时序约束设计提供直接方法论支撑",
        },
        {
            "title": "Causation, Prediction, and Search (2nd Edition)",
            "authors": "Spirtes, P., Glymour, C., Scheines, R.",
            "year": 2000,
            "journal": "MIT Press",
            "doi": "",
            "relevance": "PC/FCI因果发现算法奠基之作: 系统阐述基于条件独立检验的约束因果发现理论, "
                        "定义d-分离、忠实性等核心概念, 为Agri-PC算法提供完整的理论框架与可识别性证明基础",
        },
        {
            "title": "Causal structure learning: A review and new perspectives",
            "authors": "Heinze-Deml, C., Maathuis, M. H., Meinshausen, N.",
            "year": 2018,
            "journal": "Annual Review of Statistics and Its Application",
            "doi": "10.1146/annurev-statistics-031017-100630",
            "relevance": "因果结构学习综述: 系统对比PC/FCI/GES/NOTEARS等因果发现算法的假设条件与经验表现, "
                        "明确约束方法在稀疏高维场景的优势, 为Agri-PC算法选型提供权威依据",
        },
    ],
    "ACML": [
        {
            "title": "Metalearners for estimating heterogeneous treatment effects using machine learning",
            "authors": "Künzel, S. R., Sekhon, J. S., Bickel, P. J., Yu, B.",
            "year": 2019,
            "journal": "Proceedings of the National Academy of Sciences",
            "doi": "10.1073/pnas.1804597116",
            "relevance": "元学习因果推断核心框架: 提出X-learner/T-learner/S-learner三类元学习器, "
                        "证明X-learner在处理组样本不平衡时具有参数速率收敛性, 为ACML因果特征加权设计提供直接方法论基础",
        },
        {
            "title": "Quasi-oracle estimation of heterogeneous treatment effects",
            "authors": "Nie, X., Wager, S.",
            "year": 2021,
            "journal": "Biometrika",
            "doi": "10.1093/biomet/asaa076",
            "relevance": "R-learner准神谕估计: 提出基于Robinson分解的R-learner, 证明在 nuisance参数估计良好时"
                        "CATE估计可达准参数速率, 为ACML极端场景自适应模块的收敛性分析提供理论支撑",
        },
        {
            "title": "Recursive partitioning for heterogeneous causal effects",
            "authors": "Athey, S., Imbens, G. W.",
            "year": 2016,
            "journal": "Proceedings of the National Academy of Sciences",
            "doi": "10.1073/pnas.1510489113",
            "relevance": "异质性处理效应树: 提出因果树(Causal Tree)与诚实估计(Honest Estimation)框架, "
                        "通过样本分割消除自适应偏差, 为ACML多任务协同模块的偏差控制策略提供参考",
        },
        {
            "title": "Generalized random forests",
            "authors": "Athey, S., Tibshirani, J., Wager, S.",
            "year": 2019,
            "journal": "Annals of Statistics",
            "doi": "10.1214/18-AOS1709",
            "relevance": "广义随机森林: 将因果森林扩展至一般异质性效应估计, 提供渐近正态性与置信区间, "
                        "为ACML在农业保险定价场景中的统计推断与不确定性评估提供方法论参考",
        },
    ],
    "CCP": [
        {
            "title": "A tutorial on conformal prediction",
            "authors": "Shafer, G., Vovk, V.",
            "year": 2008,
            "journal": "Journal of Machine Learning Research",
            "doi": "",
            "relevance": "保形预测奠基教程: 系统阐述保形预测理论, 证明在可交换性假设下预测集的有限样本覆盖保证, "
                        "为CCP因果保形预测框架的覆盖保证定理(定理5)提供核心理论基础",
        },
        {
            "title": "Conformalized quantile regression",
            "authors": "Romano, Y., Patterson, E., Candès, E.",
            "year": 2019,
            "journal": "NeurIPS",
            "doi": "",
            "relevance": "保形分位数回归: 将保形预测与分位数回归结合, 实现异方差自适应的预测区间, "
                        "在保持有限样本覆盖保证的同时显著缩窄区间宽度, 为CCP区间宽度优化策略提供直接方法参考",
        },
        {
            "title": "Conformal prediction under covariate shift",
            "authors": "Tibshirani, R. J., Barber, R. F., Candes, E., Ramdas, A.",
            "year": 2019,
            "journal": "NeurIPS",
            "doi": "",
            "relevance": "协变量偏移下的保形预测: 提出加权保形预测方法, 在训练与测试分布不同时仍保持覆盖保证, "
                        "为CCP在农业数据分布偏移场景(季节性/极端行情)下的自适应覆盖提供理论支撑",
        },
        {
            "title": "Distribution-free predictive inference for regression",
            "authors": "Lei, J., G'Sell, M., Rinaldo, A., Tibshirani, R. J., Wasserman, L.",
            "year": 2018,
            "journal": "Journal of the American Statistical Association",
            "doi": "10.1080/01621459.2017.1307116",
            "relevance": "分布无关回归预测推断: 建立完整的split/full conformal回归推断框架, "
                        "证明预测带在有限样本下的边际覆盖保证与一致性, 为CCP在定价回归场景中的理论分析提供完整框架",
        },
    ],
}

ALGORITHM_DESCRIPTIONS = {
    "Agri-PC": "三重约束因果发现算法: 时序约束+业务先验+独立性检验三重剪枝的PC因果发现",
    "ACML": "三项创新元学习器: 因果特征加权+极端场景自适应+多任务协同的元学习因果推断",
    "CCP": "因果保形预测框架: 将因果信息融入保形预测, 实现有限样本覆盖保证",
}

MIN_LITERATURE_PER_ALGORITHM = 3
REQUIRED_FIELDS = ["title", "authors", "year", "journal", "relevance"]
OPTIONAL_FIELDS = ["doi"]
