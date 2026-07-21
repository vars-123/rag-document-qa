from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    chroma_db_path: str = "./chroma_db"
    database_url: str = "sqlite:///./chat.db"
    frontend_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
