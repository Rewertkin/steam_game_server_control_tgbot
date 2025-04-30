import json
import os
from dotenv import load_dotenv, find_dotenv

class Config:
    """Класс для работы с конфигурацией"""
    def __init__(self, data: dict):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, Config(value))
            else:
                setattr(self,key, value)

def load_config() -> Config:
    """Считываем данные конфига"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return Config(config_data)

class Api_keys:
    """класс для работы с апи ключами"""
    def __init__(self, steam_api, bot_api):
        # Считываем данные токенов
        self.steam_api = steam_api
        self.bot_api = bot_api

def load_env() -> Api_keys:
    load_dotenv(find_dotenv())
    return Api_keys(os.getenv('STEAMAPI'), os.getenv('API_TOKEN'))

def modify_config_game_version(version):
    """Изменить конфиг, версию игры на сервере"""
    config.game_version = version
    with open("person_encoder.json", "w", encoding="utf-8") as f:
        json.dump(person, f, cls=PersonEncoder, ensure_ascii=False, indent=4)

config = load_config()
api_keys = load_env()