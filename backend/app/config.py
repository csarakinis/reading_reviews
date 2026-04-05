from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://reading_user:reading_pass@db:5432/reading_db"
    secret_key: str = "change-me-in-production-secret-key"
    session_cookie_name: str = "reading_session"
    app_name: str = "Reading Reviews API"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
