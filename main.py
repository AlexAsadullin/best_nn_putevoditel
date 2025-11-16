from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import asyncio
from datetime import date
import os
from contextlib import contextmanager

API_TOKEN = '8013644792:AAH8NkeG-RFcqPhP3jkXNjLzjfpQH0oYc7Y'
WELCOME_PHOTO_PATH = os.path.join('data', 'welcome.png')
DB_URL = 'sqlite:///users.db'

engine = create_engine(DB_URL)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String)
    fio = Column(String)
    dob = Column(Date)


Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command('start'))
async def start_handler(message: types.Message):
    with get_db() as db:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            user = User(telegram_id=message.from_user.id, username=message.from_user.username)
            db.add(user)
            db.commit()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='О регионе', callback_data='about_region')],
        [InlineKeyboardButton(text='Нижний Новгород - локации', callback_data='nizniy')],
        [InlineKeyboardButton(text='Нижегородская Область - города', callback_data='directions')],
        [InlineKeyboardButton(text='Готовые маршруты', callback_data='ready_routes')],
    ])
    photo = FSInputFile(WELCOME_PHOTO_PATH)
    await bot.send_photo(
        message.chat.id,
        photo=photo,
        caption='Здравствуйте! Это бот-путеводитель по Нижегородской области, выберите направление:',
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data == 'main_menu')
async def main_menu_handler(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='О регионе', callback_data='about_region')],
        [InlineKeyboardButton(text='Нижний Новгород - локации', callback_data='nizniy')],
        [InlineKeyboardButton(text='Нижегородская Область - города', callback_data='directions')],
        [InlineKeyboardButton(text='Готовые маршруты', callback_data='ready_routes')],
    ])
    photo = FSInputFile(WELCOME_PHOTO_PATH)
    await bot.send_photo(
        callback.message.chat.id,
        photo=photo,
        caption='Здравствуйте! Это бот-путеводитель по Нижегородской области, выберите направление:',
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data == 'nizniy')
async def nizniy_handler(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Нижегородский Кремль', callback_data='nizhegorodskiy-kreml')],
        [InlineKeyboardButton(text='Чкаловская лестница', callback_data='chkalovskaya-lestnitsa')],
        [InlineKeyboardButton(text='Большая Покровская улица', callback_data='bolshaya-pokrovskaya-ulitsa')],
        [InlineKeyboardButton(text='Нижегородская ярмарка', callback_data='nizhegorodskaya-yarmarka')],
        [InlineKeyboardButton(text='Собор Александра Невского', callback_data='sobor-aleksandra-nevskogo')],
        [InlineKeyboardButton(text='Рождественская церковь', callback_data='rozhdestvenskaya-tserkov')],
        [InlineKeyboardButton(text='← Назад', callback_data='back_to_start')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id, "Выберите достопримечательность Нижнего Новгорода:",
                           reply_markup=keyboard)


@dp.callback_query(lambda c: c.data in ['nizhegorodskiy-kreml', 'chkalovskaya-lestnitsa', 'bolshaya-pokrovskaya-ulitsa',
                                        'nizhegorodskaya-yarmarka', 'sobor-aleksandra-nevskogo',
                                        'rozhdestvenskaya-tserkov'])
async def nn_dostoprim_handler(callback: types.CallbackQuery):
    await callback.answer()
    sights = {
        'nizhegorodskiy-kreml': 'Нижегородский Кремль',
        'chkalovskaya-lestnitsa': 'Чкаловская лестница',
        'bolshaya-pokrovskaya-ulitsa': 'Большая Покровская улица',
        'nizhegorodskaya-yarmarka': 'Нижегородская ярмарка',
        'sobor-aleksandra-nevskogo': 'Собор Александра Невского',
        'rozhdestvenskaya-tserkov': 'Рождественская церковь',
    }

    sight_name = callback.data
    file_path = os.path.join('data', 'Nizniy', f'{sight_name}.txt')

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"Информация о {sights.get(sight_name, sight_name)} временно недоступна."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='← Назад', callback_data='back_to_start')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id, content, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == 'directions')
async def directions_handler(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Павлово', callback_data='pavlovo')],
        [InlineKeyboardButton(text='Ичалки', callback_data='ichalki')],
        [InlineKeyboardButton(text='Болдино', callback_data='boldino')],
        [InlineKeyboardButton(text='Богородск', callback_data='bogorodsk')],
        [InlineKeyboardButton(text='Кстово', callback_data='kstovo')],
        [InlineKeyboardButton(text='Бор', callback_data='bor')],
        [InlineKeyboardButton(text='Арзамас', callback_data='arzamas')],
        [InlineKeyboardButton(text='Заволжье', callback_data='zavolzhye')],
        [InlineKeyboardButton(text='Гродец', callback_data='grodets')],
        [InlineKeyboardButton(text='Лысково', callback_data='lyskovo')],
        [InlineKeyboardButton(text='Семенов', callback_data='semenov')],
        [InlineKeyboardButton(text='Дивеево', callback_data='diveevo')],
        [InlineKeyboardButton(text='Острово-Вознесенское', callback_data='ostrovo-voznesenskoe')],
        [InlineKeyboardButton(text='Озеро Светлояр', callback_data='ozero-svetloyar')],
        [InlineKeyboardButton(text='Горьковское море', callback_data='gorkovskoe-more')],
        [InlineKeyboardButton(text='Дзержинск', callback_data='dzerzhinsk')],
        [InlineKeyboardButton(text='Чкаловск', callback_data='chkalovsk')],
        [InlineKeyboardButton(text='Сергач', callback_data='sergach')],
        [InlineKeyboardButton(text='Медвежий угол (Балахна)', callback_data='medvezhiy-ugol-balahna')],
        [InlineKeyboardButton(text='Балахна', callback_data='balahna')],
        [InlineKeyboardButton(text='Пешеланский гипсовый карьер', callback_data='peshelanskiy-gipsovyy-karer')],
        [InlineKeyboardButton(text='Станция Железнодорожная (Петрякша)',
                              callback_data='stantsiya-zheleznodorozhnaya-petryaksha')],
        [InlineKeyboardButton(text='Васильсурск', callback_data='vasilsursk')],
        [InlineKeyboardButton(text='Лукоянов', callback_data='lukoyanov')],
        [InlineKeyboardButton(text='← Назад', callback_data='back_to_start')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id, "Выберите направление в Нижегородской области:",
                           reply_markup=keyboard)


@dp.callback_query(lambda c: c.data == 'back_to_start')
async def back_to_start_handler(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='О регионе', callback_data='about_region')],
        [InlineKeyboardButton(text='Нижний Новгород - локации', callback_data='nizniy')],
        [InlineKeyboardButton(text='Нижегородская Область - города', callback_data='directions')],
        [InlineKeyboardButton(text='Готовые маршруты', callback_data='ready_routes')],
    ])
    photo = FSInputFile(WELCOME_PHOTO_PATH)
    await bot.send_photo(
        callback.message.chat.id,
        photo=photo,
        caption='Здравствуйте! Это бот-путеводитель по Нижегородской области, выберите направление:',
        reply_markup=keyboard
    )


