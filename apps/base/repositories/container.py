class RepositoriesBaseContainer:
    _instance: 'RepositoriesBaseContainer | None' = None

    def __new__(cls) -> 'RepositoriesBaseContainer':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
