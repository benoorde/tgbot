import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import settings
import user_handlers


async def main() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем роутеры
    dp.include_router(user_handlers.router)

    # Если указан URL вебхука, запускаем в режиме Webhook
    if settings.BASE_WEBHOOK_URL:
        # Устанавливаем вебхук на адрес Cloudflare Worker или вашего домена
        webhook_url = f"{settings.BASE_WEBHOOK_URL}/webhook"
        await bot.set_webhook(webhook_url, drop_pending_updates=True)

        # Настройка aiohttp приложения
        app = web.Application()
        
        # Обработчик запросов
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        # Регистрируем обработчик на путь /webhook
        webhook_requests_handler.register(app, path="/webhook")
        
        setup_application(app, dp, bot=bot)
        
        # Запуск веб-сервера
        runner = web.AppRunner(app)
        await runner.setup()
        # Используем порт от платформы (PORT), если он есть, иначе из конфига
        port = settings.PORT or settings.WEB_SERVER_PORT
        site = web.TCPSite(runner, host=settings.WEB_SERVER_HOST, port=port)
        await site.start()
        
        logging.info(f"Webhook running on {settings.WEB_SERVER_HOST}:{port}")
        logging.info(f"Webhook URL set to: {webhook_url}")
        
        # Бесконечный цикл, чтобы приложение не закрылось (так как мы не используем web.run_app внутри asyncio.run)
        await asyncio.Event().wait()
        
    else:
        # Иначе запускаем Polling (для локальной разработки)
        await bot.delete_webhook(drop_pending_updates=True)
        logging.info("Starting polling...")
        await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
