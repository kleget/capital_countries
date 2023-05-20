from importt import *
import logging
from db_manage import *
from base_words import *
from data_words import base2

api = TOKEN
logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

#выводим приветсвие, правила, особенности
#проверяем. если пользователь есть в бд, то ладно, если нет, то добавляем его
@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    await start(message)

async def start(message):
    await bot.send_message(message.chat.id, md.text("Привет ✌, это бот, который поможет тебе выучить все столицы всех стран мира! 🌏\nДля быстрого ввода комманд воспользуйся синей кнопкой menu слева от поля ввода."))
    with sq.connect('data_base.db') as con:
        sql = con.cursor()
        sql.execute(f"SELECT user_id FROM users WHERE user_id == {str(message.chat.id)}")
        if sql.fetchone() is None:
            sql.execute("INSERT INTO users (user_id, user_link, first_name, full_name, statpm) VALUES (?, ?, ?, ?, ?)", (message.chat.id, message.chat.mention, message.chat.first_name, message.chat.full_name, ''))
    await game_f(message.chat.id)

@dp.message_handler(commands="help")
async def help_command(message: types.Message):
    await message.answer("Если вы столкнулись с с проблемой ⚙ в боте, или у вас есть вопросы или предложения, то вы можете связаться с создателем бота написав ему в личные сообщения в телеграме. 👨‍💻 https://t.me/kleget")

@dp.message_handler(commands="info")
async def help_command(message: types.Message):
    await message.answer("Выбери уровень кнопкой с ниизу, затем также выбери карту.\nПосле бот дает на выбор 4 столицы, 1 из которых верная.\nИграй и учи столицы стран!")
    await game_f(message.chat.id)

#по /game выводим кнопки с выбором уровня
# @dp.message_handler(commands='game')
# async def levels_button(message: types.Message):
#     await game_f(message.chat.id)

