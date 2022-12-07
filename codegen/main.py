from noapi import create_and_run_api

if __name__ == "__main__":
    resources = {
        "Account": {
            "methods": ["get_many", "get_one", "post", "patch", "delete"],
            "model": {
                "id": "UUID",
                "name": "str",
                "email": "str",
                "password": "password",
            },
        },
        "Session": {
            "methods": ["get_many", "get_one", "post", "delete"],
            "model": {
                "id": "UUID",
                "account_id": "UUID",  # TODO: something like "$Account.id"?
                "expires": "datetime",
            },
        },
    }

    exit_code = create_and_run_api(resources)
    raise SystemExit(exit_code)
