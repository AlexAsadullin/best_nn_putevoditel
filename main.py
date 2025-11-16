from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import declarative_base, sessionmaker
import asyncio
from datetime import date
import os

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
    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
    if not user:
        user = User(telegram_id=message.from_user.id, username=message.from_user.username)
        db.add(user)
        db.commit()
    db.close()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='направления', callback_data='directions')]
    ])
    photo = FSInputFile(WELCOME_PHOTO_PATH)
    await bot.send_photo(
        message.chat.id,
        photo=photo,
        caption='Welcome message!',
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data == 'directions')
async def directions_handler(callback: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # сюда доавблять новые города
        [InlineKeyboardButton(text='Павлово', callback_data='pavlovo')],
        [InlineKeyboardButton(text='Ичалки', callback_data='ichalki')],
        [InlineKeyboardButton(text='Болдино', callback_data='boldino')],
        [InlineKeyboardButton(text='Богородск', callback_data='bogorodsk')],
        [InlineKeyboardButton(text='Кстово', callback_data='kstovo')],
        [InlineKeyboardButton(text='Бор', callback_data='bor')],
        [InlineKeyboardButton(text='Арзамас', callback_data='arzamas')],
        [InlineKeyboardButton(text='Заволжье', callback_data='zavolzhye')],
    ])
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()

# сюда доавблять новые города
@dp.callback_query(lambda c: c.data in ['pavlovo', 'ichalki', 'boldino', 'bogorodsk', 'kstovo', 'bor', 'arzamas', 'zavolzhye'])
async def city_handler(callback: types.CallbackQuery):
    cities = {
        # сюда доавблять новые города
        'pavlovo': 'Павлово',
        'ichalki': 'Ичалки',
        'boldino': 'Болдино',
        'bogorodsk': 'Богородск',
        'kstovo': 'Кстово',
        'bor': 'Бор',
        'arzamas': 'Арзамас',
        'zavolzhye': 'Заволжье',
    }
    city = cities.get(callback.data, 'Город')
    text = f"go {city}"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='куда сходить', callback_data=f'{callback.data}_sights')],
        [InlineKeyboardButton(text='жилье', callback_data=f'{callback.data}_housing')],
        [InlineKeyboardButton(text='кафе', callback_data=f'{callback.data}_cafe')],
        [InlineKeyboardButton(text='как добраться', callback_data=f'{callback.data}_transport')]
    ])
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@dp.callback_query(lambda c: c.data.endswith(('_sights', '_housing', '_cafe', '_transport')))
async def content_handler(callback: types.CallbackQuery):
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
        [InlineKeyboardButton(text='Назад к направлению', callback_data=city)]
    ])
    await callback.message.edit_text(content, reply_markup=keyboard)
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
