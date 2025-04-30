import asyncio
import subprocess
from config_loader import config, modify_config_game_version
import api_client

# Флаг обновления сервера
updating_event = asyncio.Event()

async def update_server():
    """Обновить сервер"""
    updating_event.set() #флаг обновления
    update_process = await asyncio.create_subprocess_shell(config.update_server)
    try:
        await asyncio.wait_for(update_process.wait(), config.start_waiting_time)
        result = True
    except asyncio.TimeoutError:
        update_process.terminate()  # Принудительное завершение, если превышено время
        result = False
    updating_event.clear() #снимаем флаг обновления
    modify_config_game_version(api_client.get_current_game_version())
    await start_server()
    return result

async def stop_server():
    """Остановить сервер"""
    stop_process = await asyncio.create_subprocess_shell(f'start cmd /c "{config.stop_server}"')
    try:
        await asyncio.wait_for(stop_process.wait(), config.stop_waiting_time)
        return True
    except asyncio.TimeoutError:
        stop_process.kill()  # Принудительное завершение, если превышено время
        return False
    
async def start_server():
    """Запустить сервер"""
    subprocess.Popen(f"start cmd /c {config.start_server}", shell=True)

async def update_server_bg():
    """Фоновый запуск обновления сервера"""
    while True:
        current_game_version = api_client.get_current_game_version()
        if get_server_game_version() != current_game_version and api_client.get_server_players() == 0:
            result_stop = await stop_server()
            if result_stop:
                print("Автоматичекий апдейт сервера")
                await update_server()
                print("Автоматичекий апдейт сервера завершен")
        await asyncio.sleep(config.bg_waiting_time)

def get_server_game_version():
    """Получить версию игры на серверве"""
    return int(config.game_version)

def check_status_update():
    """Проверить статус обновления"""
    if updating_event.is_set():
        return False
    return True

async def manual_start_server():
    if check_status_update():
        if not api_client.check_server_online():
            await start_server()
        return'Сервер запущен!'
    return 'Сервер обновляется! Дождитесь обновления!'

async def manual_server_stop():
    """Ручная остановка сервера"""
    result = await stop_server()
    if result is False:
        return '❌Что-то пошло не так!'
    return 'Сервер остановлен!'

async def manual_server_update():
    result = await update_server()
    if result:
        return 'Сервер обновлен и запущен!'
    return 'Что-то пошло не так. Возможно сервер еще обновляется.'