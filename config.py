import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    TOKEN_TG_BOT: str
    TOKEN_VB_BOT: str
    BOSS_IP: list[str]
    SERVER_IP: str
    SERVER_PORT: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    )

    def get_db_url(self):
        return (f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}")


settings = Settings()

if __name__ == "__main__":
    print(f"SERVER_IP => {settings.BOSS_IP}")
    print(f"SERVER_PORT => {settings.BOSS_IP}\n")
    print(f"DB_USER => {settings.DB_USER}")
    print(f"DB_PASSWORD => {settings.DB_PASSWORD}")
    print(f"DB_HOST => {settings.DB_HOST}")
    print(f"DB_PORT => {settings.DB_PORT}")
    print(f"DB_NAME => {settings.DB_NAME}")
    print(f"DB_URL => {settings.get_db_url()}")
    print(f"TOKEN_TG_BOT =>  {settings.TOKEN_TG_BOT}")
    print(f"TOKEN_VB_BOT => {settings.TOKEN_VB_BOT}")
    print(f"BOSS_IP => {settings.BOSS_IP}")
