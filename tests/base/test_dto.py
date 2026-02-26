from __future__ import annotations

from dataclasses import dataclass

from apps.base.dto import BaseDTO


@dataclass(slots=True)
class _SampleDTO(BaseDTO):
    name: str
    age: int


def test_from_dict_creates_instance():
    dto = _SampleDTO.from_dict({'name': 'Alice', 'age': 30})
    assert dto.name == 'Alice'
    assert dto.age == 30


def test_from_dict_ignores_unknown_keys():
    dto = _SampleDTO.from_dict({'name': 'Bob', 'age': 25, 'extra': 'ignored'})
    assert dto.name == 'Bob'
    assert dto.age == 25


def test_slots_true_subclass_has_no_dict():
    dto = _SampleDTO(name='test', age=1)
    assert not hasattr(dto, '__dict__')
