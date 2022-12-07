#!/usr/bin/env python3
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
            {
                "name": "Account",
                "table_name": "accounts",
                "methods": ["get_many", "get_one", "post", "patch", "delete"],
                "model": {
                    "id": "UUID",
                    "name": "str",
                    "email": "str",
                    "password": "password",
                    "created_at": "datetime",
                    "updated_at": "datetime",
                },
                "backing_service": "mysql",  # NOTE: this is by service name
            },
            {
                "name": "Session",
                "table_name": "accounts",
                "methods": ["get_many", "get_one", "post", "delete"],
                "model": {
                    "id": "UUID",
                    "account_id": "UUID",  # TODO: something like "$Account.id"?
                    "expires_at": "datetime",
                    "created_at": "datetime",
                    "updated_at": "datetime",
                },
                "backing_service": "mysql",  # NOTE: this is by service name
            },
        ],
    }

    exit_code = create_and_run_api(specification)
    raise SystemExit(exit_code)
