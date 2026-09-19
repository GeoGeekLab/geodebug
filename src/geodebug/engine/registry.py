from geodebug.rules.base import Rule


class DuplicateRuleError(ValueError):
    pass


class UnknownRuleError(KeyError):
    pass


class RuleRegistry:
    def __init__(self) -> None:
        self._rules: dict[str, Rule] = {}

    def register(self, rule: Rule) -> None:
        rule_id = rule.spec.id
        if rule_id in self._rules:
            raise DuplicateRuleError(f"duplicate rule id: {rule_id}")
        self._rules[rule_id] = rule

    def get(self, rule_id: str) -> Rule:
        try:
            return self._rules[rule_id]
        except KeyError as exc:
            raise UnknownRuleError(rule_id) from exc

    def all(self) -> tuple[Rule, ...]:
        return tuple(self._rules[key] for key in sorted(self._rules))
