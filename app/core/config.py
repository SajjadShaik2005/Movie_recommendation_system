from pydantic_settings import BaseSettings
from pydantic import Field
import os

class Settings(BaseSettings):
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    debug: bool = Field(default=True, validation_alias="DEBUG")
    
    # Path to the dataset
    data_path: str = Field(
        default=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "movies.csv"),
        validation_alias="DATA_PATH"
    )
    
    # Optional TMDB API Key for fetching real movie posters
    tmdb_api_key: str = Field(default="", validation_alias="TMDB_API_KEY")
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
