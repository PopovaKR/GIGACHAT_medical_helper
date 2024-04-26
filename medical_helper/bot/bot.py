import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.chat_models.gigachat import GigaChat
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import CharacterTextSplitter
from aiogram import types

from .auth import is_user_registered
from .dev_mode_tools import is_developer_mode_enabled
from .forms import Form
from .utils import remove_ws, format_docs, load_multiple
from .config import GIGACHAT_TOKEN, bot, dp, scenario_texts

storage = MemoryStorage()
chat = GigaChat(credentials=GIGACHAT_TOKEN, scope='GIGACHAT_API_CORP', verify_ssl_certs=False, profanity_check=False)


file_paths = [
    '/medical_helper/web/data/klinical_recomendation.pdf',
    '/medical_helper/web/data/klinical_recomendation_measles.pdf',
    '/medical_helper/web/data/klinical_recomendation_scarlet.pdf',
]


# file_paths = [
    # '/Users/maksimpugacev/PycharmProjects/django-on-docker/medical_helper/data/klinical_recomendation.pdf',
    # '/Users/maksimpugacev/PycharmProjects/django-on-docker/medical_helper/data/klinical_recomendation_measles.pdf',
    # '/Users/maksimpugacev/PycharmProjects/django-on-docker/medical_helper/data/klinical_recomendation_scarlet.pdf',
# ]

pages_py = load_multiple(file_paths)

text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=2000,
    chunk_overlap=150,
    length_function=len
)

docs = text_splitter.split_documents(pages_py)

docs = [remove_ws(d) for d in docs]

vectors = Chroma.from_documents(
    documents=docs,
    embedding=HuggingFaceEmbeddings(
        model_name='intfloat/multilingual-e5-base',
    ),
)


retriever = vectors.as_retriever()
template = """
Ты вежливый опытный бот врач, отвечай на все медицинские вопросы.
Используйте следующую информацию для ответа на вопрос пользователя.
Если вы не знаете ответ, скажите об этом, не пытайтесь придумать ответ.

Контекст: {context}
Вопрос: {question}

Возвращайте только полезный ответ ниже и ничего больше
"""


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer(
        "Привет! Я бот c искусственным интелелктом.\n"
        "Я призван помогать врачам ставить первичные диагнозы и вырабатываться стратегии лечения!\n"
        "Используйте команду /registration для регистрации, если вы врач 👨‍💊💉️"
    )


@dp.message_handler(commands=['script'])
async def choose_scenario(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton('1'), types.KeyboardButton('2'), types.KeyboardButton('3'),
               types.KeyboardButton('4'), types.KeyboardButton('5'))
    await message.answer(
        "Выберите один из сценариев:\n"
        "Сценарий 1: Определение диагноза по известным симптомам.\n"
        "Сценарий 2: Определение симптомов при известном диагнозе.\n"
        "Сценарий 3: Определение лечения при известном диагнозе.\n"
        "Сценарий 4: Консультация-совет по сдаче анализов для подтверждения диагноза.\n"
        "Сценарий 5: Общая медицинская информация.\n",
        reply_markup=markup
    )
    await Form.scenario.set()


@dp.message_handler(commands=['registration'])
async def request_email(message: types.Message):
    await Form.email.set()
    await message.reply("Введите вашу почту:")


@dp.message_handler(commands=['check_mode'])
async def check_developer_mode(message: types.Message):
    dev_mode_enabled = await is_developer_mode_enabled(message.from_user.id)
    # await message.answer(f"Режим разработчика {'включен' if dev_mode_enabled else 'выключен'}.")
    return 'включен' if dev_mode_enabled else 'выключен'


@dp.message_handler(commands=['mode'], state='*')
async def toggle_developer_mode(message: types.Message, state: FSMContext):
    if not await is_user_registered(message.chat.id):
        await message.reply("Эта фича доступна только зарегистрированным пользователям")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.row(types.KeyboardButton('Да'), types.KeyboardButton('Нет'))
    await Form.developer_mode.set()
    await message.answer(
        "Хотите включить режим разработчика?\n"
             "Это Вам позволит видеть текст ошибок если они возникнут, а также ссылки на источники ответа💡\n"
             f"Текущий статус: {await check_developer_mode(message)}",
        reply_markup=markup,
    )


@dp.message_handler()
async def answer_question(message: types.Message):
    user_question = message.text
    await find_closest_match(user_question, message.chat.id)


async def find_closest_match(user_question: str, chat_id: int):
    qa_prompt = PromptTemplate(template=template, input_variables=['context', 'question'])
    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | qa_prompt
            | chat
            | StrOutputParser()
    )
    response = rag_chain.invoke(user_question)
    await bot.send_message(chat_id, response)


@dp.message_handler(state=Form.scenario)
async def set_scenario(message: types.Message, state: FSMContext):
    global template

    selected_scenario = message.text
    if selected_scenario in scenario_texts:
        template = scenario_texts[selected_scenario][0]
        await message.answer(scenario_texts[selected_scenario][1])
        await state.finish()
    else:
        await message.reply("Выберите правильный сценарий, используя кнопки.")


if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
