from __future__ import annotations

from geodebug.facts.keys import CRS_AXIS_UNITS, CRS_KIND
from geodebug.models.context import EvaluationContext
from geodebug.models.enums import FactState, RuleState
from geodebug.models.evidence import Evidence


def geographic_crs_status(
    context: EvaluationContext,
) -> tuple[RuleState, tuple[Evidence, ...], str | None]:
    subject = context.primary
    if subject is None:
        return (RuleState.UNKNOWN, (), "Operation input is unavailable.")

    kind = subject.facts.get(CRS_KIND)
    if kind is None or kind.state is not FactState.KNOWN:
        return (RuleState.UNKNOWN, (), "CRS type could not be established.")
    if str(kind.value).casefold() != "geographic":
        return (RuleState.PASS, (), None)

    units = subject.facts.get(CRS_AXIS_UNITS)
    if units is None or units.state is not FactState.KNOWN:
        return (RuleState.UNKNOWN, (), "CRS axis units could not be established.")

    units_value = units.value
    if isinstance(units_value, (list, tuple)):
        normalized_units = tuple(str(value) for value in units_value)
    else:
        normalized_units = (str(units_value),)

    return (
        RuleState.FAIL,
        (
            Evidence(key=CRS_KIND, value="geographic"),
            Evidence(key=CRS_AXIS_UNITS, value=normalized_units),
        ),
        None,
    )
