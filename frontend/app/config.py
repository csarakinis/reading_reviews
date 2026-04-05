from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    backend_url: str = "http://backend:8000"
    secret_key: str = "change-me-in-production-secret-key"
    session_cookie_name: str = "reading_session"
    session_cookie_max_age: int = int(60 * 60 * 24 * 365.25)  # one year in seconds
    app_name: str = "Reading Reviews"

    class Config:
        env_file = ".env"


settings = Settings()
