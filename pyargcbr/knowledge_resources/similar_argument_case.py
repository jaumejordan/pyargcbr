from dataclasses import dataclass

from .argument_case import ArgumentCase
from .similar_case import SimilarCase


@dataclass
class SimilarArgumentCase(SimilarCase):
    """Structure to store the degree of similarity of an argument case

    In similar argument cases the similarity is interpreted as suitability"""
    case: ArgumentCase