async def game_f(id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # хз, наверное параметры кнопок
    markup.row("уровень 1", "уровень 2", "уровень 3").add("уровень 4", "уровень 5", "уровень 6")  # добавляем кнопки
    await bot.send_message(id, "Выбери уровень.\nЧем выше уровень, тем сложнее! 💪", reply_markup=markup)


#обрабатываем нажатые кнопки
@dp.message_handler()
async def filter_msg(message: types.Message):
    if message.text in ["уровень 1", "уровень 2", "уровень 3", "уровень 4", "уровень 5", "уровень 6"]:
        await db_update('уровень', message.chat.id, message.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # хз, наверное параметры кнопок
        markup.add('билет 1', 'билет 2', 'билет 3', 'билет 4', 'билет 5', 'билет 6', 'билет 7', 'билет 8', '<- назад')  # добавляем кнопки
        await bot.send_message(message.chat.id, 'Выбери билет.\nЧем выше номер билета, там сложнее. 💪', reply_markup=markup)

    elif message.text in ['билет 1', 'билет 2', 'билет 3', 'билет 4', 'билет 5', 'билет 6', 'билет 7', 'билет 8', '<- назад']:
        statpm = ''
        await db_update('statpm', message.chat.id, statpm)
        if message.text == '<- назад':
            await game_f(message.chat.id)
        else:
            await db_update('билет', message.chat.id, message.text)
            # markup = types.ReplyKeyboardRemove()
            await bot.send_message(
                message.chat.id,
                md.text("Игра началась!"),
                # reply_markup=markup,  # удаляем кнопки
                # parse_mode=ParseMode.MARKDOWN,  # хз
            )
            await start_1(message)
            await button_answer(message)


async def start_1(message):
    lvl = await db_select('уровень', message.chat.id)
    crd = await db_select('билет', message.chat.id)
    tbword = str(lvl[0] + crd[0]).replace(' ', '')
    await db_update('fbw', message.chat.id, tbword)
    await db_update('indx', message.chat.id, 0)

async def button_answer(message):
    fbw = await db_select('fbw', message.chat.id)
    indx = await db_select('indx', message.chat.id)
    fbwz = globals()[fbw[0]]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)  # хз, наверное параметры кнопок
    arr = [base2[random.randint(0, 100)].split('$')[1], base2[random.randint(101, 170)].split('$')[1], base2[random.randint(171, 255)].split('$')[1], fbwz[int(indx[0])].split('$')[1]]
    arr.sort()
    markup.row(arr[0], arr[1]).add(arr[2], arr[3])
    await bot.send_message(message.chat.id, text=f"Столица страны {fbwz[int(indx[0])].split('$')[0]} - это ", reply_markup=markup)
    arr.clear()
    await answer.stolica.set()


class answer(StatesGroup):                                                             #создаем класс и передаем параметр StatesGroup(хз что это)
    stolica = State()

@dp.message_handler(state=answer.stolica)
async def play(message: types.Message, state: FSMContext):
    await bot.send_message('-1001806040146', f"{message.chat.mention}, {message.text}")
    fbw = await db_select('fbw', message.chat.id)
    indx = await db_select('indx', message.chat.id)
    fbwz = globals()[fbw[0]]

    await state.update_data(stolica=message.text)  # вызываем метод update_data(), который сохраняет данные в память
    data = await state.get_data()
    statpm = await db_select("statpm", message.chat.id)
    statpm = statpm[0]
    if data['stolica'] == fbwz[int(indx[0])].split('$')[1]:
        statpm += '+'
        await db_update('statpm', message.chat.id, statpm)
        await bot.send_message(message.chat.id, f"✅ Правильно, столица страны {fbwz[int(indx[0])].split('$')[0]} - это {fbwz[int(indx[0])].split('$')[1]}.")
        await state.finish()  # Данный метод очищает все состояния пользователя, а также удаляет все ранее сохраненные данные. Если же вам надо сбросить только состояние, воспользуйтесь: await state.reset_state(with_data=False)
        if int(indx[0]) == 0 or int(indx[0]) < len(fbwz)-1:
            await db_update('indx', message.chat.id, int(indx[0]) + 1)
            await button_answer(message)
        else:
            await db_update('indx', message.chat.id, 0)
            # markup = types.ReplyKeyboardRemove()
            statpm = await db_select("statpm", message.chat.id)
            ar = await stats_hendler(statpm[0])
            await bot.send_message(
                message.chat.id,
                md.text(f"Молодец, ты ответил на все вопросы!\n{ar}"),
                # reply_markup=markup,  # удаляем кнопки
                # parse_mode=ParseMode.MARKDOWN,  # хз
            )
            await game_f(message.chat.id)

    elif data['stolica'] == '/game':
        # markup = types.ReplyKeyboardRemove()
        await bot.send_message(
            message.chat.id,
            md.text(f"Пока-пока! 👋"),
            # reply_markup=markup,  # удаляем кнопки
            # parse_mode=ParseMode.MARKDOWN,  # хз
        )
        await state.finish()
        await game_f(message.chat.id)

    elif data['stolica'] == '/start':
        # markup = types.ReplyKeyboardRemove()
        await bot.send_message(
            message.chat.id,
            md.text(f"Пока-пока! 👋"),
            # reply_markup=markup,  # удаляем кнопки
            # parse_mode=ParseMode.MARKDOWN,  # хз
        )
        await state.finish()
        await start(message)

    else:
        statpm += '-'
        await db_update('statpm', message.chat.id, statpm)
        await bot.send_message(message.chat.id, f"❌ Не правильно, столица страны {fbwz[int(indx[0])].split('$')[0]} - это {fbwz[int(indx[0])].split('$')[1]}.")
        await state.finish()  # Данный метод очищает все состояния пользователя, а также удаляет все ранее сохраненные данные. Если же вам надо сбросить только состояние, воспользуйтесь: await state.reset_state(with_data=False)
        if int(indx[0]) == 0 or int(indx[0]) < len(fbwz)-1:
            await db_update('indx', message.chat.id, int(indx[0]) + 1)
            await button_answer(message)
        else:
            await db_update('indx', message.chat.id, 0)
            # markup = types.ReplyKeyboardRemove()
            statpm = await db_select("statpm", message.chat.id)
            ar = await stats_hendler(statpm[0])
            await bot.send_message(
                message.chat.id,
                md.text(f"Молодец, ты ответил на все вопросы!\n{ar}"),
                # reply_markup=markup,  # удаляем кнопки
                # parse_mode=ParseMode.MARKDOWN,  # хз
            )
            await game_f(message.chat.id)

async def stats_hendler(statss):
    statss = statss.replace('+', '✅')
    statss = statss.replace('-', '❌')
    return statss

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
