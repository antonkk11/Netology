from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):

    access_token : SecretStr
    user_id : SecretStr
    ydisk_token : SecretStr

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

config = Settings()
