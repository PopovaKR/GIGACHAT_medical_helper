from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async

from .config import dp
from .forms import Form
from .models import RegisteredUser


@dp.message_handler(state=Form.developer_mode)
async def set_developer_mode(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        await update_developer_mode(message.chat.id, True)
        await message.reply("Режим разработчика включен. Теперь вы будете видет текст ошибок, если они возникнут.")
    else:
        await update_developer_mode(message.chat.id, False)
        await message.reply("Режим разработчика выключен.")
    await state.finish()


@sync_to_async
def get_developer_mode_status(user_id):
    try:
        user = RegisteredUser.objects.get(user_id=user_id)
        return user.developer_mode
    except RegisteredUser.DoesNotExist:
        return False


async def is_developer_mode_enabled(user_id):
    return await get_developer_mode_status(user_id)


@sync_to_async
def update_developer_mode(user_id, mode):
    try:
        user = RegisteredUser.objects.get(user_id=user_id)
        user.developer_mode = mode
        user.save()
    except RegisteredUser.DoesNotExist:
        print(f"Не найден пользователь с id: {user_id}")
