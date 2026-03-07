import abc

from apps.base.repositories.container import RepositoriesBaseContainer


class AbstractService(abc.ABC):
    """Abstract base class for services."""

    @abc.abstractmethod
    def __init__(self, repo: RepositoriesBaseContainer) -> None:
        """Initialize service with repositories container."""
        self.repo = repo
