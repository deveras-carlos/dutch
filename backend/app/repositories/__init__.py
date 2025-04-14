from .base_repository import BaseRepository

class RepositoryManager:
    _repositories : dict = dict(  )

    @staticmethod
    def get_manager_from_model(model):
        key = f"{ model.__name__ }_GenericManager"
        if key in RepositoryManager._repositories:
            return RepositoryManager._repositories.get(key)

        class GenericRepository(BaseRepository):
            def __init__(self):
                super().__init__(model)
                RepositoryManager._repositories[key] = self

        return GenericRepository()