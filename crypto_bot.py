from aiocryptopay import AioCryptoPay, Networks

from config import settings


async def create_crypto_bot_invoice(amount: float):
    """
    Создает счет на оплату через CryptoBot.
    """
    cryptopay = AioCryptoPay(token=settings.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    try:
        invoice = await cryptopay.create_invoice(
            asset="USDT", amount=amount, allow_anonymous=False
        )
        return invoice
    finally:
        await cryptopay.close()


async def get_crypto_bot_invoice(invoice_id: int):
    """
    Получает информацию о счете по его ID.
    """
    cryptopay = AioCryptoPay(token=settings.CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    try:
        invoices = await cryptopay.get_invoices(invoice_ids=[invoice_id])
        return invoices[0] if invoices else None
    finally:
        await cryptopay.close()