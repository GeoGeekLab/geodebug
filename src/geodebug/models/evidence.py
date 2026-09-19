from dataclasses import dataclass
from typing import Any

from geodebug.models.enums import Certainty


@dataclass(frozen=True, slots=True)
class Evidence:
    key: str
    value: Any
    origin: str | None = None
    certainty: Certainty = Certainty.DETERMINISTIC
