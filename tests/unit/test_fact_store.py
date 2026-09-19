import pytest

from geodebug.models.facts import DuplicateFactError, FactRecord, FactStore


def test_fact_store_rejects_duplicate_keys() -> None:
    facts = [FactRecord.known("crs.present", True), FactRecord.known("crs.present", False)]

    with pytest.raises(DuplicateFactError):
        FactStore(facts)


def test_fact_store_iterates_in_stable_key_order() -> None:
    store = FactStore([FactRecord.known("z", 1), FactRecord.known("a", 2)])

    assert [record.key for record in store] == ["a", "z"]
