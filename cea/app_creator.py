import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.routing import NoMatchFound

from iam.app.repositories import permission_repository
from iam.app.services.user import UserService
from iam.core.cache import RedisCache
from iam.core.configs import ServerConfigs
from iam.core.db import Database

_logger = logging.getLogger(__name__)


class AppCreator:
    def __init__(
        self,
        server_configs: ServerConfigs,
        db: Database,
        users: UserService,
        blacklist_cache: RedisCache,
    ) -> None:
        self._server_configs = server_configs
        self._server = FastAPI(
            lifespan=self.lifespan,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )

        self._server.add_middleware(
            GZipMiddleware,
            minimum_size=self._server_configs.gzip.minimum_size,
            compresslevel=self._server_configs.gzip.compress_level,
        )
        self._server.add_middleware(
            CORSMiddleware,
            allow_origins=self._server_configs.cors.origins,
            allow_methods=self._server_configs.cors.allow_methods,
            allow_headers=self._server_configs.cors.allow_headers,
            allow_credentials=self._server_configs.cors.allow_credentials,
        )

        self._db = db
        self._users = users
        self._blacklist_cache = blacklist_cache

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        await self._blacklist_cache.connect()

        await permission_repository.fill_permission_table(self._db)
        await self._users.create_super_admin()

        yield
        if self._db.engine is not None:
            await self._db.close()

        await self._blacklist_cache.close()

    def url_for(self, endpoint: str, **kwargs) -> str:
        """Generate relative URL for `endpoint`"""

        endpoint_parts = endpoint.split('.')
        endpoint_tags = endpoint_parts[:-1]
        endpoint_name = endpoint_parts[-1]
        if not endpoint_tags or not endpoint_name:
            raise NoMatchFound(endpoint, kwargs)
        for route in self._server.routes:
            if endpoint_name != route.name or any(  # type: ignore
                tag not in getattr(route, 'tags', []) for tag in endpoint_tags
            ):
                continue
            try:
                return route.url_path_for(endpoint_name, **kwargs)
            except NoMatchFound:
                pass
        raise NoMatchFound(endpoint, kwargs)

    def run(self) -> None:
        """Start `uvicorn` server.`"""
        uvicorn.run(
            self._server,
            host=self._server_configs.host,
            port=self._server_configs.port,
            proxy_headers=True,
            forwarded_allow_ips='*',
        )

    def include_routers(self) -> 'AppCreator':
        """
        Connect exceptions handlers, endpoints and blueprints to app.
        """

        from iam.app.routers import index, openapi
        from iam.app.routers.v1 import (
            auth,
            avatar,
            catalog,
            internal,
            role,
            token,
            user,
        )
        from iam.app.services import exceptions  # noqa

        if not self._server_configs.disable_swagger:
            self._server.include_router(openapi.router, tags=['OpenAPI'])

        self._server.include_router(index.router, tags=['Index'])
        self._server.include_router(role.router, tags=['Role'])
        self._server.include_router(avatar.router, tags=['Avatar'])
        self._server.include_router(user.router, tags=['User'])
        self._server.include_router(auth.router)
        self._server.include_router(token.router)
        self._server.include_router(catalog.router)
        self._server.include_router(internal.router)

        return self

    @property
    def server(self) -> FastAPI:
        return self._server
