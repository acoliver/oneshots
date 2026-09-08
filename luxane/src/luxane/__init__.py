"""Luxane: deterministic, offline total-daily-dose checker for home medication.

Same cabinet, same ingredients, same frequency: same report, byte for byte.
"""

from .registry import (
    INGREDIENTS,
    PRODUCTS,
    UNKNOWN_INGREDIENT,
    UnknownIngredient,
    ProductDim,
)
from .engine import ingredient_key, add_product_frequency, Resolution, Cabinet, analyze

__version__ = "1.0.0"

__all__ = [
    "INGREDIENTS",
    "PRODUCTS",
    "UNKNOWN_INGREDIENT",
    "UnknownIngredient",
    "Ingredient",
    "ProductDim",
    "ingredient_key",
    "add_product_frequency",
    "Resolution",
    "Cabinet",
    "analyze",
    "__version__",
]
