from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PG_USER: str = Field(...)
    PG_PASSWORD: str = Field(...)
    PG_HOST: str = Field(...)
    PG_PORT: str = Field(...)
    PG_DB: str = Field(...)

    def MIGRATION_URL(self) -> str:
        return f"postgresql+psycopg://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    def DAO_URL(self) -> str:
        return f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}"

    model_config = SettingsConfigDict(env_file='.env')
