import unittest
from unittest.mock import MagicMock

from apps.base.repositories.base import DjangoRepository


def make_repo(use_replica: bool = False) -> DjangoRepository:
    repo = DjangoRepository.__new__(DjangoRepository)
    repo.model_class = MagicMock()
    repo.use_replica_for_reads = use_replica
    return repo


class TestGetManager(unittest.TestCase):
    def test_returns_objects_for_write(self):
        repo = make_repo(use_replica=True)
        self.assertIs(repo._get_manager(for_write=True), repo.model_class.objects)

    def test_returns_objects_when_replica_disabled(self):
        repo = make_repo(use_replica=False)
        self.assertIs(repo._get_manager(for_write=False), repo.model_class.objects)

    def test_returns_replica_when_available(self):
        repo = make_repo(use_replica=True)
        replica = MagicMock()
        repo.model_class.replica_objects = replica
        self.assertIs(repo._get_manager(for_write=False), replica)

    def test_falls_back_to_objects_without_replica(self):
        repo = make_repo(use_replica=True)
        repo.model_class = MagicMock(spec=['objects', 'DoesNotExist'])
        self.assertIs(repo._get_manager(for_write=False), repo.model_class.objects)


class TestGetById(unittest.TestCase):
    def test_returns_instance_when_found(self):
        repo = make_repo()
        expected = MagicMock()
        repo.model_class.objects.get.return_value = expected

        result = repo.get_by_id(1)

        repo.model_class.objects.get.assert_called_once_with(id=1)
        self.assertIs(result, expected)

    def test_returns_none_when_not_found(self):
        repo = make_repo()
        repo.model_class.DoesNotExist = LookupError
        repo.model_class.objects.get.side_effect = LookupError

        self.assertIsNone(repo.get_by_id(999))


class TestGetByIdOrRaise(unittest.TestCase):
    def test_returns_instance_when_found(self):
        repo = make_repo()
        expected = MagicMock()
        repo.model_class.objects.get.return_value = expected

        self.assertIs(repo.get_by_id_or_raise(1), expected)

    def test_raises_when_not_found(self):
        repo = make_repo()
        repo.model_class.objects.get.side_effect = LookupError

        with self.assertRaises(LookupError):
            repo.get_by_id_or_raise(999)


class TestList(unittest.TestCase):
    def test_list_without_filters(self):
        repo = make_repo()
        qs = MagicMock()
        repo.model_class.objects.filter.return_value = qs

        self.assertIs(repo.list(), qs)
        repo.model_class.objects.filter.assert_called_once_with()

    def test_list_with_filters(self):
        repo = make_repo()
        qs = MagicMock()
        repo.model_class.objects.filter.return_value = qs

        result = repo.list(name="test", is_active=True)

        repo.model_class.objects.filter.assert_called_once_with(name="test", is_active=True)
        self.assertIs(result, qs)

    def test_list_for_write_skips_replica(self):
        repo = make_repo(use_replica=True)
        repo.model_class.replica_objects = MagicMock()

        repo.list(for_write=True)

        repo.model_class.objects.filter.assert_called_once()
        repo.model_class.replica_objects.filter.assert_not_called()


class TestCreate(unittest.TestCase):
    def test_creates_and_returns_instance(self):
        repo = make_repo()
        expected = MagicMock()
        repo.model_class.objects.create.return_value = expected

        result = repo.create(name="foo", value=42)

        repo.model_class.objects.create.assert_called_once_with(name="foo", value=42)
        self.assertIs(result, expected)


class TestCreateWithM2m(unittest.TestCase):
    def test_creates_object_and_sets_m2m(self):
        repo = make_repo()
        instance = MagicMock()
        repo.model_class.objects.create.return_value = instance
        tags = [1, 2, 3]

        result = repo.create_with_m2m(m2m_field="tags", m2m_values=tags, name="foo")

        repo.model_class.objects.create.assert_called_once_with(name="foo")
        instance.tags.set.assert_called_once_with(tags)
        self.assertIs(result, instance)


class TestSetM2m(unittest.TestCase):
    def test_sets_m2m_field(self):
        instance = MagicMock()
        DjangoRepository.set_m2m(instance, "categories", [10, 20])
        instance.categories.set.assert_called_once_with([10, 20])


class TestUpdate(unittest.TestCase):
    def test_updates_attributes_and_saves(self):
        repo = make_repo()
        instance = MagicMock()

        result = repo.update(instance, name="new_name", value=99)

        self.assertEqual(instance.name, "new_name")
        self.assertEqual(instance.value, 99)
        instance.save.assert_called_once()
        self.assertIs(result, instance)


class TestDelete(unittest.TestCase):
    def test_calls_delete_on_instance(self):
        repo = make_repo()
        instance = MagicMock()
        repo.delete(instance)
        instance.delete.assert_called_once()


class TestArchive(unittest.TestCase):
    def test_sets_is_active_false(self):
        repo = make_repo()
        instance = MagicMock(spec=["is_active", "save"])
        instance.is_active = True

        repo.archive(instance)

        self.assertFalse(instance.is_active)
        instance.save.assert_called_once()

    def test_raises_if_no_is_active_field(self):
        repo = make_repo()
        instance = MagicMock(spec=[])
        repo.model_class.__name__ = "MyModel"

        with self.assertRaises(AttributeError):
            repo.archive(instance)


class TestExists(unittest.TestCase):
    def test_returns_true(self):
        repo = make_repo()
        repo.model_class.objects.filter.return_value.exists.return_value = True
        self.assertTrue(repo.exists(name="foo"))

    def test_returns_false(self):
        repo = make_repo()
        repo.model_class.objects.filter.return_value.exists.return_value = False
        self.assertFalse(repo.exists(name="ghost"))


class TestCount(unittest.TestCase):
    def test_returns_count(self):
        repo = make_repo()
        repo.model_class.objects.filter.return_value.count.return_value = 5

        result = repo.count(is_active=True)

        repo.model_class.objects.filter.assert_called_once_with(is_active=True)
        self.assertEqual(result, 5)


class TestUpdateOrCreate(unittest.TestCase):
    def test_returns_tuple_on_create(self):
        repo = make_repo()
        instance = MagicMock()
        repo.model_class.objects.update_or_create.return_value = (instance, True)

        result, created = repo.update_or_create(defaults={"name": "bar"}, slug="bar")

        repo.model_class.objects.update_or_create.assert_called_once_with(
            defaults={"name": "bar"}, slug="bar"
        )
        self.assertTrue(created)
        self.assertIs(result, instance)

    def test_returns_tuple_on_update(self):
        repo = make_repo()
        instance = MagicMock()
        repo.model_class.objects.update_or_create.return_value = (instance, False)

        _, created = repo.update_or_create(slug="bar")

        self.assertFalse(created)

    def test_defaults_none_becomes_empty_dict(self):
        repo = make_repo()
        repo.model_class.objects.update_or_create.return_value = (MagicMock(), True)

        repo.update_or_create(slug="bar")

        repo.model_class.objects.update_or_create.assert_called_once_with(
            defaults={}, slug="bar"
        )


if __name__ == "__main__":
    unittest.main()
