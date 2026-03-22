from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import settings


def get_payment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="⭐️ Telegram Stars", callback_data="pay_stars"),
        InlineKeyboardButton(text="💎 CryptoBot", callback_data="pay_crypto")
    )
    return builder.as_markup()