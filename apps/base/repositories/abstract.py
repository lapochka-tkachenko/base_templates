import abc
from typing import Any

from django.db.models import Model, QuerySet


class AbstractRepository[TModel: Model](abc.ABC):
    """Abstract base repository for data access operations."""

    model_class: type[TModel] | None = None

    @abc.abstractmethod
    def get_by_id(self, obj_id: str) -> TModel | None:
        """Retrieve object by ID or return None."""
        raise NotImplementedError

    @abc.abstractmethod
    def get_by_id_or_raise(self, obj_id: str) -> TModel:
        """Retrieve object by ID or raise DoesNotExist."""
        raise NotImplementedError

    @abc.abstractmethod
    def list(self, **filters: Any) -> QuerySet[TModel]:
        """List objects matching filters."""
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, **kwargs: Any) -> TModel:
        """Create a new object."""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, instance: TModel, **kwargs: Any) -> TModel:
        """Update an existing object."""
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, instance: TModel) -> None:
        """Delete an object."""
        raise NotImplementedError

    @abc.abstractmethod
    def exists(self, **filters: Any) -> bool:
        """Check if object exists."""
        raise NotImplementedError
