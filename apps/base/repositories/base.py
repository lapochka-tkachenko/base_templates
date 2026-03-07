from collections.abc import Iterable
from typing import Any, cast

from django.db.models import Manager, Model, QuerySet

from apps.base.repositories.abstract import AbstractRepository


class DjangoRepository[TModel: Model](AbstractRepository[TModel]):
    """Base Django repository with common CRUD operations.

    Features:
    - Automatic replica database usage for read operations
    - Type-safe operations with generics
    - Consistent API across all repositories
    """

    model_class: type[TModel] | None = None
    use_replica_for_reads: bool = True

    @property
    def _model(self) -> type[TModel]:
        assert self.model_class is not None, f'{type(self).__name__}.model_class is not set'
        return self.model_class

    def _get_manager(self, *, for_write: bool = False) -> Manager[TModel]:
        """Get appropriate manager based on operation type."""
        model = self._model
        if for_write or not self.use_replica_for_reads:
            return cast('Manager[TModel]', model.objects)  # type: ignore[attr-defined]
        return cast(
            'Manager[TModel]',
            getattr(model, 'replica_objects', model.objects),  # type: ignore[attr-defined]
        )

    def get_by_id(self, obj_id: str | int) -> TModel | None:
        """Retrieve object by ID or return None."""
        try:
            return self._get_manager().get(id=obj_id)
        except self._model.DoesNotExist:  # type: ignore[attr-defined]
            return None

    def get_by_id_or_raise(self, obj_id: str | int) -> TModel:
        """Retrieve object by ID or raise DoesNotExist."""
        return self._get_manager(for_write=True).get(id=obj_id)

    def list(self, *, for_write: bool = False, **filters: Any) -> QuerySet[TModel]:
        """List objects matching filters."""
        _filters = filters or {}
        return self._get_manager(for_write=for_write).filter(**_filters)

    def create(self, **kwargs: Any) -> TModel:
        """Create a new object."""
        return cast('TModel', self._model.objects.create(**kwargs))  # type: ignore[attr-defined]

    def create_with_m2m(
        self,
        m2m_field: str,
        m2m_values: Iterable[Any],
        **fields: Any,
    ) -> TModel:
        """Create a new object and set for many to many fields."""
        obj = cast('TModel', self._model.objects.create(**fields))  # type: ignore[attr-defined]
        self.set_m2m(obj, m2m_field, m2m_values)
        return obj

    @staticmethod
    def set_m2m(obj: TModel, m2m_field: str, m2m_values: Iterable[Any]) -> None:
        """Set many-to-many field values on a model instance."""
        related_manager = getattr(obj, m2m_field)
        related_manager.set(m2m_values)

    def update(self, instance: TModel, **kwargs: Any) -> TModel:
        """Update an existing object.

        Note: Uses instance.save() to ensure model methods are called.
        """
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: TModel) -> None:
        """Delete an object."""
        instance.delete()

    def archive(self, instance: TModel) -> TModel:
        """Archive an object (soft delete).
        Sets is_archived=True instead of deleting the record.

        Args:
            instance: The model instance to archive

        Returns:
            The archived instance

        Raises:
            AttributeError: If the model doesn't have an is_active field

        """
        if not hasattr(instance, 'is_active'):
            msg = f'{self._model.__name__} does not have an is_active field'
            raise AttributeError(msg)
        return self.update(instance, is_active=False)

    def exists(self, **filters: Any) -> bool:
        """Check if object exists."""
        return self._get_manager().filter(**filters).exists()

    def count(self, **filters: Any) -> int:
        """Count objects matching filters."""
        return self._get_manager().filter(**filters).count()

    def update_or_create(
        self, defaults: dict[str, Any] | None = None, **filters: Any
    ) -> tuple[TModel, bool]:
        """Get or create object, updating if exists."""
        if defaults is None:
            defaults = {}
        return cast(
            'tuple[TModel, bool]',
            self._model.objects.update_or_create(  # type: ignore[attr-defined]
                defaults=defaults, **filters
            ),
        )
