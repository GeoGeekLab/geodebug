from __future__ import annotations

from typing import Any

from geodebug.adapters.base import InspectOptions
from geodebug.adapters.defaults import build_default_adapter_registry
from geodebug.engine.defaults import build_default_registry
from geodebug.engine.evaluator import Evaluator
from geodebug.engine.policy import Policy
from geodebug.facts.relations import build_relation_facts
from geodebug.models.context import EvaluationContext
from geodebug.models.report import Report
from geodebug.models.subjects import DatasetSnapshot


def inspect(target: Any, *, deep: bool = False) -> DatasetSnapshot:
    """Inspect one geospatial target and return normalized facts."""
    return build_default_adapter_registry().inspect(
        target,
        options=InspectOptions(deep=deep),
    )


def check(
    target: Any,
    *,
    deep: bool = False,
    policy: Policy | None = None,
) -> Report:
    """Run dataset diagnostics against one target."""
    snapshot = inspect(target, deep=deep)
    return evaluate(EvaluationContext(subjects=(snapshot,)), policy=policy)


def compare(
    left: Any,
    right: Any,
    *,
    deep: bool = False,
    policy: Policy | None = None,
) -> Report:
    """Run dataset and relational diagnostics against two targets."""
    left_snapshot = inspect(left, deep=deep)
    right_snapshot = inspect(right, deep=deep)
    relation_facts = build_relation_facts(left_snapshot, right_snapshot)
    context = EvaluationContext(
        subjects=(left_snapshot, right_snapshot),
        facts=relation_facts,
    )
    return evaluate(context, policy=policy)


def evaluate(context: EvaluationContext, *, policy: Policy | None = None) -> Report:
    """Evaluate built-in rules against an already-normalized context."""
    return Evaluator(build_default_registry(), policy=policy).evaluate(context)
