import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from config import token
from sqlighter import SQLighter
from sqlighter1 import SQLighter1
import keyboards as kb
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

l = 0
l1 = 0

# задаем уровень логов
logging.basicConfig(level=logging.INFO)

# инициализируем бота
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# инициализируем соединение с Базой Данных
db_users = SQLighter('db_users.db')
db_bars = SQLighter1('db_bars.db')

message_from_user = ''
list_with_bar = []
list_with_bar1 = []


class PhoneNumber(StatesGroup):
    step_1 = State()


class Bar_Title(StatesGroup):
    step_2 = State()


class Bar_Metro(StatesGroup):
    step_3 = State()
    step_3_1 = State()


class Bar_Metro1(StatesGroup):
    step_3_2 = State()


class Cancel(StatesGroup):
    step_4 = State()


class Bar_Next(StatesGroup):
    step_5 = State()


class Users_bar(StatesGroup):
    step_6 = State()


class User_photo(StatesGroup):
    step_reg_photo = State()


class User_age(StatesGroup):
    step_reg_age = State()


class User_male(StatesGroup):
    step_reg_male = State()
    step_reg_male1 = State()


class Bar_buttons(StatesGroup):
    step_bar_button = State()


# начало бота
'''@dp.message_handler(commands=['start'])
async def starter(message: types.Message):
    await message.answer('Привет, пропиши /help для получения информации')
'''


@dp.message_handler(commands=['help'])
async def starter(message: types.Message):
    await message.answer('Пропиши /regphone для регистрации номера телефона')


# команда активации подписки
'''@dp.message_handler(commands=['subscribe'])
async def subscribe(message: types.Message):
    if not db_users.subscriber_exists(message.from_user.id):
        # если нет в базе, то добавим
        db_users.add_subscriber(message.from_user.id)
    else:
        # обновим базу
        db_users.update_subscription(message.from_user.id, True)
    await message.answer('Вы успешно подписались!')
'''

# команда отмены подписки
'''@dp.message_handler(commands=['unsubscribe'])
async def unsubscribe(message: types.Message):
    if not db_users.subscriber_exists(message.from_user.id):
        # если нет юзера в базе, добавим с неактивной подпиской (запомним)
        db_users.add_subscriber(message.from_user.id, False)
        await message.answer("Вы отписаны!")
    else:
        # если уже есть, то меняем статус подписки
        db_users.update_subscription(message.from_user.id, False)
        await message.answer("Вы успешно отписались!")
'''


# обработка кнопок при баре
@dp.callback_query_handler(state=Bar_Title.step_2)
async def callback_male(call: types.CallbackQuery):
    if '0' <= call.data[0] <= '9':
        if db_bars.get_reg_in_bar(call.data, db_users.get_username(call.from_user.id)) == -1:
            if db_users.users_bar(call.from_user.id)[2:-3] != "''" and db_users.users_bar(call.from_user.id)[
                                                                       2:-3] != "None":
                db_bars.update_bar_no_user(db_users.users_bar(call.from_user.id)[2:-3],
                                           db_bars.clear_user_in_bar(db_users.users_bar(call.from_user.id)[2:-3],
                                                                     db_users.get_username(call.from_user.id)))
                await call.answer('Вы идете в бар!\nЗапись в другой бар удалена')
            else:
                await call.answer('Вы идете в бар')
            db_bars.into_bar(call.data, bar_users=db_users.get_username(call.from_user.id) + ' ')
            db_users.update_regged_bar(call.from_user.id, call.data)
        else:
            await call.answer('Вы уже записаны')
            # print(str(db_bars.count_users(list_with_bar2[0]))[2:-2].split(','))


# запись пола
@dp.callback_query_handler(text="male")
async def callback_male(call: types.CallbackQuery):
    db_users.add_user_male(call.from_user.id, call.data)
    await call.message.answer('Еще чуть-чуть\nСколько вам лет?')
    await User_age.step_reg_age.set()


@dp.callback_query_handler(text="female")
async def callback_female(call: types.CallbackQuery):
    db_users.add_user_male(call.from_user.id, call.data)
    await call.message.answer('Еще чуть-чуть\nСколько вам лет?')
    await User_age.step_reg_age.set()


# запись возраста
@dp.message_handler(state=User_age.step_reg_age, content_types=types.ContentTypes.TEXT)
async def reg_age(message: types.Message, state: FSMContext):
    age = message.text
    t = True
    for i in range(len(age)):
        if not (age[i] >= '0' and age[i] <= '9'):
            t = False
    if not t:
        await message.answer('Отправьте корректный возраст')
        await state.finish()
        await User_age.step_reg_age.set()
    else:
        if int(age) < 18:
            await message.answer('Вы слишком юны!\nВведите возраст заново')
            await state.finish()
            await User_age.step_reg_age.set()
        elif int(age) > 60:
            await message.answer('В вашем возрасте бы пить чаёк\nВведите возраст заново')
            await state.finish()
            await User_age.step_reg_age.set()
        else:
            db_users.add_user_age(message.from_user.id, age)
            await message.answer('Осталось отправить фото')
            await User_photo.step_reg_photo.set()


