import random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from aiogram import types
from aiogram.dispatcher import FSMContext
from asgiref.sync import sync_to_async

from .config import bot, EMAIL_ADDRESS, EMAIL_PASSWORD, dp
from .dev_mode_tools import is_developer_mode_enabled
from .forms import Form
from .models import RegisteredUser


@sync_to_async
def is_user_registered(user_id):
    return RegisteredUser.objects.filter(user_id=user_id, email_confirmed=True).exists()


@dp.message_handler(state=Form.email)
async def process_email_registration(message: types.Message, state: FSMContext):
    email = message.text.lower()
    # if re.match(r".+@(contractor\.gazprom-neft\.ru|gazprom-neft\.ru)$", email):
    confirmation_code = random.randint(100000, 999999)
    await send_confirmation_email(email, confirmation_code)

    try:
        await sync_to_async(RegisteredUser.objects.update_or_create)(
            user_id=message.chat.id,
            defaults={
                'email': email,
                'email_confirmed': False,  # Начинаем с False, подтверждение будет позже
                'developer_mode': False   # Стандартное значение при регистрации
            }
        )
        await state.update_data(confirmation_code=confirmation_code)
        await Form.confirmation_code.set()
        await message.reply("Мы отправили код подтверждения на вашу почту. \nВведите его здесь:")
    except Exception as e:
        if await is_developer_mode_enabled(message.chat.id):
            await bot.send_message(message.chat.id, f"Error: {str(e)}")
        else:
            print(f"Error: {str(e)}")
        await message.reply("Произошла ошибка при регистрации.")
    # else:
    #     await message.reply("Пожалуйста, введите корректный адрес почты!")

async def send_confirmation_email(email: str, code: int) -> None:
    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = 'Код подтверждения регистрации'

    body = f"""
    <html>
        <head></head>
        <body>
            <p>Добрый день!</p>
            <p>Вас приветствует команда ЛУПА, которая создала AI-помощника для врачей💉💊️</p>
            <p>Ваш код подтверждения для регистрации в нашем боте <a href="https://t.me/sirius_medicine_bot">t.me/sirius_medicine_bot</a>:</p>
            <p><strong style="font-size: 16px; color: #347AB7;">{code}</strong></p>
        </body>
    </html>
    """
    msg.attach(MIMEText(body, 'html'))

    try:
        smtp = aiosmtplib.SMTP(hostname='smtp.gmail.com', port=465, use_tls=True)
        await smtp.connect()
        await smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        await smtp.send_message(msg)
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
    finally:
        await smtp.quit()


@dp.message_handler(state=Form.confirmation_code)
async def confirm_email_registration(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    expected_code = user_data['confirmation_code']
    entered_code = message.text

    if str(expected_code) == entered_code:
        try:
            user = await sync_to_async(RegisteredUser.objects.get)(user_id=message.chat.id)
            user.email_confirmed = True
            await sync_to_async(user.save)()

            await message.answer("Вы успешно зарегистрированы и подтвердили свою почту.\n"
                                 "Добро пожаловать! Теперь Вам доступно:\n"
                                 "- 1\n"
                                 "- 2\n"
                                 "- 3")
        except RegisteredUser.DoesNotExist:
            await message.reply("Пользователь не найден.")
        except Exception as e:
            if await is_developer_mode_enabled(message.chat.id):
                await bot.send_message(message.chat.id, f"Error: {str(e)}")
            else:
                print(f"Error: {str(e)}")
            await message.reply("Произошла ошибка при подтверждении почты.")
        finally:
            await state.finish()
    else:
        await message.reply("Код подтверждения неверен. Пожалуйста, попробуйте еще раз или запросите новый код.")
