from typing import Dict, List, Optional, Type, Any


class AlgorithmRegistry:
    _registry: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, category: str, algorithm_class: Type,
                 config_key: str = None) -> None:
        cls._registry[name] = {
            'class': algorithm_class,
            'category': category,
            'config_key': config_key or name,
        }

    @classmethod
    def get(cls, name: str) -> Optional[Type]:
        entry = cls._registry.get(name)
        return entry['class'] if entry else None

    @classmethod
    def list_algorithms(cls, category: str = None) -> List[str]:
        if category is None:
            return list(cls._registry.keys())
        return [name for name, info in cls._registry.items()
                if info['category'] == category]

    @classmethod
    def get_categories(cls) -> List[str]:
        return sorted({info['category'] for info in cls._registry.values()})

    @classmethod
    def create(cls, name: str, **kwargs) -> Optional[Any]:
        algorithm_class = cls.get(name)
        if algorithm_class is None:
            return None
        return algorithm_class(**kwargs)

    @classmethod
    def get_info(cls, name: str) -> Optional[Dict[str, Any]]:
        entry = cls._registry.get(name)
        if entry is None:
            return None
        return {
            'name': name,
            'category': entry['category'],
            'config_key': entry['config_key'],
            'class_name': entry['class'].__name__,
            'module': entry['class'].__module__,
        }

    @classmethod
    def get_all_info(cls) -> List[Dict[str, Any]]:
        return [cls.get_info(name) for name in cls._registry]


def register_algorithm(name: str, category: str, config_key: str = None):
    def decorator(cls):
        AlgorithmRegistry.register(name, category, cls, config_key)
        return cls
    return decorator


def _auto_register():
    try:
        from models.causal_discovery import CausalDiscovery
        AlgorithmRegistry.register('StandardPC', 'causal_discovery',
                                   CausalDiscovery, 'standard_pc')
    except ImportError:
        pass

    try:
        from models.agri_pc import AgriPC
        AlgorithmRegistry.register('AgriPC', 'causal_discovery',
                                   AgriPC, 'agri_pc')
    except ImportError:
        pass

    try:
        from models.causal_estimation import PSMEstimator
        AlgorithmRegistry.register('PSM', 'causal_estimation',
                                   PSMEstimator, 'psm')
    except ImportError:
        pass

    try:
        from models.causal_estimation import SLearner
        AlgorithmRegistry.register('SLearner', 'causal_estimation',
                                   SLearner, 's_learner')
    except ImportError:
        pass

    try:
        from models.causal_estimation import TLearner
        AlgorithmRegistry.register('TLearner', 'causal_estimation',
                                   TLearner, 't_learner')
    except ImportError:
        pass

    try:
        from models.causal_estimation import DMLEstimator
        AlgorithmRegistry.register('DML', 'causal_estimation',
                                   DMLEstimator, 'dml')
    except ImportError:
        pass

    try:
        from models.causal_estimation import IVEstimator
        AlgorithmRegistry.register('IV', 'causal_estimation',
                                   IVEstimator, 'iv')
    except ImportError:
        pass

    try:
        from models.acml import ACML
        AlgorithmRegistry.register('ACML', 'causal_estimation',
                                   ACML, 'acml')
    except ImportError:
        pass

    try:
        from models.pricing_model import PricingModel
        AlgorithmRegistry.register('XGBoostPricing', 'pricing',
                                   PricingModel, 'xgboost_pricing')
    except ImportError:
        pass

    try:
        from models.ccp import CausalConformalPricing
        AlgorithmRegistry.register('CCP', 'pricing',
                                   CausalConformalPricing, 'ccp')
    except ImportError:
        pass

    try:
        from models.risk_assessor import RiskAssessor
        AlgorithmRegistry.register('RiskAssessor', 'risk',
                                   RiskAssessor, 'risk_assessor')
    except ImportError:
        pass

    try:
        from models.extreme_risk_warning import ExtremeRiskWarning
        AlgorithmRegistry.register('ExtremeRiskWarning', 'risk',
                                   ExtremeRiskWarning, 'extreme_risk_warning')
    except ImportError:
        pass

    try:
        from models.premium_calculator import PremiumCalculator
        AlgorithmRegistry.register('PremiumCalculator', 'premium',
                                   PremiumCalculator, 'premium_calculator')
    except ImportError:
        pass

    try:
        from models.dynamic_premium import DynamicPremiumAdjuster
        AlgorithmRegistry.register('DynamicPremiumAdjuster', 'premium',
                                   DynamicPremiumAdjuster, 'dynamic_premium')
    except ImportError:
        pass

    try:
        from models.social_value import SocialValueCalculator
        AlgorithmRegistry.register('SocialValueCalculator', 'social',
                                   SocialValueCalculator, 'social_value')
    except ImportError:
        pass

    try:
        from models.policy_evaluation import PolicyEvaluator
        AlgorithmRegistry.register('PolicyEvaluator', 'policy',
                                   PolicyEvaluator, 'policy_evaluator')
    except ImportError:
        pass


_auto_register()
