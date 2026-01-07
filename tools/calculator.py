"""
Safe mathematical calculator tool.
Used by Solver Agent for numeric & symbolic verification.
"""

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)

# Allowed transformations (prevents code execution)
TRANSFORMATIONS = (
    standard_transformations +
    (implicit_multiplication_application,)
)

# Whitelisted symbols & functions
ALLOWED_SYMBOLS = {
    # Constants
    "pi": sp.pi,
    "e": sp.E,

    # Functions
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "Abs": sp.Abs,

    # Algebra
    "factor": sp.factor,
    "simplify": sp.simplify,
    "expand": sp.expand,

    # Calculus
    "diff": sp.diff,
    "integrate": sp.integrate,
    "limit": sp.limit,

    # Probability helpers
    "binomial": sp.binomial
}


class Calculator:
    """
    Safe math execution engine using SymPy.
    """

    def evaluate(self, expression: str):
        """
        Evaluate numeric or symbolic expression.
        Example:
            "2 + 3*4"
            "sqrt(16)"
            "diff(x**2, x)"
        """
        try:
            expr = parse_expr(
                expression,
                local_dict=ALLOWED_SYMBOLS,
                transformations=TRANSFORMATIONS,
                evaluate=True
            )
            return {
                "success": True,
                "result": str(expr),
                "latex": sp.latex(expr)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def substitute_and_evaluate(self, expression: str, values: dict):
        """
        Substitute variables and compute numeric value.
        Example:
            expression="x**2 + 2*x + 1"
            values={"x": 2}
        """
        try:
            expr = parse_expr(
                expression,
                local_dict=ALLOWED_SYMBOLS,
                transformations=TRANSFORMATIONS,
                evaluate=True
            )
            substituted = expr.subs(values)
            numeric = substituted.evalf()
            return {
                "success": True,
                "expression": str(expr),
                "substituted": str(substituted),
                "value": float(numeric)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def check_probability_bounds(self, value):
        """
        Ensure probability is within [0,1].
        """
        try:
            val = float(value)
            return {
                "valid": 0.0 <= val <= 1.0,
                "value": val
            }
        except:
            return {
                "valid": False,
                "value": None
            }
