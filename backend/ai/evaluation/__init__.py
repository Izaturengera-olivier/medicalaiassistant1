"""Kinyarwanda and Multilingual Evaluation System for Clinical CDS AI."""

from .dataset import EVALUATION_DATASET, get_dataset_stats
from .evaluator import KinyarwandaAIEvaluator, EvaluationResult, DimensionScore

__all__ = [
    "EVALUATION_DATASET",
    "get_dataset_stats",
    "KinyarwandaAIEvaluator",
    "EvaluationResult",
    "DimensionScore",
]
