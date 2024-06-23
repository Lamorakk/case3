import logging
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram import Router, Bot, Dispatcher, F

router = Router()

# Define bot and dispatcher here if necessary or import from main bot file
bot = Bot.get_current()
dp = Dispatcher.get_current()

# Create a keyboard for company information
def create_company_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Company Info", callback_data="company_info")],
        [InlineKeyboardButton(text="Our Mission", callback_data="our_mission")],
        [InlineKeyboardButton(text="Our Team", callback_data="our_team")],
        [InlineKeyboardButton(text="Contact Us", callback_data="contact_us")]
    ])

# Handler to display the company keyboard
@router.message(F.text == "Company")
async def show_company_menu(message: types.Message):
    keyboard = create_company_keyboard()
    await message.answer("Choose an option:", reply_markup=keyboard)

# Handler for company info
@router.callback_query(F.data == "company_info")
async def company_info(callback_query: types.CallbackQuery):
    photo = InputFile("media/photo1.jpg")
    text = "Here is some information about our company."
    await bot.send_photo(callback_query.from_user.id, photo, caption=text)

# Handler for our mission
@router.callback_query(F.data == "our_mission")
async def our_mission(callback_query: types.CallbackQuery):
    photo = InputFile("media/photo2.jpg")
    text = "Our mission is to provide the best services to our customers."
    await bot.send_photo(callback_query.from_user.id, photo, caption=text)

# Handler for our team
@router.callback_query(F.data == "our_team")
async def our_team(callback_query: types.CallbackQuery):
    photo = InputFile("media/photo3.jpg")
    text = "Meet our dedicated team."
    await bot.send_photo(callback_query.from_user.id, photo, caption=text)

# Handler for contact us
@router.callback_query(F.data == "contact_us")
async def contact_us(callback_query: types.CallbackQuery):
    photo = InputFile("media/photo4.jpg")
    text = "You can contact us at contact@company.com."
    await bot.send_photo(callback_query.from_user.id, photo, caption=text)