# загрузка фото
@dp.message_handler(state=User_photo.step_reg_photo, content_types=types.ContentTypes.PHOTO)
async def reg_photo(message: types.Message, state: FSMContext):
    await state.finish()
    photo = message.photo[0].file_id
    # await bot.send_photo(message.chat.id, message.photo[0].file_id, caption=message.caption)
    db_users.add_user_photo(message.from_user.id, photo)
    await message.answer('Регистрация завершена!', reply_markup=kb.markup_requests1)
    await Cancel.step_4.set()


# команда регистрации пользователя
@dp.message_handler(commands=['start'])
async def registration(message: types.Message):
    if not db_users.subscriber_exists(message.from_user.id):
        # если не зарегистрирован
        db_users.add_subscriber(message.from_user.id, True, message.from_user.full_name, message.from_user.username,
                                '?')
    else:
        # обновляем, если нет телефона
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username,
                                         '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username,
                                         db_users.get_phone(message.from_user.id))
    await message.answer("Поехали, укажите пол", reply_markup=kb.markup_male)
    if str(message.from_user.username) == 'None':
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''), '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         db_users.get_phone(message.from_user.id))
    else:
        if db_users.get_phone(message.from_user.id) == '?':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, '?')
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, db_users.get_phone(message.from_user.id))


# начинаем запись телефона
@dp.message_handler(commands=['regphone'])
async def reg_phone(message: types.Message):
    await message.answer('Поделиться телефоном ☎', reply_markup=kb.markup_requests)
    await PhoneNumber.step_1.set()


# после присланного номера записываем
@dp.message_handler(state=PhoneNumber.step_1, content_types=types.ContentTypes.CONTACT)
async def get_phonenumber(message: types.Message, state: FSMContext):
    user_phone_number = message.contact.phone_number
    if not db_users.subscriber_exists(message.from_user.id):
        # если не зарегистрирован
        db_users.add_subscriber(message.from_user.id, True, message.from_user.full_name, message.from_user.username,
                                user_phone_number)
        if str(message.from_user.username) == 'None':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         user_phone_number)
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, user_phone_number)
    else:
        if str(message.from_user.username) == 'None':
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.full_name.replace(" ", ''),
                                         user_phone_number)
        else:
            db_users.update_subscription(message.from_user.id, True, message.from_user.full_name,
                                         message.from_user.username, user_phone_number)
    await message.answer('Телефон успешно зарегистрирован', reply_markup=kb.markup_requests1)
    await state.finish()
    await Cancel.step_4.set()


@dp.message_handler(state=PhoneNumber.step_1)
async def get_phonenumber1(message: types.Message, state: FSMContext):
    await message.answer('Телефон не отправлен!\nНу и ладно\nНачнем поиск баров!', reply_markup=kb.markup_requests1)
    await state.finish()
    await Cancel.step_4.set()


# поиск бара
@dp.message_handler(commands=['find_bar'])
async def registration(message: types.Message):
    await message.answer("Поиск баров", reply_markup=kb.markup_requests1)
    await Cancel.step_4.set()


# написана ерунда
@dp.message_handler(state=Cancel.step_4)
async def get_bars_from_title(message: types.Message, state: FSMContext):
    await state.finish()
    if message.text != 'Поиск бара по названию' and message.text != 'Отмена поиска' and message.text != 'Поиск бара по метро' and message.text != 'Куда записан пользователь':
        await message.answer('Ни одна кнопка не нажата', reply_markup=kb.ReplyKeyboardRemove())
    else:
        if message.text == 'Поиск бара по названию':
            await message.answer('Введи название бара', reply_markup=kb.ReplyKeyboardRemove())
            await Bar_Title.step_2.set()
        elif message.text == 'Поиск бара по метро':
            await message.answer('Введи станцию метро', reply_markup=kb.ReplyKeyboardRemove())
            await Bar_Metro.step_3.set()
        elif message.text == 'Куда записан пользователь':
            await message.answer('Введите хэндл', reply_markup=kb.ReplyKeyboardRemove())
            await Users_bar.step_6.set()
        elif message.text == 'Отмена поиска':
            await message.answer('Поиск отменен', reply_markup=kb.ReplyKeyboardRemove())


