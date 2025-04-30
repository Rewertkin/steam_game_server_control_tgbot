"""Реализация телеграмм бота для управления игровым сервером STEAM"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from config_loader import config, api_keys
import steam_ds_server as sdss
import docker_server as docker_game
import api_client

bot = Bot(token=api_keys.bot_api)
dp = Dispatcher()

async def send_message(text, message):
    """Отправить сообщение"""
    await message.answer(text)
    print(f'{message.chat.id} = {text}')

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
    """Приветственное сообщение"""
    if message.chat.id not in WHITELIST:
        await send_message(f''' Ваш Telegram 🆔: `{message.chat.id}`
                           \n❌ У вас нет доступа к этому боту.''', message)
        return
    await message.answer("✅ Добро пожаловать! Вы в белом списке.")
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message(lambda message: message.text == '🚀Старт сервера')
async def manual_server_startup(message: types.Message):
    """Ручной запуск сервера"""
    if config.server_type == "steam_dc":
        await send_message(await sdss.manual_start_server(), message)
    if config.server_type == "docker":
        await send_message(docker_game.manual_start_server(), message)

@dp.message(lambda message: message.text == '⛔Стоп сервера')
async def manual_server_stop(message: types.Message):
    """Ручная остановка сервера"""
    if api_client.check_server_online():
        await send_message('Сервер останавливается...', message)
        if config.server_type == "steam_dc":    
            await send_message(await sdss.manual_server_stop(), message)
        if config.server_type == "docker":
            await send_message(docker_game.manual_server_stop(), message)
    else:
        await send_message('Сервер остановлен!', message)

@dp.message(lambda message: message.text == '🔄Обновление сервера')
async def manual_server_update(message: types.Message):
    """Ручное обновление сервера"""
    if api_client.check_server_online():
        await send_message('Сервер запущен! Для обновления остановите сервер!', message)
        return
    
    if config.server_type == "steam_dc": 
        if sdss.check_status_update() is False:
            await send_message('Сервер уже обновляется! Запуск нового обновления не требуется!', message)
            return
        await send_message('Сервер обновляется...', message)
        await send_message(await sdss.manual_server_update(), message)
    
    if config.server_type == "docker":
        docker_game.manual_server_update()

@dp.message(lambda message: message.text == '👀Статус сервера')
async def get_server_status(message: types.Message):
    """Получить статус сервера"""
    server_data = api_client.get_data_server_steam_api()
    if api_client.check_server_online(server_data):
        message_data = api_client.get_data_for_message()
        await send_message(f"✅Сервер работает!\nНазвание сервера: {message_data.name}\nАдрес сервера: {message_data.addr}\nКоличество игроков: {message_data.players}/{message_data.max_players}",
                           message)
    elif sdss.check_status_update() is False:
        await send_message('🔄 Сервер обновляется...', message)
    else:
        await send_message('❌Сервер упал!', message)

async def main():
    """Функция для запуска"""
    if config.server_type == "steam_dc":
        asyncio.create_task(sdss.update_server_bg())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
