from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI-Based Pain Assessment Backend"
    app_version: str = "0.1.0"
    environment: str = "development"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    jwt_secret: str = "vccRBmlFkehp0hk676UzBJrB+Khf9L+pGGXMixJZDHokFMb5m1LzYVHzCbo2UisBeM9gFxP8CEE75Hz/D6gtqw=="
    jwt_algorithm: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()