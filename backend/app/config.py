from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str = ""
    chroma_db_path: str = "./chroma_db"
    database_url: str = "sqlite:///./chat.db"
    frontend_url: str = "http://localhost:5173"
    llm_model: str = "gemini-2.5-flash"
    embedding_model: str = "gemini-embedding-2"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def frontend_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_url.split(",") if origin.strip()]


settings = Settings()
