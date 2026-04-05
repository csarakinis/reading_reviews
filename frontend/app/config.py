# pydantic-settings reads values from environment variables automatically.
# Any field here can be overridden by setting an environment variable with the
# same name in uppercase (e.g. BACKEND_URL=http://localhost:8000).
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Where the backend API is running. In Docker Compose the service name
    # 'backend' resolves to the correct container automatically.
    backend_url: str = "http://backend:8000"

    # Used for cryptographic operations (e.g. signing cookies). Change this
    # to a long random string in any real deployment.
    secret_key: str = "change-me-in-production-secret-key"

    # The name of the browser cookie that tracks which user is logged in.
    session_cookie_name: str = "reading_session"
    session_cookie_max_age: int = int(60 * 60 * 24 * 365.25)  # one year in seconds

    app_name: str = "Reading Reviews"

    class Config:
        # If a .env file exists next to the running process, load it too.
        env_file = ".env"


# Import this `settings` object anywhere you need configuration values.
settings = Settings()
