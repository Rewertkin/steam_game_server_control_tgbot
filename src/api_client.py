import requests
import json
from types import SimpleNamespace
from config_loader import config, api_keys


def get_data_server_steam_api():
    """Получить данные сервера из Steam API"""
    url = fr"""https://api.steampowered.com/IGameServersService/GetServerList/v1/?key={api_keys.steam_api}&filter=addr\{config.addr}&filter=appid\{config.app_id}"""
    response = requests.get(url, timeout=10)
    data = response.json()
    return data


def check_server_online(server_data=None):
    """Проверить статус серверва"""
    if server_data is None:
        server_data = get_data_server_steam_api()

    try:
        # Проверяем, что "response" есть и он непустой
        if "response" in server_data and server_data["response"]:
            return True
    except json.JSONDecodeError:
        return False

def get_server_players():
    """Получить кол-во игроков на серверве"""
    try:
        return get_data_server_steam_api().get('response').get('servers')[0].get('players')
    except json.JSONDecodeError:
        return 0
    

def get_data_game_steamcmd_api():
    """Получить данные игры из SteamCMD"""
    url = f'https://api.steamcmd.net/v1/info/{config.app_id}'
    response = requests.get(url, timeout=10)
    data = response.json()
    return data

def get_current_game_version(game_data = None):
    """Получить актуальную версию игры"""
    if game_data is None:
        game_data = get_data_game_steamcmd_api()
    return game_data.get('data', 'error').get(str(config.app_id), 'error').get('_change_number', 'error')

def get_data_for_message():
    return SimpleNamespace(**get_data_server_steam_api().get('response').get('servers')[0])