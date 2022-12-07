def dsn(
    driver: str,
    user: str,
    password: str,
    host: str,
    port: int,
    database: str,
) -> str:
    return f"{driver}://{user}:{password}@{host}:{port}/{database}"