@dp.callback_query(lambda c: c.data == 'about_region')
async def about_region_handler(callback: types.CallbackQuery):
    await callback.answer()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='← Назад', callback_data='back_to_start')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id,
                           "Приветствуем вас в Нижнем Новгороде — городе с тысячелетней историей на слиянии Волги и Оки, где жили и творили великие нижегородцы: Козьма Минин, герой ополчения 1612 года; Максим Горький, классик литературы; Андрей Сахаров, нобелевский лауреат и правозащитник; Валерий Чкалов, легендарный лётчик.\nНижегородская область — сердце Волжского федерального округа в центре европейской России (площадь 76,6 тыс. км², население 3,04 млн чел. на 2025 г., 80% городского). География: умеренный континентальный климат, 48% лесов, 41% сельхозугодий, ресурсы — песок с титаном-цирконием, глина, гипс, торф, соль, древесина. Экономика: 7-е место по промышленному производству (машиностроение, химия, нефтехимия, деревообработка — 83% ВРП). Культура: православие (69%), древние монастыри (Серафимо-Дивеевский), ярмарки, кремль ЮНЕСКО.\nПогрузитесь в интерактивное путешествие: от кремлёвских стен до волжских просторов!",
                           reply_markup=keyboard)


@dp.callback_query(
    lambda c: c.data in ['pavlovo', 'ichalki', 'boldino', 'bogorodsk', 'kstovo', 'bor', 'arzamas', 'zavolzhye',
                         'grodets', 'lyskovo', 'semenov', 'diveevo', 'ostrovo-voznesenskoe', 'ozero-svetloyar',
                         'gorkovskoe-more', 'dzerzhinsk', 'chkalovsk', 'sergach', 'medvezhiy-ugol-balahna', 'balahna',
                         'peshelanskiy-gipsovyy-karer', 'stantsiya-zheleznodorozhnaya-petryaksha', 'vasilsursk',
                         'lukoyanov'])
