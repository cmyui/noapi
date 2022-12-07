import abc

import databases
import httpx


class AbstractContext(abc.ABC):
    @property
    @abc.abstractmethod
    def database_client(self) -> databases.Database:
        ...

    @property
    @abc.abstractmethod
    def http_client(self) -> httpx.AsyncClient:
        ...
