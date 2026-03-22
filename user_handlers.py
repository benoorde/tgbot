import logging
from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (CallbackQuery, LabeledPrice, Message,
                           PreCheckoutQuery, SuccessfulPayment, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton)

from config import settings
from inline_keyboards import get_payment_keyboard
from crypto_bot import create_crypto_bot_invoice, get_crypto_bot_invoice

router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start. Приветствует пользователя и предлагает варианты оплаты.
    """
    photo = FSInputFile("start.jpg")
    text = (
        "🚀 **Добро пожаловать в Traders Metod!** 🚀\n\n"
        "Вы в одном шаге от того, чтобы изменить свой подход к трейдингу. Наш канал — это не просто сигналы, это <b>полноценная база знаний и гайдов</b>, которая поможет вам принимать взвешенные решения на рынке.\n\n"
        "📈 **Что внутри?**\n"
        "• Эксклюзивные торговые стратегии.\n"
        "• Подробные гайды для новичков и опытных трейдеров.\n"
        "• Аналитика рынка от профессионалов.\n"
        "• Доступ в закрытое комьюнити единомышленников.\n\n"
        "Готовы начать свой путь к успешному трейдингу? Оплатите доступ и присоединяйтесь к нам! 👇\n\n"
        f"Стоимость: <b>{settings.PRICE_STARS} Telegram Stars</b> или "
        f"<b>{settings.PRICE_USDT} USDT</b>."
    )
    await message.answer_photo(
        photo=photo,
        caption=text,
        reply_markup=get_payment_keyboard()
    )


@router.callback_query(F.data == "pay_crypto")
async def process_crypto_payment(callback: CallbackQuery):
    """
    Создает и отправляет счет для оплаты через CryptoBot.
    """
    await callback.answer("Создаем счет в CryptoBot...")
    try:
        invoice = await create_crypto_bot_invoice(amount=settings.PRICE_USDT)
        if invoice:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔗 Оплатить", url=invoice.bot_invoice_url)],
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_crypto_{invoice.invoice_id}")]
            ])
            await callback.message.answer(
                f"Ваш счет на оплату {settings.PRICE_USDT} USDT создан.\n"
                f"Нажмите кнопку ниже после оплаты.",
                reply_markup=keyboard
            )
        else:
            await callback.message.answer("Не удалось создать счет. Попробуйте позже.")
    except Exception as e:
        logging.error(f"Ошибка CryptoBot: {e}")
        await callback.message.answer("Ошибка платежной системы. Пожалуйста, попробуйте позже или свяжитесь с поддержкой.")


@router.callback_query(F.data.startswith("check_crypto_"))
async def check_crypto_payment_handler(callback: CallbackQuery, bot: Bot):
    """
    Проверяет статус оплаты счета CryptoBot.
    """
    invoice_id = int(callback.data.split("_")[-1])
    await callback.answer("Проверяем оплату...")

    try:
        invoice = await get_crypto_bot_invoice(invoice_id)
        if invoice and invoice.status == "paid":
            await callback.message.edit_text("✅ Оплата подтверждена!")
            await send_channel_link(bot, callback.from_user.id, callback.message)
        elif invoice:
            await callback.answer(
                f"Счет еще не оплачен. Статус: {invoice.status}\n"
                "Если вы только что оплатили, подождите пару минут и нажмите кнопку снова.",
                show_alert=True
            )
        else:
            await callback.answer("Счет не найден.", show_alert=True)
    except Exception as e:
        logging.error(f"Ошибка при проверке счета: {e}")
        await callback.answer("Ошибка при проверке. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data == "pay_stars")
async def process_stars_payment(callback: CallbackQuery, bot: Bot):
    """
    Создает и отправляет счет для оплаты через Telegram Stars.
    """
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Подписка на канал",
        description="Единоразовая оплата за доступ к эксклюзивному контенту.",
        payload=f"subscribe_payload_{callback.from_user.id}",
        provider_token="",  # Для Stars токен не нужен
        currency="XTR",
        prices=[LabeledPrice(label="Подписка", amount=settings.PRICE_STARS)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_query_handler(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    """
    Подтверждает готовность к обработке платежа (для Stars).
    """
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message, bot: Bot):
    """
    Обрабатывает успешную оплату и выдает ссылку на канал.
    """
    logging.info(f"Successful payment: {message.successful_payment.model_dump_json(indent=4)}")
    await message.answer("Оплата прошла успешно!")
    await send_channel_link(bot, message.from_user.id, message)


async def send_channel_link(bot: Bot, user_id: int, message: Message):
    """
    Вспомогательная функция: создает ссылку и отправляет её пользователю.
    """
    expire_date = datetime.now() + timedelta(days=1) # Ссылка живет 24 часа от текущего момента
    invite_link = await bot.create_chat_invite_link(
        chat_id=settings.PRIVATE_CHANNEL_ID,
        expire_date=expire_date,
        member_limit=1
    )
    await message.answer(
        "Спасибо за покупку! Вот ваша одноразовая ссылка для входа в канал:\n"
        f"{invite_link.invite_link}\n\n"
        "<b>Внимание:</b> Ссылка действительна 24 часа и только для одного вступления."
    )