#!/usr/bin/env python3
from datetime import datetime
from uuid import UUID
from uuid import uuid4

from pydantic.fields import FieldInfo

from noapi import create_and_run_api

if __name__ == "__main__":
    specification = {
        "services": [
            {
                "name": "mysql",
                "type": "sql",
                "driver": "mysql",
                "user": "cmyui",
                "password": "lol123",
                "host": "localhost",
                "port": 3306,
                "database": "noapi",
            },
        ],
        "resources": [
            # TODO: resource definitions are diverging from configuration into python code.
            # this likely needs to be factored out into more parsing logic if we're
            # to make to the tier of an an industry-standard technology.
            {
                "name": "Account",
                "table_name": "accounts",
                "methods": ["get_many", "get_one", "post", "patch", "delete"],
                "model": {
                    "id": (UUID, FieldInfo(default_factory=uuid4)),
                    "name": (str, "John"),
                    "email": (str, "john@example.com"),
                    "password": (str, "someSecureP4assw0rd"),
                    "created_at": (datetime, FieldInfo(default_factory=datetime.now)),
                    "updated_at": (datetime, FieldInfo(default_factory=datetime.now)),
                },
                "backing_service": "mysql",  # NOTE: this is by service name
            },
            {
                "name": "Session",
                "table_name": "accounts",
                "methods": ["get_many", "get_one", "post", "delete"],
                "model": {
                    "id": (UUID, FieldInfo(default_factory=uuid4)),
                    # TODO: something like "$Account.id"?
                    "account_id": (UUID, FieldInfo(default_factory=uuid4)),
                    "expires_at": (datetime, FieldInfo(default_factory=datetime.now)),
                    "created_at": (datetime, FieldInfo(default_factory=datetime.now)),
                    "updated_at": (datetime, FieldInfo(default_factory=datetime.now)),
                },
                "backing_service": "mysql",  # NOTE: this is by service name
            },
        ],
    }

    exit_code = create_and_run_api(specification)
    raise SystemExit(exit_code)