# поиск по пользователю
@dp.message_handler(state=Users_bar.step_6)
async def search_user_bar(message: types.Message, state: FSMContext):
    if message.text[0] == '@':
        username_to_find = message.text[1:]
    else:
        username_to_find = message.text
    t = db_users.users_bar_to_go(username_to_find)
    if t != 'no_user':
        if t != "''":
            bar = db_bars.bar_title_from_bar_id(t)
            bar = list(bar[0])
            if len(bar) != 0:
                bar2 = f"<b>{bar[0]}</b>\n\n" \
                       f"{bar[1]}\n\n" \
                       f"Метро: {bar[2]}\n\n" \
                       f"{bar[3]}\n"
                await message.answer(bar2, reply_markup=kb.markup_requests1)
        else:
            await message.answer('Пользователь никуда не записан', reply_markup=kb.markup_requests1)
    else:
        await message.answer('Пользователя не существует', reply_markup=kb.markup_requests1)
    await state.finish()
    await Cancel.step_4.set()


# поиск запущен по названию
@dp.message_handler(Text(equals='Отмена'), state=Bar_Title.step_2)
async def cancel_search_title(message: types.Message, state: FSMContext):
    global l1
    await message.answer('Поиск по названию отменен', reply_markup=kb.markup_requests1)
    l1 = 0
    await state.finish()
    await Cancel.step_4.set()


@dp.message_handler(Text(equals='Посмотреть записавшихся'), state=Bar_Title.step_2)
async def regged_users(message: types.Message, state: FSMContext):
    global l1
    list_with_bar3 = list(list_with_bar1[l1 - 1])
    if db_bars.who_is_in_bar(list_with_bar3[5]) != '':
        await message.answer(db_bars.who_is_in_bar(list_with_bar3[5]), reply_markup=kb.markup_bar)
    else:
        await message.answer('Записавшихся нет', reply_markup=kb.markup_bar)


'''
@dp.message_handler(Text(equals='Записаться в бар'), state=Bar_Title.step_2)
async def reg_in_bar_title(message: types.Message, state: FSMContext):
    global l1
    list_with_bar3 = list(list_with_bar1[l1 - 1])
    if db_bars.get_reg_in_bar(list_with_bar3[5], db_users.get_username(message.from_user.id)) == -1:
        if db_users.users_bar(message.from_user.id)[2:-3] != "''" and db_users.users_bar(message.from_user.id)[
                                                                      2:-3] != "None":
            db_bars.update_bar_no_user(db_users.users_bar(message.from_user.id)[2:-3],
                                       db_bars.clear_user_in_bar(db_users.users_bar(message.from_user.id)[2:-3],
                                                                 db_users.get_username(message.from_user.id)))
            await message.answer('Вы идете в бар\nЗаписи в другие бары удалены', reply_markup=kb.markup_bar)
        else:
            await message.answer('Вы идете в бар', reply_markup=kb.markup_bar)
        db_bars.into_bar(list_with_bar3[5], bar_users=db_users.get_username(message.from_user.id) + ' ')
        db_users.update_regged_bar(message.from_user.id, list_with_bar3[5])
    else:
        await message.answer('Вы уже записаны', reply_markup=kb.markup_bar)
        # print(str(db_bars.count_users(list_with_bar2[0]))[2:-2].split(','))
'''


@dp.message_handler(state=Bar_Title.step_2)
async def get_bars_from_title(message: types.Message, state: FSMContext):
    global list_with_bar1, l1
    if l1 == 0:
        list_with_bar1 = db_bars.get_bar_from_title(message.text)
        list_with_bar1 = list(list_with_bar1)
        if len(list_with_bar1) != 0:
            list_with_bar2 = list(list_with_bar1[l1])
            await message.answer(f"Всего баров найдено: {len(list_with_bar1)}", reply_markup=kb.markup_bar)
            bar = f"<b>{list_with_bar2[0]}</b>\n\n" \
                  f"{list_with_bar2[1]}\n\n" \
                  f"Метро: {list_with_bar2[2]}\n\n" \
                  f"{list_with_bar2[3]}\n"
            l1 += 1
            bar_id_keyboard = str(list_with_bar2[5])
            bar_users_keyboard = str(list_with_bar2[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = 'no_users'
            markup_bar = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard)).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar)
        else:
            await message.answer('Бар не найден')
            l1 = 0
            await state.finish()
    elif l1 >= 1 and message.text == 'Показать следующий бар':
        if l1 == len(list_with_bar1):
            await message.answer('Бары закончились', reply_markup=kb.ReplyKeyboardRemove())
            l1 = 0
            await state.finish()
        else:
            list_with_bar2 = list(list_with_bar1[l1])
            bar = f"<b>{list_with_bar2[0]}</b>\n\n" \
                  f"{list_with_bar2[1]}\n\n" \
                  f"Метро: {list_with_bar2[2]}\n\n" \
                  f"{list_with_bar2[3]}\n"
            l1 += 1
            bar_id_keyboard = str(list_with_bar2[5])
            bar_users_keyboard = str(list_with_bar2[4])
            if bar_users_keyboard == '':
                bar_users_keyboard = 'no_users'
            markup_bar = InlineKeyboardMarkup(resize_keyboard=True).add(
                InlineKeyboardButton("Записаться в бар", callback_data=bar_id_keyboard)).add(
                InlineKeyboardButton("Посмотреть записавшихся", callback_data=bar_users_keyboard))
            await message.answer(bar, reply_markup=markup_bar)
    else:
        await message.answer('Процедура поиска прервана', reply_markup=kb.ReplyKeyboardRemove())
        l1 = 0
        await state.finish()


