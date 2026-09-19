from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.engine.policy import Policy
from geodebug.models.context import EvaluationContext
from geodebug.models.report import Report


def evaluate(context: EvaluationContext, *, policy: Policy | None = None) -> Report:
    """Evaluate the built-in rule set against an already-normalized context."""
    return Evaluator(build_default_registry(), policy=policy).evaluate(context)
