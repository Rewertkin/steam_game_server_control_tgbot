import asyncio
import json
import subprocess
import requests
import time
from dotenv import load_dotenv, find_dotenv
import os
from dotenv import load_dotenv, find_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from dataclasses import dataclass
from types import SimpleNamespace

# Считываем данные конфига
with open("config.json", "r", encoding="utf-8") as file: 
    config = json.load(file)
WHITELIST = config["allowed_users"]
START_WAITING_TIME = config["start_waiting_time"]
BG_WAITING_TIME = config["bg_waiting_time"]
APP_ID = config['app_id']

# Считываем данные токенов
load_dotenv(find_dotenv())
API_TOKEN = os.getenv('API_TOKEN')
STEAMAPI = os.getenv('STEAMAPI')

# Флаг обновления сервера
updating_event = asyncio.Event()

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

def run_batch_file(file_path):
    subprocess.Popen(file_path,creationflags=subprocess.CREATE_NEW_CONSOLE)

async def send_message(text, message):
    await message.answer(text)
    print(f'{message.chat.id} = {text}')

def get_data_server_steam_api():
    url = f'https://api.steampowered.com/IGameServersService/GetServerList/v1/?key={STEAMAPI}&filter=addr\81.30.105.180&filter=appid\{APP_ID}'

    response = requests.get(url)
    data = response.json()
    return data

def get_data_game_steamcmd_api():
    url = f'https://api.steamcmd.net/v1/info/{APP_ID}'
    
    response = requests.get(url)
    data = response.json()
    return data

def get_current_game_version(game_data):
    return game_data.get('data', 'error').get(str(APP_ID), 'error').get('_change_number', 'error')


def get_server_game_version():
    return int(config["game_version"])

def modify_config_game_version(version):
    config["game_version"] = version
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

def check_status_update():
    if updating_event.is_set():
        return False
    return True

def check_server_online(server_data=None):
    if server_data is None:
        server_data = get_data_server_steam_api()

    try:
        if "response" in server_data and server_data["response"]:  # Проверяем, что "response" есть и он непустой
            return True
    except:
        return False

async def start_server():
      subprocess.Popen(f"start cmd /c {config["start_server"]}", shell=True)

async def update_server():
    updating_event.set() #флаг обновления
    update_process = await asyncio.create_subprocess_shell(config["update_server"])
    try:
        await asyncio.wait_for(update_process.wait(), config["start_waiting_time"]) 
        result = True
    except asyncio.TimeoutError:
        update_process.terminate()  # Принудительное завершение, если превышено время
        result = False
    updating_event.clear() #снимаем флаг обновления
    modify_config_game_version(get_current_game_version(get_data_game_steamcmd_api()))
    await start_server() 
    return result

async def stop_server():
    stop_process = await asyncio.create_subprocess_shell(config["stop_server"])
    try:
        await asyncio.wait_for(stop_process.wait(), config["stop_waiting_time"])
        return True
    except asyncio.TimeoutError:
        stop_process.terminate()  # Принудительное завершение, если превышено время
        return False

def get_server_players():
    try:
        return get_data_server_steam_api().get('response').get('servers')[0].get('players')
    except:
        return 0

# Создаём клавиатуру
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🚀Старт сервера"), #кнопки действий в один ряд
            KeyboardButton(text="⛔Стоп сервера"),
            KeyboardButton(text="🔄Обновление сервера")
        ],
        [KeyboardButton(text="👀Статус сервера")] #запрос статус отдельно
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    if message.chat.id not in WHITELIST:
        await send_message(f" Ваш Telegram 🆔: `{message.chat.id}`\n❌ У вас нет доступа к этому боту.", message)
        return
    await message.answer("✅ Добро пожаловать! Вы в белом списке.")
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message(lambda message: message.text == '🚀Старт сервера')
async def manual_server_startup(message: types.Message):
    if check_status_update():  
        if not check_server_online():
            await start_server()
        await send_message('Сервер запущен!', message)
        return
    await send_message('Сервер обновляется! Дождитесь обновления!', message)


@dp.message(lambda message: message.text == '⛔Стоп сервера')
async def manual_server_stop(message: types.Message):
    if check_server_online():
        await send_message('Сервер останавливается...', message)
        result = stop_server()
        if result == False:
            await send_message('❌Что-то пошло не так!', message)
            return
    await send_message('Сервер остановлен!', message)

@dp.message(lambda message: message.text == '🔄Обновление сервера')
async def manual_server_update(message: types.Message):
    if check_server_online():
        await send_message('Сервер запущен! Для обновления остановите сервер!', message)
        return
    if check_status_update() == False:
        await send_message('Сервер уже обновляется! Запуск нового обновления не требуется!', message)
        return
    await send_message('Сервер обновляется...', message)
    result = update_server()
    if result:
        await send_message('Сервер обновлен и запущен!', message)
        return
    await send_message('Что-то пошло не так. Возможно сервер еще обновляется.', message)    

@dp.message(lambda message: message.text == '👀Статус сервера')
async def get_server_status(message: types.Message):
    server_data = get_data_server_steam_api()
    if check_server_online(server_data):
        message_data = SimpleNamespace(**get_data_server_steam_api().get('response').get('servers')[0])
        await send_message(f'✅Сервер работает!\nНазвание сервера: {message_data.name}\nАдрес сервера: {message_data.addr}\nКоличество игроков: {message_data.players} / {message_data.max_players}', message)
    elif check_status_update() == False:
         await send_message('🔄 Сервер обновляется...', message)
    else:
        await send_message('❌Сервер упал!', message)

async def update_server_bg():
    while True:
        current_game_version = get_current_game_version(get_data_game_steamcmd_api())
        if get_server_game_version() != current_game_version and get_server_players() == 0:
            result_stop = await stop_server()
            if result_stop:
                print("Автоматичекий апдейт сервера")
                await update_server()
                print("Автоматичекий апдейт сервера завершен")              
        await asyncio.sleep(BG_WAITING_TIME)

async def main():
    asyncio.create_task(update_server_bg())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())