# поиск запущен по метро
@dp.message_handler(Text(equals='Отмена'), state=Bar_Metro.step_3)
async def cancel_search(message: types.Message, state: FSMContext):
    global l
    await message.answer('Поиск по метро отменен', reply_markup=kb.markup_requests1)
    l = 0
    await state.finish()
    await Cancel.step_4.set()


@dp.message_handler(Text(equals='Посмотреть записавшихся'), state=Bar_Metro.step_3)
async def regged_users_m(message: types.Message, state: FSMContext):
    global l
    list_with_bar3 = list(list_with_bar[l - 1])
    if db_bars.who_is_in_bar(list_with_bar3[5]) != '':
        await message.answer(db_bars.who_is_in_bar(list_with_bar3[5]), reply_markup=kb.markup_bar)
    else:
        await message.answer('Записавшихся нет', reply_markup=kb.markup_bar)


@dp.message_handler(Text(equals='Записаться в бар'), state=Bar_Metro.step_3)
async def into_bar(message: types.Message, state: FSMContext):
    global l
    list_with_bar2 = list(list_with_bar[l - 1])
    if db_bars.get_reg_in_bar(list_with_bar2[5], db_users.get_username(message.from_user.id)) == -1:
        if db_users.users_bar(message.from_user.id)[2:-3] != 'None' and db_users.users_bar(message.from_user.id)[
                                                                        2:-3] != "''":
            db_bars.update_bar_no_user(db_users.users_bar(message.from_user.id)[2:-3],
                                       db_bars.clear_user_in_bar(db_users.users_bar(message.from_user.id)[2:-3],
                                                                 db_users.get_username(message.from_user.id)))
            await message.answer('Вы идете в бар\nЗаписи в другие бары удалена', reply_markup=kb.markup_bar)
        else:
            await message.answer('Вы идете в бар', reply_markup=kb.markup_bar)
        db_bars.into_bar(list_with_bar2[5], bar_users=db_users.get_username(message.from_user.id) + ' ')
        db_users.update_regged_bar(message.from_user.id, list_with_bar2[5])

    else:
        await message.answer('Вы уже записаны', reply_markup=kb.markup_bar)


# поиск запущен по метро
@dp.message_handler(state=Bar_Metro.step_3)
async def get_bars_from_metro(message: types.Message, state: FSMContext):
    global message_from_user, list_with_bar, l
    if l == 0:
        message_from_user = message.text
        list_with_bar = db_bars.get_bar_from_metro(message_from_user)
        list_with_bar = list(list_with_bar)
        if len(list_with_bar) != 0:
            list_with_bar1 = list(list_with_bar[l])
            await message.answer(f"Всего баров найдено: {len(list_with_bar)}")
            bar = f"<b>{list_with_bar1[0]}</b>\n\n" \
                  f"{list_with_bar1[1]}\n\n" \
                  f"Метро: {list_with_bar1[2]}\n\n" \
                  f"{list_with_bar1[3]}\n"
            l += 1
            await message.answer(bar, reply_markup=kb.markup_bar)
        else:
            await message.answer('Рядом баров нет')
            l = 0
            await state.finish()
    elif l >= 1 and message.text == 'Показать следующий бар':
        if l == len(list_with_bar):
            await message.answer('Бары закончились', reply_markup=kb.ReplyKeyboardRemove())
            l = 0
            await state.finish()
        else:
            list_with_bar1 = list(list_with_bar[l])
            bar = f"<b>{list_with_bar1[0]}</b>\n\n" \
                  f"{list_with_bar1[1]}\n\n" \
                  f"Метро: {list_with_bar1[2]}\n\n" \
                  f"{list_with_bar1[3]}\n"
            l += 1
            await message.answer(bar, reply_markup=kb.markup_bar)
    else:
        await message.answer('Процедура поиска прервана', reply_markup=kb.ReplyKeyboardRemove())
        l = 0
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
