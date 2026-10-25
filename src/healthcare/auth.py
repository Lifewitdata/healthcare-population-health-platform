"""Transient credentials shared by the connector and dbt child process."""
import getpass
import os
import warnings
from contextlib import contextmanager

PASSWORD_ENV = "DBT_ENV_SECRET_SNOWFLAKE_PASSWORD"
PASSWORD_AUTH = {"snowflake", "username_password_mfa"}


def password_options():
    if os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser").lower() not in PASSWORD_AUTH:
        return {}
    password = os.getenv(PASSWORD_ENV)
    if not password:
        raise ValueError("Password missing. Run healthcare build interactively or configure DBT_ENV_SECRET_SNOWFLAKE_PASSWORD in your secret manager.")
    return {"password": password}


@contextmanager
def login_password(enabled):
    needs_password = enabled and os.getenv("SNOWFLAKE_AUTHENTICATOR", "externalbrowser").lower() in PASSWORD_AUTH
    previous = os.environ.get(PASSWORD_ENV)
    prompted = needs_password and not previous
    try:
        if prompted:
            # Refuse terminals that cannot hide input.
            with warnings.catch_warnings():
                warnings.simplefilter("error", getpass.GetPassWarning)
                password = getpass.getpass("Snowflake password (hidden): ")
            if not password:
                raise ValueError("Snowflake password cannot be empty.")
            os.environ[PASSWORD_ENV] = password
        yield
    finally:
        if prompted:
            if previous is None:
                os.environ.pop(PASSWORD_ENV, None)
            else:
                os.environ[PASSWORD_ENV] = previous
