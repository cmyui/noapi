import databases
import fastapi
import httpx

from noapi import context


class RestContext(context.AbstractContext):
    def __init__(self, request: fastapi.Request) -> None:
        self._request = request

    @property
    def database_client(self) -> databases.Database:
        return self._request.app.state.database_client

    @property
    def http_client(self) -> httpx.AsyncClient:
        return self._request.app.state.http_client
