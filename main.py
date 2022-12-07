#!/usr/bin/env python3
from noapi import create_and_run_api

if __name__ == "__main__":
    specification = {
        "services": [
            {
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
                "methods": ["get_many", "get_one", "post", "patch", "delete"],
                "model": {
                    "id": "UUID",
                    "name": "str",
                    "email": "str",
                    "password": "password",
                },
            },
            {
                "name": "Session",
                "methods": ["get_many", "get_one", "post", "delete"],
                "model": {
                    "id": "UUID",
                    "account_id": "UUID",  # TODO: something like "$Account.id"?
                    "expires": "datetime",
                },
            },
        ],
    }

    exit_code = create_and_run_api(specification)
    raise SystemExit(exit_code)
