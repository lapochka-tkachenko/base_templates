from apps.base.repositories.container import RepositoriesBaseContainer
from apps.base.servic_layer.abstract import AbstractService


class BaseServiceFactory:
    def __init__(
        self,
        service: type[AbstractService],
        repositories_container: RepositoriesBaseContainer,
    ) -> None:
        self.service = service
        self.repositories_container = repositories_container

    def make(self) -> AbstractService:
        """Instantiate and return the service with the repositories container."""
        return self.service(repo=self.repositories_container)