async def city_handler(callback: types.CallbackQuery):
    await callback.answer()
    cities = {
        'pavlovo': 'Павлово',
        'ichalki': 'Ичалки',
        'boldino': 'Болдино',
        'bogorodsk': 'Богородск',
        'kstovo': 'Кстово',
        'bor': 'Бор',
        'arzamas': 'Арзамас',
        'zavolzhye': 'Заволжье',
        'grodets': 'Гродец',
        'lyskovo': 'Лысково',
        'semenov': 'Семенов',
        'diveevo': 'Дивеево',
        'ostrovo-voznesenskoe': 'Острово-Вознесенское',
        'ozero-svetloyar': 'Озеро Светлояр',
        'gorkovskoe-more': 'Горьковское море',
        'dzerzhinsk': 'Дзержинск',
        'chkalovsk': 'Чкаловск',
        'sergach': 'Сергач',
        'medvezhiy-ugol-balahna': 'Медвежий угол (Балахна)',
        'balahna': 'Балахна',
        'peshelanskiy-gipsovyy-karer': 'Пешеланский гипсовый карьер',
        'stantsiya-zheleznodorozhnaya-petryaksha': 'Станция Железнодорожная (Петрякша)',
        'vasilsursk': 'Васильсурск',
        'lukoyanov': 'Лукоянов',
    }
    city = cities.get(callback.data, 'Город')
    text = f"Город: {city}, что вас интересует?"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='куда сходить', callback_data=f'{callback.data}_sights')],
        [InlineKeyboardButton(text='жилье', callback_data=f'{callback.data}_housing')],
        [InlineKeyboardButton(text='кафе', callback_data=f'{callback.data}_cafe')],
        [InlineKeyboardButton(text='как добраться', callback_data=f'{callback.data}_transport')],
        [InlineKeyboardButton(text='← Назад', callback_data='directions')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id, text, reply_markup=keyboard)


@dp.callback_query(lambda c: c.data.endswith(('_sights', '_housing', '_cafe', '_transport')))
async def content_handler(callback: types.CallbackQuery):
    await callback.answer()
    parts = callback.data.rsplit('_', 1)
    city = parts[0]
    suffix = parts[1]
    suffix_to_file = {
        'sights': 'sights.txt',
        'housing': 'housing.txt',
        'cafe': 'cafe.txt',
        'transport': 'transport.txt'
    }
    filename = suffix_to_file.get(suffix, 'unknown.txt')
    file_path = os.path.join('data', city, filename)

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = f"Файл {filename} не найден для {city}."

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='← Назад', callback_data='directions')],
        [InlineKeyboardButton(text='🏠 Главное меню', callback_data='main_menu')]
    ])
    await bot.send_message(callback.message.chat.id, content, reply_markup=keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
